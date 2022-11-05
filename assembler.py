"""
Assembles instructions into a bytecode format, formatting the notecard nicely.
"""
import json
from typing import List, Dict, Callable, NamedTuple, Hashable

from constants import *


class Label(str):
    """Named label that can be jumped to"""
    pass


class HandlerLabel(NamedTuple):
    """Label for an event handler, like state_entry()"""
    state: int
    event: str


def _clamp_opcode(assembled_instr):
    assert(assembled_instr <= 0xFFffFFff)
    assert(assembled_instr > -0x80000000)
    if assembled_instr > 0x7FffFFff:
        assembled_instr = -assembled_instr
    return assembled_instr


def pack_json(val) -> str:
    return json.dumps(val, separators=(',', ':'), ensure_ascii=False)


def types_to_str(types):
    return "".join((str(int(x)) for x in types))


class Assembler:
    # Actually 1024 (incl newline) but let's be conservative.
    MAX_LINE = 500

    def __init__(self):
        self.assembled = []
        self._opcode_dispatch: Dict[OpCode, Callable] = {
            OpCode.PUSH: self._assemble_push_or_store,
            OpCode.STORE: self._assemble_push_or_store,
            OpCode.STORE_DEFAULT: self._assemble_push_or_store,
            OpCode.ALLOC_SLOTS: self._assemble_alloc_slots,
            OpCode.JUMP: self._assemble_jump_or_call,
            OpCode.CALL: self._assemble_jump_or_call,
            OpCode.CALL_LIB: self._assemble_call_lib,
        }
        self.deferred_jumps: Dict[int, List] = {}
        self.labels: Dict[Hashable, int] = {}
        self.event_handlers: Dict[HandlerLabel, int] = {}
        self.lines: List[int] = [0]
        self.cur_line = []

    def assemble(self, vals: List):
        if self.assembled:
            raise RuntimeError("Already assembled")

        for val in vals:
            if isinstance(val, list):
                opcode = val[0]
                args = val[1:]
                handler = self._opcode_dispatch.get(opcode, self._assemble_simple)
                assembled_opcode = handler(opcode, *args)
                opcode, operands = assembled_opcode[0], assembled_opcode[1:]
                op_and_operands = [_clamp_opcode(opcode), *operands]

                # If the notecard line gets too long then we need to drop to the next
                # line, but we don't want to split opcodes off from their operands.
                # Check if adding this to the line
                if not self._will_fit(op_and_operands):
                    # Ok, start a new line and mark this as the first instruction.
                    self.lines.append(len(self.assembled))
                    self.cur_line.clear()
                    if not self._will_fit(op_and_operands):
                        raise ValueError(f"Bytecode won't fit on a line! {op_and_operands!r}")
                self.assembled.extend(op_and_operands)
                self.cur_line.extend(op_and_operands)

            elif isinstance(val, (Label, HandlerLabel)):
                if val in self.labels:
                    raise ValueError(f"{val!r} already in self.labels!")
                self.labels[val] = len(self.assembled)
                if isinstance(val, HandlerLabel):
                    self.event_handlers[val] = len(self.assembled)
            else:
                raise ValueError(f"unexpected instruction type {val!r}")

        self._patch_jumps()

        return self.assembled

    def _will_fit(self, op_and_operands):
        return len(pack_json(self.cur_line + op_and_operands).encode("utf8")) < self.MAX_LINE

    def _patch_jumps(self):
        for jump_pos, jump_params in self.deferred_jumps.items():
            opcode, jump_type, jump_target = jump_params
            if isinstance(jump_target, (Label, HandlerLabel)):
                jump_target = self.labels[jump_target]
            # Jumps are relative to the instruction AFTER the jump
            rel_jump_target = jump_target - (jump_pos + 1)
            self.assembled[jump_pos] = _clamp_opcode(int(
                opcode | ((jump_type | (rel_jump_target << 3)) << OPCODE_WIDTH)
            ))

    def _assemble_simple(self, opcode, *args) -> List[int]:
        num_args = len(args)
        if num_args > 3:
            raise ValueError(f"Non-simple case: {(opcode, args):!r}")

        arg_bits = 0x0
        if num_args == 1:
            # 24-bit arg
            arg_bits = int(args[0])
            if arg_bits & ~0x00FFffFF:
                raise ValueError(f"Arg out of range {(opcode, args)!r}")
        elif num_args == 2 or num_args == 3:
            # 2 or 3 8-bit args
            if any(x & ~0xff for x in args):
                raise ValueError(f"Arg out of range {(opcode, args)!r}")
            first_arg = True
            for arg in reversed(args):
                if not first_arg:
                    arg_bits <<= 8
                arg_bits |= arg
                first_arg = False

        return [int(opcode | (arg_bits << OPCODE_WIDTH))]

    def _assemble_push_or_store(self, opcode, whatce, whence, wherece, *operands) -> List[int]:
        wherece <<= 8
        whence <<= 5
        operands = list(operands)
        assert len(operands) < 2
        if operands and whatce == LSLType.STRING:
            # https://jira.secondlife.com/browse/BUG-227035
            operands = [f"<{operands[0]}>"]
        return [int(opcode | ((whatce | whence | wherece) << OPCODE_WIDTH)), *operands]

    def _assemble_alloc_slots(self, _opcode, whence, args_str) -> List[int]:
        return [int(OpCode.ALLOC_SLOTS | (whence << OPCODE_WIDTH)), args_str]

    def _assemble_jump_or_call(self, opcode, jump_type, target):
        self.deferred_jumps[len(self.assembled)] = [opcode, jump_type, target]
        # return placeholder
        return [int(OpCode.JUMP | (0x00ffFFff << OPCODE_WIDTH))]

    def _assemble_call_lib(self, _opcode, num_args, lib_func, no_wait=0) -> List[int]:
        # 15 args supported max
        assert(not (num_args & ~0x0F))
        # The library function can be referenced by name _or_ number, but
        # we need to resolve to the number version when assembling.
        if isinstance(lib_func, str):
            lib_func = LIBRARY_FUNCS[lib_func].num
        lib_func <<= 4
        no_wait <<= 16
        return [int(OpCode.CALL_LIB | ((num_args | lib_func | no_wait) << OPCODE_WIDTH))]

    def pack(self) -> str:
        packed_handlers = []
        # Make a flattened strided list of line number -> instruction pointer
        line_ips = []
        for i, ip in enumerate(self.lines):
            # TODO: multi-notecard support
            line_ips.extend(CodeIndex(ip=ip, nc_and_line=i))

        for handler, ip in self.event_handlers.items():
            event_num = EVENTS[handler.event].num
            packed_handlers.extend(HandlerIndex(state_and_event=(handler.state << 16) | event_num, ip=ip))

        # Split out the assembled code into separate lines along the pre-established line boundaries
        split_code = []
        last_start = None
        for line_start in reversed(self.lines):
            split_code.insert(0, self.assembled[line_start:last_start])
            last_start = line_start

        return "\n".join(pack_json(v) for v in (packed_handlers, line_ips, *split_code))
