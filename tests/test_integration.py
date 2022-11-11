"""
Run the library, manager and interpreter scripts together.

These tests are somewhat slow due to the state fixups lslopt
needs to constantly do to ensure that results of operations match
what LSL would do.
"""

import asyncio
import pathlib
import unittest
from typing import Sequence, Callable, Union, List
from unittest.mock import Mock

from lummao import BaseLSLScript, convert_script_to_ir

from assembler import Assembler, types_to_str
from constants import *
from ir2asm import IRConverter
from pythonized import interpreter, library, manager

from . import MockNotecardHandler, MockNotecard, LinkMessage

BASE_PATH = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_PATH = BASE_PATH / "test_resources"


class LinkMessagePropagator:
    """Passes outbound link messages to all other scripts in the set"""
    def __init__(self, scripts: Sequence[BaseLSLScript]):
        self.scripts = scripts
        self.sent_messages: List[LinkMessage] = []

    def patch_scripts(self):
        for script in self.scripts:
            script.builtin_funcs['llMessageLinked'] = self._make_message_sender(script)

    def _make_message_sender(self, script: BaseLSLScript) -> Callable:
        """Make a version of llMessageLinked that will queue link_messages on other scripts"""
        def _send_message(link_num, num, string, key):
            for other_script in self.scripts:
                # Scripts can hear their own link_messages, so don't bypass sending
                # the event to the sending script!
                other_script.queue_event("link_message", (link_num, num, string, key))
            self.sent_messages.append(LinkMessage(num, string, key))
        return _send_message


class IntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.interp_script = interpreter.Script()
        self.manager_script = manager.Script()
        self.library_script = library.Script()
        self.scripts = [self.interp_script, self.manager_script, self.library_script]

        for script in self.scripts:
            self._patch_builtins(script)

        self.message_propagator = LinkMessagePropagator(self.scripts)
        self.message_propagator.patch_scripts()
        self.notecard = MockNotecard("script", "")
        self.notecard_handler = MockNotecardHandler(self.manager_script, [self.notecard])
        self.notecard_handler.patch_script()

    def _patch_builtins(self, script: BaseLSLScript):
        base_builtins = script.builtin_funcs
        base_builtins['llOwnerSay'] = print
        base_builtins['llSay'] = lambda _chan, msg: print(msg)
        # Our state is already clean, we don't need to restart.
        base_builtins['llResetScript'] = lambda: None
        base_builtins['llSetText'] = lambda *args: None
        base_builtins['llResetTime'] = lambda: None
        base_builtins['llGetTime'] = lambda: 0.0

    def _script_to_asm(self, contents: Union[str, bytes]):
        converter = IRConverter(convert_script_to_ir(contents))
        assembler = Assembler()
        assembler.assemble(converter.convert())
        return assembler

    async def execute_scripts(self) -> bool:
        """
        Run all scripts in a sequence until all their event queues have drained

        This ensures that all communication between the scripts themselves has fully
        completed, and that nothing further could happen without another event coming
        in from outside the system.
        """
        handled = False
        while any(await asyncio.gather(*[s.execute() for s in self.scripts])):
            handled = True
        return handled

    async def test_simple(self):
        assembler = self._script_to_asm("""
default {
    state_entry() {
        llStopMoveToTarget();
    }
}
""")
        self.notecard.text = assembler.pack()[0]
        target_mock = Mock()
        self.manager_script.builtin_funcs['llStopMoveToTarget'] = target_mock
        await self.execute_scripts()
        target_mock.assert_called_once()

    async def test_lsl_conformance(self):
        with open(RESOURCES_PATH / "lsl_conformance.lsl", "rb") as f:
            assembler = self._script_to_asm(f.read())
        self.notecard.text = assembler.pack()[0]
        await self.execute_scripts()
        # Check test failed / passed numbers
        self.assertEqual(188, self.interp_script.gGlobals[0])
        self.assertEqual(0, self.interp_script.gGlobals[1])

    async def test_lsl_conformance2(self):
        with open(RESOURCES_PATH / "lsl_conformance2.lsl", "rb") as f:
            assembler = self._script_to_asm(f.read())
        self.notecard.text = assembler.pack()[0]
        await self.execute_scripts()
        # Check test failed / passed numbers
        self.assertEqual(69, self.interp_script.gGlobals[0])
        self.assertEqual(0, self.interp_script.gGlobals[1])

    async def test_long_script(self):
        assembler = Assembler()
        opcodes = [
            [OpCode.ALLOC_SLOTS, Whence.GLOBAL, types_to_str((LSLType.INTEGER,))],
            [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 0],
        ]

        for _ in range(0x2Fff):
            opcodes.extend([
                [OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 0, 1],
                [OpCode.BIN_OP, Operation.PLUS, LSLType.INTEGER, LSLType.INTEGER],
            ])

        opcodes.extend([
            [OpCode.STORE, LSLType.INTEGER, Whence.GLOBAL, 0],
            [OpCode.RET, 0],
        ])

        assembler.assemble(opcodes)
        self.notecard_handler.notecards.clear()

        new_notecards = []
        for i, notecard_text in enumerate(assembler.pack()):
            new_notecards.append(MockNotecard(f"script{str(i) if i else ''}", notecard_text))
        self.assertTrue(len(new_notecards) > 1)
        self.notecard_handler.notecards = new_notecards
        await self.execute_scripts()
        self.assertEqual(0x2Fff, self.interp_script.gGlobals[0])
