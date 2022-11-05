#!/usr/bin/env python
import json
import unittest.mock
from typing import *

from lummao import Vector, Quaternion, Key

from . import serialize_list, deserialize_list, BaseMessagingTestCase, LinkMessage

from pythonized import interpreter
from constants import *
from assembler import Assembler, Label, types_to_str


class InterpreterTests(BaseMessagingTestCase):
    script: interpreter.Script

    async def asyncSetUp(self):
        self.script = interpreter.Script()
        await super().asyncSetUp()
        # intentionally don't run state_entry(),
        # that's only used by the in-world script.
        self.script.event_queue.clear()

    async def _load_assembly(self, opcodes, at: int = 0):
        assembler = Assembler()
        assembled = assembler.assemble(opcodes)
        assembled_str = json.dumps(assembled, separators=(',', ':'))
        self.script.gCode = json.loads(assembled_str)
        # set IPB and recalculate IP
        await self.script.handleCodeReload(at)

    async def _call_into(self, *args):
        serialized_args = await serialize_list(args)
        message = LinkMessage(IPCType.INVOKE_HANDLER, serialized_args, Key(str(0)))
        self.script.queue_event("link_message", message)
        await self.script.execute()

    def _take_yielded(self) -> List[Any]:
        yielded = []
        for _ in range(self.script.gYielded - 1):
            yielded.append(self.script.gStack.pop(-1))
        return yielded

    async def _run_until_yield(self):
        await self.script.interpreterLoop()
        self.assertTrue(self.script.gYielded)

    async def assertYields(self, values: List[Any], execute: bool = True):
        if execute:
            await self._run_until_yield()
        self.assertSequenceEqual(values, self._take_yielded())

    async def assertYieldsList(self, values: List[Any], execute: bool = True):
        if execute:
            await self._run_until_yield()
        yielded = self._take_yielded()
        self.assertEqual(1, len(yielded))
        self.assertSequenceEqual(values, await deserialize_list(yielded[0]))

    async def test_chained_expressions(self):
        await self._load_assembly([
            # Push can push from a constant relative to IP, local reference or global.
            # They use the same instruction to reduce dispatch code overhead.
            # Could refer to a constant pool at the start of the bank.
            # Literals can live in the bytecode, they get cast before getting
            # put on the stack according to the type operand of PUSH
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 2],
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, "8"],
            # We can also explicitly cast things
            [OpCode.CAST, LSLType.STRING, LSLType.INTEGER],
            [OpCode.BIN_OP, Operation.PLUS, LSLType.INTEGER, LSLType.INTEGER],
            # Duplicate the result on top of the stack so that we can use it after the YIELD
            [OpCode.DUP],
            # Yield to the interpreter, they MUST pop the stack after.
            [OpCode.YIELD, 1],

            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, -3],
            [OpCode.BIN_OP, Operation.MINUS, LSLType.INTEGER, LSLType.INTEGER],
            [OpCode.DUP],
            [OpCode.YIELD, 1],

            [OpCode.CAST, LSLType.INTEGER, LSLType.FLOAT],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 2.0],
            [OpCode.BIN_OP, Operation.PLUS, LSLType.FLOAT, LSLType.FLOAT],
            [OpCode.YIELD, 1],
        ])

        # Execute until the script engine yields
        await self.assertYields([10])
        await self.assertYields([-13])
        await self.assertYields([-11.0])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_vector_constant(self):
        await self._load_assembly([
            # Vector constants can't survive the JSONification of bytecode,
            # they get cast when pushed from a constant. Storing as 3 separate
            # floats would be possible too, but that's more expensive because LSL
            # Note that we can omit decimals and closing ">" to reduce size.
            [OpCode.PUSH, LSLType.VECTOR, Whence.CONST, 0, "<1,2,3"],
            [OpCode.YIELD, 1],
        ])
        await self.assertYields([Vector((1.0, 2.0, 3.0))])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_locals(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.LOCAL, types_to_str((LSLType.FLOAT,))],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 2.0],
            [OpCode.STORE, LSLType.FLOAT, Whence.LOCAL, 0],
            # You can push from locals as well, this pushes a float
            # that was already on the stack, in the locals relative to
            # the base pointer register.
            [OpCode.PUSH, LSLType.FLOAT, Whence.LOCAL, 0],
            [OpCode.YIELD, 1],
        ])
        await self.assertYields([2.0])
        # The local should still be on the stack
        self.assertSequenceEqual([2.0], self.script.gStack)
        # Base pointer should be 0, locals are at the bottom.
        self.assertEqual(0, self.script.gBP)

    async def test_globals(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.GLOBAL, types_to_str((LSLType.FLOAT,))],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 2.0],
            [OpCode.STORE, LSLType.FLOAT, Whence.GLOBAL, 0],
            # You can push from locals as well, this pushes a float
            # that was already on the stack, in the locals relative to
            # the base pointer register.
            [OpCode.PUSH, LSLType.FLOAT, Whence.GLOBAL, 0],
            [OpCode.YIELD, 1],
        ])
        await self.assertYields([2.0])
        # Nothing should be on the stack
        self.assertSequenceEqual([], self.script.gStack)
        # The global should still be present
        self.assertSequenceEqual([2.0], self.script.gGlobals)
        # Base pointer should be 0
        self.assertEqual(0, self.script.gBP)

    async def test_alloc_all_types(self):
        all_types = (LSLType.INTEGER, LSLType.FLOAT, LSLType.STRING, LSLType.KEY,
                     LSLType.VECTOR, LSLType.ROTATION, LSLType.LIST)
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.GLOBAL, types_to_str(all_types)],
            [OpCode.ALLOC_SLOTS, Whence.LOCAL, types_to_str(all_types)],
        ])
        await self.script.interpreterLoop()
        expected_locals = [0, 0.0, "", Key(""), Vector((0.0, 0.0, 0.0)), Quaternion((0.0, 0.0, 0.0, 0.0)), "[]"]
        self.assertSequenceEqual(expected_locals, self.script.gStack)
        # Global initialization is slightly different with regard to quaternions
        expected_globals = [0, 0.0, "", Key(""), Vector((0.0, 0.0, 0.0)), Quaternion((0.0, 0.0, 0.0, 1.0)), "[]"]
        self.assertSequenceEqual(expected_globals, self.script.gGlobals)

    async def test_loops_and_locals(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.LOCAL, types_to_str((LSLType.INTEGER, LSLType.FLOAT, LSLType.STRING))],

            # Looping, whoo!
            Label("StartLoop"),

            # This section is effectively `for (i; i<10; i += 1) {}`
            [OpCode.PUSH, LSLType.INTEGER, Whence.LOCAL, 0],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 10],
            [OpCode.BIN_OP, Operation.GREATER, LSLType.INTEGER, LSLType.INTEGER],
            [OpCode.JUMP, JumpType.NIF, Label("EndLoop")],

            # Add one to the local
            [OpCode.PUSH, LSLType.INTEGER, Whence.LOCAL, 0],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 1],
            [OpCode.BIN_OP, Operation.PLUS, LSLType.INTEGER, LSLType.INTEGER],
            [OpCode.STORE, LSLType.INTEGER, Whence.LOCAL, 0],

            # Jump back to the start
            [OpCode.JUMP, JumpType.ALWAYS, Label("StartLoop")],
            Label("EndLoop"),

            [OpCode.PUSH, LSLType.INTEGER, Whence.LOCAL, 0],
            [OpCode.YIELD, 1],
        ])
        await self.assertYields([10])
        # the locals should still be on the stack
        self.assertSequenceEqual([10, 0.0, ''], self.script.gStack)

    async def test_code_continuation(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.LOCAL, types_to_str((LSLType.INTEGER,))],

            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 20],
            [OpCode.STORE, LSLType.INTEGER, Whence.LOCAL, 0],
        ])
        # Run until we hit the end of the code we have on hand
        await self.script.interpreterLoop()
        self.assertTrue(self.script.gCodeFetchNeeded)

        # Pretend we loaded a new chunk continuing where the code left off
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.LOCAL, 0],
            [OpCode.YIELD, 1],
        ], at=5)
        await self.assertYields([20])
        # the locals should still be on the stack
        self.assertSequenceEqual([20], self.script.gStack)

    async def test_code_continuation_ipc(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.LOCAL, types_to_str((LSLType.INTEGER,))],

            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 20],
            [OpCode.STORE, LSLType.INTEGER, Whence.LOCAL, 0],
        ])
        # Run until we hit the end of the code we have on hand
        await self.script.interpreterLoop()
        self.assertTrue(self.script.gCodeFetchNeeded)

        # Should have requested a new code chunk along with the current absolute IP
        expected_sent = [LinkMessage(IPCType.REQUEST_CODE, "", Key("5"))]
        self.assertSequenceEqual(expected_sent, self.sent_messages)

        # Pretend we loaded a new chunk continuing where the code left off
        assembler = Assembler()
        code = assembler.assemble([
            [OpCode.PUSH, LSLType.INTEGER, Whence.LOCAL, 0],
            [OpCode.YIELD, 1],
        ])
        self.script.queue_event("link_message", LinkMessage(IPCType.REQUEST_CODE_REPLY, json.dumps(code), Key("5")))
        await self.script.execute()
        await self.assertYields([20], execute=False)
        # the locals should still be on the stack
        self.assertSequenceEqual([20], self.script.gStack)

    async def test_ret(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.LOCAL, types_to_str((LSLType.INTEGER,))],
            [OpCode.RET, 0],
        ])
        await self.script.interpreterLoop()
        # Should not exit the loop with an "out of bounds execution attempt"
        # error, we're legitimately finished
        self.assertFalse(self.script.gCodeFetchNeeded)
        # Should signal we're yielding control back to the embedder
        self.assertEqual(1, self.script.gYielded)
        # No locals should be left on the stack
        self.assertSequenceEqual([], self.script.gStack)

    async def test_call(self):
        await self._load_assembly([
            # _start is actually implicit, used for bootstrapping
            # globals and such.
            Label("_start"),
            # Not a parameter for simpleFunc, just need to be sure
            # this doesn't get blown away by RET shrinking the stack
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 2],
            [OpCode.CALL, 0, Label("simpleFunc")],
            # Yield 1 stack val to the interpreter
            [OpCode.YIELD, 1],
            [OpCode.RET, 0],

            Label("simpleFunc"),
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 1],
            [OpCode.YIELD, 1],
            [OpCode.RET, 0],
        ])
        await self.assertYields([1])
        self.assertFalse(self.script.gCodeFetchNeeded)

        # Should return and yield
        await self.assertYields([2])

        await self.script.interpreterLoop()

        self.assertFalse(self.script.gCodeFetchNeeded)
        # Should signal we're yielding control back to the embedder
        self.assertEqual(1, self.script.gYielded)
        # No locals should be left on the stack
        self.assertSequenceEqual([], self.script.gStack)

    async def test_call_arg(self):
        await self._load_assembly([
            Label("_start"),
            # A parameter for simpleFunc
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 50],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 2],
            [OpCode.CALL, 0, Label("simpleFunc")],
            [OpCode.YIELD, 0],
            # Need to pop off the args after we return, RET argument
            # tells how many args to pop after the registers are restored.
            [OpCode.RET, 2],

            Label("simpleFunc"),
            [OpCode.PUSH, LSLType.INTEGER, Whence.ARG, 0],
            [OpCode.PUSH, LSLType.INTEGER, Whence.ARG, 1],
            [OpCode.BIN_OP, Operation.DIV, LSLType.INTEGER, LSLType.INTEGER],
            [OpCode.YIELD, 1],
            [OpCode.RET, 0],
        ])
        await self.assertYields([25])
        self.assertFalse(self.script.gCodeFetchNeeded)
        self.assertSequenceEqual([50, 2, 5, 0, 0], self.script.gStack)
        await self.assertYields([])
        self.assertSequenceEqual([50, 2], self.script.gStack)
        await self.script.interpreterLoop()
        self.assertSequenceEqual([], self.script.gStack)

    async def test_short_constant_pushes(self):
        # TODO: May or may not remove these. not sure. They're 32bits smaller
        # each in memory once loaded, but the JSONified bytecode is usually
        # 1 byte (2 bytes UCS-2 because mono?) longer.
        await self._load_assembly([
            # 0
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 1],
            # -1
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 1 | (-1 << 1)],
            # 0.0
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 1],
        ])
        await self.script.interpreterLoop()
        self.assertSequenceEqual([0, -1, 0.0], self.script.gStack)

    async def test_ret_with_value(self):
        await self._load_assembly([
            Label("_start"),
            # Push an empty for the retval
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 0],
            # Parameters for simpleFunc
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 50],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 2],
            [OpCode.CALL, 0, Label("simpleFunc")],
            [OpCode.YIELD, 1],
            [OpCode.RET, 0],

            Label("simpleFunc"),
            [OpCode.PUSH, LSLType.INTEGER, Whence.ARG, 0],  # 2
            [OpCode.PUSH, LSLType.INTEGER, Whence.ARG, 1],  # 50
            [OpCode.BIN_OP, Operation.DIV, LSLType.INTEGER, LSLType.INTEGER],
            # slot above the last arg is the retval
            [OpCode.STORE, LSLType.INTEGER, Whence.ARG, 2],
            [OpCode.RET, 2],
        ])
        await self.assertYields([25])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_top_level_args(self):
        # Test an externally invoked hook with args
        await self._load_assembly([
            Label("HookWithTwoArgs"),
            [OpCode.PUSH, LSLType.INTEGER, Whence.ARG, 0],
            [OpCode.PUSH, LSLType.INTEGER, Whence.ARG, 1],
            [OpCode.BIN_OP, Operation.DIV, LSLType.INTEGER, LSLType.INTEGER],
            # slot above the last arg is the retval
            [OpCode.STORE, LSLType.INTEGER, Whence.ARG, 2],
            [OpCode.RET, 2],
        ])
        await self._call_into(1, 2)
        self.assertSequenceEqual([], self.script.gStack)
        self.assertTrue(self.script.gYielded)
        self.assertFalse(self.script.gCodeFetchNeeded)

    async def test_top_level_ret(self):
        # Test an externally invoked hook with a retval
        await self._load_assembly([
            Label("HookWithARet"),
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 2],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 50],
            [OpCode.BIN_OP, Operation.DIV, LSLType.INTEGER, LSLType.INTEGER],
            # slot above the last arg is the retval
            [OpCode.STORE, LSLType.INTEGER, Whence.ARG, 0],
            [OpCode.RET, 0],
        ])
        # Make space for the retval
        self.script.gStack = [0]
        await self._call_into()
        self.assertSequenceEqual([25], self.script.gStack)
        self.assertTrue(self.script.gYielded)
        self.assertFalse(self.script.gCodeFetchNeeded)

    async def test_accessor_replace(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 4],
            [OpCode.PUSH, LSLType.VECTOR, Whence.CONST, 0, "<1,2,3"],
            [OpCode.REPLACE_MEMBER, LSLType.VECTOR, CoordAccessor.Y],

            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 5],
            [OpCode.PUSH, LSLType.ROTATION, Whence.CONST, 0, "<1,2,3,4"],
            [OpCode.REPLACE_MEMBER, LSLType.ROTATION, CoordAccessor.S],
            [OpCode.YIELD, 2],
        ])
        await self.assertYields([Quaternion((1.0, 2.0, 3.0, 5.0)), Vector((1.0, 4.0, 3.0))])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_accessor_get(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.VECTOR, Whence.CONST, 0, "<1,2,3"],
            [OpCode.TAKE_MEMBER, LSLType.VECTOR, CoordAccessor.Y],
            [OpCode.PUSH, LSLType.ROTATION, Whence.CONST, 0, "<1,2,3,4"],
            [OpCode.TAKE_MEMBER, LSLType.ROTATION, CoordAccessor.Y],
            [OpCode.YIELD, 2],
        ])
        await self.assertYields([2.0, 2.0])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_build_coord(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 0.0],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 1.0],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 2.0],
            [OpCode.BUILD_COORD, LSLType.VECTOR],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 0.0],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 1.0],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 2.0],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 3.0],
            [OpCode.BUILD_COORD, LSLType.ROTATION],
            [OpCode.YIELD, 2],
        ])
        await self.assertYields([
            Quaternion((0.0, 1.0, 2.0, 3.0)),
            Vector((0.0, 1.0, 2.0)),
        ])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_un_op(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 1],
            [OpCode.UN_OP, Operation.MINUS, LSLType.INTEGER],
            [OpCode.YIELD, 1],
        ])
        await self.assertYields([-1])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_swap_op(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 1],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 2],
            [OpCode.SWAP],
        ])
        await self.script.interpreterLoop()
        self.assertSequenceEqual([2, 1], self.script.gStack)

    async def test_bool_op(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 99],
            [OpCode.BOOL, LSLType.INTEGER],
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, ""],
            [OpCode.BOOL, LSLType.STRING],
            [OpCode.YIELD, 2]
        ])
        await self.assertYields([0, 1])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_pop_n_op(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 99],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 98],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 97],
            [OpCode.POP_N, 2],
        ])
        await self.script.interpreterLoop()
        self.assertSequenceEqual([99], self.script.gStack)

    async def test_alloc_slots(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.LOCAL, types_to_str((
                LSLType.INTEGER,
                LSLType.FLOAT,
                LSLType.STRING,
                LSLType.KEY,
                LSLType.VECTOR,
                LSLType.ROTATION,
                LSLType.LIST,
            ))],
        ])
        await self.script.interpreterLoop()
        expected_def = [0, 0.0, "", Key(""), Vector((0.0, 0.0, 0.0)), Quaternion((0.0, 0.0, 0.0, 0.0)), "[]"]
        self.assertSequenceEqual(expected_def, self.script.gStack)

    async def test_build_list(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 99],
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, "foo"],
            [OpCode.BUILD_LIST, 2],
            [OpCode.YIELD, 1],
        ])
        await self.assertYieldsList([99, "foo"])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_list_list_bin_op(self):
        await self._load_assembly([
            [OpCode.BUILD_LIST, 0],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 99],
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, "foo"],
            [OpCode.BUILD_LIST, 2],
            [OpCode.BIN_OP, Operation.NEQ, LSLType.LIST, LSLType.LIST],
            [OpCode.YIELD, 1],
        ])
        await self.assertYields([2])

    async def test_list_append(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, "bar"],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 99],
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, "foo"],
            [OpCode.BUILD_LIST, 2],
            [OpCode.BIN_OP, Operation.PLUS, LSLType.LIST, LSLType.STRING],
            [OpCode.YIELD, 1],
        ])
        await self.assertYieldsList([99, "foo", "bar"])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_list_prepend(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 99],
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, "foo"],
            [OpCode.BUILD_LIST, 2],
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, "bar"],
            [OpCode.BIN_OP, Operation.PLUS, LSLType.STRING, LSLType.LIST],
            [OpCode.YIELD, 1],
        ])
        await self.assertYieldsList(["bar", 99, "foo"])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_cast_to_list(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 99],
            [OpCode.PUSH, LSLType.STRING, Whence.CONST, 0, "foo"],
            [OpCode.BUILD_LIST, 2],
            [OpCode.CAST, LSLType.LIST, LSLType.STRING],
            [OpCode.YIELD, 1],
        ])
        await self.assertYields(["99foo"])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_cast_from_list(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 99],
            [OpCode.CAST, LSLType.INTEGER, LSLType.LIST],
            [OpCode.YIELD, 1],
        ])
        await self.assertYieldsList([99])
        self.assertSequenceEqual([], self.script.gStack)

    async def test_library_call(self):
        await self._load_assembly([
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 1.0],
            [OpCode.CALL_LIB, 1, "llFrand"],
            # We expect that the retval will be on the stack at this point, yield it.
            [OpCode.YIELD, 1],
        ])
        await self.assertYields([])
        payload = await serialize_list([1.0])
        str_lib_num = str(LIBRARY_FUNCS["llFrand"].num)
        # Check that the call request was sent correctly
        self.assertSequenceEqual([LinkMessage(IPCType.CALL_LIB, payload, str_lib_num)], self.sent_messages)

        # Mimic a response from a library script
        resp_payload = await serialize_list([2.0])
        ret_type = str(int(LibFuncRet.SIMPLE))
        self.script.queue_event("link_message", LinkMessage(IPCType.CALL_LIB_REPLY, resp_payload, ret_type))
        await self.script.execute()
        await self.assertYields([2.0], execute=False)
        self.assertSequenceEqual([], self.script.gStack)

    async def test_library_call_no_wait(self):
        await self._load_assembly([
            # Use this as a sentinel to mean llSleep hasn't completed yet
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 1],
            [OpCode.PUSH, LSLType.FLOAT, Whence.CONST, 0, 1.0],
            # Call to llSleep() with no wait.
            [OpCode.CALL_LIB, 1, "llSleep", 1],
            # Pop the stack sentinel
            [OpCode.POP_N, 1],
        ])
        await self.script.execute()
        # Everything should have been completed inside a single interpreterLoop()
        # Meaning the stack sentinel should already be popped
        self.assertSequenceEqual([], self.script.gStack)

    async def test_code_fetch_on_load_message(self):
        self.script.gCode.clear()
        self.script.queue_event("link_message", LinkMessage(IPCType.INVOKE_HANDLER, "", Key("0")))
        await self.script.execute()
        self.assertTrue(self.script.gCodeFetchNeeded)

        # Should have requested a new code chunk along with the current absolute IP
        expected_sent = [LinkMessage(IPCType.REQUEST_CODE, "", Key("0"))]
        self.assertSequenceEqual(expected_sent, self.sent_messages)

        # Pretend we loaded a new chunk continuing where the code left off
        assembler = Assembler()
        code = assembler.assemble([
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 20],
            [OpCode.YIELD, 1],
            [OpCode.RET],
        ])
        self.script.queue_event("link_message", LinkMessage(IPCType.REQUEST_CODE_REPLY, json.dumps(code), Key("0")))
        await self.script.execute()
        await self.assertYields([20], execute=False)
        await self.script.interpreterLoop()
        self.assertSequenceEqual([], self.script.gStack)

    async def test_manager_notified_handler_done(self):
        # Test an externally invoked hook with args
        await self._load_assembly([
            Label("HookWithNoArgs"),
            # Yield so we can make sure we always have gInvokingHandler
            # set mid-call
            [OpCode.YIELD, 0],
            [OpCode.RET, 0],
        ])
        await self._call_into()
        self.assertEqual(1, self.script.gYielded)
        self.assertTrue(self.script.gInvokingHandler)
        self.script.gYielded = 0
        await self.script.interpreterLoop()
        self.assertSequenceEqual([], self.script.gStack)
        expected_messages = [
            LinkMessage(IPCType.HANDLER_FINISHED, "", Key(""))
        ]
        self.assertEqual(expected_messages, self.sent_messages)
        self.assertFalse(self.script.gInvokingHandler)

    async def test_unsolicited_call_lib_reply(self):
        resp_payload = await serialize_list([2.0])
        ret_type = str(int(LibFuncRet.SIMPLE))
        self.script.builtin_funcs['llOwnerSay'] = lambda arg: None
        self.script.interpreterLoop = unittest.mock.MagicMock()
        self.script.queue_event("link_message", LinkMessage(IPCType.CALL_LIB_REPLY, resp_payload, ret_type))
        await self.script.execute()
        self.script.interpreterLoop.assert_not_called()

    async def test_change_state(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.GLOBAL, types_to_str((LSLType.FLOAT,))],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 20],
            [OpCode.CALL, 0, Label("FuncWithNoArgs")],
            Label("FuncWithNoArgs"),
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 20],
            [OpCode.CHANGE_STATE, 1],
        ])
        await self.assertYields([])
        # Stack should have fully unwound
        self.assertSequenceEqual([], self.script.gStack)
        self.assertFalse(self.script.gInvokingHandler)
        self.assertEqual(0, self.script.gBP)
        # Globals should still be there though
        self.assertSequenceEqual([0.0], self.script.gGlobals)
        expected_messages = [
            LinkMessage(IPCType.CHANGE_STATE, "", Key("1"))
        ]
        self.assertEqual(expected_messages, self.sent_messages)

    async def test_reset_vm_state(self):
        await self._load_assembly([
            [OpCode.ALLOC_SLOTS, Whence.GLOBAL, types_to_str((LSLType.FLOAT,))],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 20],
            [OpCode.CALL, 0, Label("FuncWithNoArgs")],
            Label("FuncWithNoArgs"),
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 20],
            [OpCode.YIELD, 0]
        ])
        await self.assertYields([])
        self.script.queue_event("link_message", LinkMessage(IPCType.SCRIPT_LOADED, "", Key("")))
        await self.script.execute()
        self.assertFalse(self.script.gInvokingHandler)
        self.assertEqual(0, self.script.gYielded)
        self.assertSequenceEqual([], self.script.gGlobals)
        self.assertSequenceEqual([], self.script.gStack)


if __name__ == "__main__":
    unittest.main()
