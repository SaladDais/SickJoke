"""
Compiles Lummao LSL intermediate representation to SickJoke bytecode.
"""

from typing import *

from lummao import Key, Vector, Quaternion, convert_script_to_ir

from assembler import Label, types_to_str, HandlerLabel
from constants import *


class IRConverter:
    def __init__(self, ir: Dict):
        self.ir = ir
        self.asm_list = []
        self.states = []

    def convert(self) -> List[Any]:
        if self.asm_list:
            raise RuntimeError("IRConverter has already been used!")

        for state in self.ir["states"]:
            self.states.append(state["name"])

        self.asm_list.append(Label("_start"))
        global_types = [LSLType[x.upper()] for x in self.ir["globals"]]
        if global_types:
            self.asm_list.append([OpCode.ALLOC_SLOTS, Whence.GLOBAL, types_to_str(global_types)])
        self.build_function({"code": self.ir["init_code"]}, "_start")

        for func in self.ir["functions"]:
            unique_prefix = f"f{func['name']}"
            self.asm_list.append(Label(unique_prefix))
            self.build_function(func, unique_prefix + "/")

        for state_num, state in enumerate(self.ir["states"]):
            for handler in state["handlers"]:
                unique_prefix = f"e{state['name']}/{handler['name']}"
                self.asm_list.append(HandlerLabel(state_num, handler["name"]))
                self.build_function(handler, unique_prefix + "/")

        return self.asm_list

    def build_function(self, func_data: Dict, unique_prefix: str):
        if func_data.get("locals"):
            local_types = [LSLType[x.upper()] for x in func_data["locals"]]
            self.asm_list.append([OpCode.ALLOC_SLOTS, Whence.LOCAL, types_to_str(local_types)])

        for instr in func_data["code"]:
            instr_type = instr["instr_type"]
            if instr_type == "label":
                self.asm_list.append(Label(unique_prefix + instr["label"]))
                continue
            assert(instr_type == "op")

            whence, index = self._fix_whence(func_data, instr)
            op = instr["op"]

            if op in ("STORE", "STORE_DEFAULT", "PUSH"):
                self.asm_list.append([
                    OpCode[op], LSLType[instr["type"].upper()], whence, index,
                ])
            elif op == "PUSH_CONSTANT":
                value = instr["value"]
                if instr["type"] == "vector":
                    value = str(Vector([float(x) for x in value]))
                elif instr["type"] == "rotation":
                    value = str(Quaternion([float(x) for x in value]))
                elif instr["type"] == "key":
                    value = Key(value)
                elif instr["type"] == "float":
                    value = float(value)

                self.asm_list.append([
                    OpCode.PUSH, LSLType[instr["type"].upper()], Whence.CONST, 0, value
                ])
            elif op == "PUSH_EMPTY":
                # Equivalent to PUSHE in LSO. Empties are only really used as placeholders,
                # and we don't really care about the type of those. Just use an empty integer
                # since it's the smallest.
                self.asm_list.append([
                    OpCode.PUSH, LSLType.INTEGER, Whence.CONST, 1
                ])
            elif op == "JUMP":
                self.asm_list.append([
                    OpCode[op], JumpType[instr["jump_type"].upper()], Label(unique_prefix + instr["label"]),
                ])
            elif op == "POP_N":
                self.asm_list.append([
                    OpCode[op], instr["num"],
                ])
            elif op == "CHANGE_STATE":
                self.asm_list.append([
                    OpCode[op], self.states.index(instr["state"]),
                ])
            elif op == "RET":
                self.asm_list.append([
                    OpCode[op], len(func_data.get("args", [])),
                ])
            elif op in ("TAKE_MEMBER", "REPLACE_MEMBER"):
                self.asm_list.append([
                    OpCode[op], LSLType[instr["type"].upper()], instr["offset"],
                ])
            elif op in ("DUP", "SWAP", "DUMP"):
                self.asm_list.append([
                    OpCode[op],
                ])
            elif op == "CAST":
                self.asm_list.append([
                    OpCode[op], LSLType[instr["from_type"].upper()], LSLType[instr["to_type"].upper()],
                ])
            elif op in ("BOOL", "BUILD_COORD"):
                self.asm_list.append([
                    OpCode[op], LSLType[instr["type"].upper()],
                ])
            elif op == "BUILD_LIST":
                self.asm_list.append([
                    OpCode[op], instr["num_elems"],
                ])
            elif op == "CALL":
                self.asm_list.append([
                    OpCode[op], 0, Label(f"f{instr['name']}"),
                ])
            elif op == "CALL_LIB":
                num_args = len(LIBRARY_FUNCS[instr["name"]].arg_types)
                self.asm_list.append([
                    OpCode[op], num_args, instr["name"], 0
                ])
            elif op == "UN_OP":
                self.asm_list.append([
                    OpCode[op], Operation[instr["operation"]], LSLType[instr["type"].upper()],
                ])
            elif op == "BIN_OP":
                left_type = LSLType[instr["left_type"].upper()]
                right_type = LSLType[instr["right_type"].upper()]

                # To simplify things, the interpreter only implements a single variant of equivalent
                # expressions where the types can be swapped. Swap the operands on the stack before
                # we execute. This ensures we still evaluate the expressions right-to-left like LSL
                # demands.
                need_swap = False
                if left_type == LSLType.FLOAT and right_type == LSLType.VECTOR:
                    need_swap = True
                elif left_type == LSLType.ROTATION and right_type == LSLType.VECTOR:
                    need_swap = True

                if need_swap:
                    self.asm_list.append([OpCode.SWAP])
                    left_type, right_type = right_type, left_type

                self.asm_list.append([OpCode[op], Operation[instr["operation"]], left_type, right_type])
            else:
                raise ValueError(f"Unknown instr {instr!r}")

    def _fix_whence(self, func_data, instr) -> Tuple[Optional[Whence], Optional[int]]:
        if "whence" not in instr:
            return None, None
        whence = instr["whence"]
        index = int(instr["index"])
        # Store in retval, actually uses ARG offset in our bytecode
        if whence == "RETURN":
            whence = "ARG"
            # retval goes just past the first arg
            index = len(func_data.get("args", []))
        elif whence == "ARG":
            index = (len(func_data.get("args", [])) - 1) - index

        return Whence[whence], index
