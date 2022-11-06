"""
Constants shared between LSL and Python

Converted to LSL by generated_code.py.

* Integer constants will be included as-is
* Enums will be converted to LSL with prefixed values
* NamedTuples will be treated as indices into strided lists
"""

import enum
import os
import typing

from lummao import Key


OPCODE_WIDTH = 6
# How many registers get pushed when we CALL
CALL_REGISTERS_LEN = 3


def _limit_bits(num_bits):
    max_val = (2 ** num_bits) - 1

    def _cls_wrapper(cls):
        if max(cls) > max_val:
            raise ValueError(f"{cls}'s {int(max(cls))} is bigger than {max_val}")
        return cls
    return _cls_wrapper


class LibraryFunc(typing.NamedTuple):
    num: int
    arg_types: typing.List[str]
    ret_type: str
    name: str


def _parse_builtins() -> typing.Tuple[dict, dict]:
    library_funcs = {}
    events = {}
    with open(os.environ["LSL_PYOPTIMIZER_PATH"] + "/builtins.txt", "r") as f:
        cur_func_num = 0
        cur_event_num = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            decl_type, _, decl = line.partition(" ")
            # Only care about functions
            if decl_type == "const":
                continue
            func_name, _, argspec = decl.partition("(")
            argspec = argspec.rstrip(")")
            args = []
            for arg in argspec.split(","):
                arg = arg.strip()
                if not arg:
                    continue
                arg_type, _, arg_name = arg.partition(" ")
                args.append(arg_type.strip())
            func_name = func_name.strip()
            if decl_type == "event":
                events[func_name] = LibraryFunc(
                    ret_type="void",
                    arg_types=args,
                    num=cur_event_num,
                    name=func_name,
                )
                cur_event_num += 1
            else:
                library_funcs[func_name] = LibraryFunc(
                    ret_type=decl_type,
                    arg_types=args,
                    num=cur_func_num,
                    name=func_name,
                )
                cur_func_num += 1
    return library_funcs, events


LIBRARY_FUNCS, EVENTS = _parse_builtins()


# relatively small number of opcodes
# with a lot of options for those opcodes to reduce
# branching overhead. LSL doesn't have a switch() statement,
# jump tables, or computed goto!
#
# For ex, LSO2 has a "PUSHGS", which means push a string
# from a global, instead we have a "PUSH" with "whence" and
# "type" operands of "global" and "string".
@_limit_bits(OPCODE_WIDTH)
class OpCode(enum.IntEnum):
    NO_OP = 0

    BIN_OP = enum.auto()
    UN_OP = enum.auto()
    CAST = enum.auto()
    BOOL = enum.auto()

    ALLOC_SLOTS = enum.auto()
    PUSH = enum.auto()
    POP_N = enum.auto()
    STORE = enum.auto()
    STORE_DEFAULT = enum.auto()
    DUP = enum.auto()
    SWAP = enum.auto()

    JUMP = enum.auto()
    CALL = enum.auto()
    RET = enum.auto()
    CALL_LIB = enum.auto()

    BUILD_LIST = enum.auto()
    BUILD_COORD = enum.auto()

    # These should be close to last.
    # They're instructions for working with the member
    # accessors of vectors and rotations
    TAKE_MEMBER = enum.auto()
    REPLACE_MEMBER = enum.auto()

    YIELD = enum.auto()
    CHANGE_STATE = enum.auto()

    DUMP = enum.auto()


@_limit_bits(2)
class Register(enum.IntEnum):
    BP = 0
    IP = enum.auto()


@_limit_bits(2)
class JumpType(enum.IntEnum):
    ALWAYS = 0
    IF = 1
    NIF = 2


@_limit_bits(2)
class CallType(enum.IntEnum):
    RELATIVE = 0
    ABSOLUTE = enum.auto()


@_limit_bits(2)
class Whence(enum.IntEnum):
    CONST = 0
    LOCAL = enum.auto()
    GLOBAL = enum.auto()
    ARG = enum.auto()


@_limit_bits(4)
class LSLType(enum.IntEnum):
    # Note that this does NOT match LSL's TYPE_ builtin constants!
    # We optimize for smaller string representation of integer opcodes.

    # Can't ever go above 9 due to how we do type strings
    # (or 15 if we switched to hex)
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    KEY = 3
    VECTOR = 4
    ROTATION = 5
    LIST = 6
    VOID = 7


@_limit_bits(2)
class CoordAccessor(enum.IntEnum):
    X = 0
    Y = enum.auto()
    Z = enum.auto()
    S = enum.auto()


@_limit_bits(5)
class Operation(enum.IntEnum):
    """
    Kinds of operations in LSL

    Some of these that LSL supports aren't in here because they'll
    be de-sugared by the compiler.
    """
    PLUS = 0
    MINUS = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MOD = enum.auto()
    BOOLEAN_NOT = enum.auto()
    BOOLEAN_AND = enum.auto()
    BOOLEAN_OR = enum.auto()
    LESS = enum.auto()
    GREATER = enum.auto()
    LEQ = enum.auto()
    GEQ = enum.auto()
    EQ = enum.auto()
    NEQ = enum.auto()
    BIT_NOT = enum.auto()
    BIT_XOR = enum.auto()
    BIT_AND = enum.auto()
    BIT_OR = enum.auto()
    SHIFT_LEFT = enum.auto()
    SHIFT_RIGHT = enum.auto()


# Not bit-limited, this will occupy the whole `num` field of a `link_message`
class IPCType(enum.IntEnum):
    # MIN and MAX MUST be set so the manager can figure out
    # which link_message ranges belong to the interpreter,
    # to strip those out when forwarding events along.
    MIN = 0XF1FE
    # Interpreter -> Library
    CALL_LIB = enum.auto()
    # Interpreter <- Library
    CALL_LIB_REPLY = enum.auto()

    # Manager -> Interpreter
    INVOKE_HANDLER = enum.auto()
    # Interpreter -> Manager
    HANDLER_FINISHED = enum.auto()

    # Interpreter -> Manager
    REQUEST_CODE = enum.auto()
    # Interpreter <- Manager
    REQUEST_CODE_REPLY = enum.auto()

    # Manager -> *
    MANAGER_RESTARTED = enum.auto()
    # Manager -> Interpreter
    SCRIPT_LOADED = enum.auto()
    # Interpreter -> Manager
    CHANGE_STATE = enum.auto()

    MAX = enum.auto()


class LibFuncRet(enum.IntEnum):
    NONE = 0
    SIMPLE = enum.auto()
    LIST = enum.auto()


class LoadState(enum.IntEnum):
    NONE = 0
    HANDLERS = enum.auto()
    LINES = enum.auto()
    CODE = enum.auto()


def _lsl_namedtuple(cls):
    """
    Mark this NamedTuple as a definition for a typed list stride

    Makes it less annoying to ensure we're working with the same stride definitions in
    both Python and LSL. These get splatted out into index offsets + stride definitions
    for LSL in generate_code.py.
    """
    cls._is_lsl_namedtuple = True
    cls.indices = enum.IntEnum(cls.__name__, [(v.upper(), k) for k, v in enumerate(cls._fields)])
    return cls


@_lsl_namedtuple
class HandlerIndex(typing.NamedTuple):
    """An index allowing lookup of state and event -> instruction pointer"""
    # ORed together, state is top 16 bits, event type is bottom 16 bits.
    state_and_event: int
    # IP where the event handler starts, manager asks interpreter to call
    # into this.
    ip: int


@_lsl_namedtuple
class CodeIndex(typing.NamedTuple):
    """An index used to find which notecard line a code chunk lives on"""
    # IP for the first byte in the code line
    ip: int
    # ORed together to notecard num and line. Notecard in the high bits.
    nc_and_line: int


@_lsl_namedtuple
class CachedCode(typing.NamedTuple):
    """An entry in the Manager's LRU code cache"""
    last_used: int
    # ORed together to notecard num and line. Notecard in the high bits.
    # Used as a cache key
    nc_and_line: int
    code: typing.Union[str, int]  # only the placeholder is an int


# How many code lines to keep in the cache
NUM_CACHED_CODES = 20
CACHED_CODES_LEN = NUM_CACHED_CODES * len(CachedCode.indices)


@_lsl_namedtuple
class QueuedEvent(typing.NamedTuple):
    """An event the Manager is holding until the Interpreter is ready"""
    state_and_event: int
    ip: int
    args: str
    detected_stack: str


@_lsl_namedtuple
class DetectEntry(typing.NamedTuple):
    key: Key
    owner: Key


MAX_QUEUED_EVENTS = 5
MAX_EVENT_QUEUE_SIZE = MAX_QUEUED_EVENTS * len(QueuedEvent.indices)

# Some functions need special handling by some other script, and should _not_ be handled
# by the library scripts. Especially important for functions that only generate events
# in the script that called the function, like llListen().

# These are ones that can have autogenerated wrappers that just need to live in the
# manager script.
MANAGER_AUTO_FUNCTIONS = {
    # Things might get wacky if some async thing is the thing sleeping
    "llSleep",
    # We need to handle listen() events
    "llListen",
    "llListenRemove",
    "llListenControl",
    # We need to handle timer() events
    "llSetTimerEvent",
    # Targets are script-specific, we need to make sure they're always dealt with from
    # the same script.
    "llMoveToTarget",
    "llStopMoveToTarget",
    # These are probably the same as above
    "llLookAt",
    "llRotLookAt",
    "llStopLookAt",
    # These all need to live in the same script
    "llGetTime",
    "llResetTime",
    "llGetAndResetTime",

    # If we don't do this from the same script as the one with the link_message() event
    # (the manager) then we'll pick up our own link messages!
    "llMessageLinked",

    # These are functions that deal with perms. They need to live in the same script
    # that has the perms, they can't be in _any_ other script!
    "llGetPermissions",
    "llGetPermissionsKey",
    "llRequestPermissions",

    "llTransferLindenDollars",
    "llGiveMoney",

    "llTakeControls",
    "llReleaseControls",

    "llStartAnimation",
    "llStopAnimation",

    "llAttachToAvatar",
    "llAttachToAvatarTemp",
    "llDetachFromAvatar",

    "llBreakAllLinks",
    "llBreakLink",
    "llCreateLink",

    "llGetCameraPos",
    "llGetCameraRot",

    "llSetCameraParams",
    "llClearCameraParams",

    "llTeleportAgent",

    "llManageEstateAccess",

    "llSetAnimationOverride",
    "llGetAnimationOverride",
    "llResetAnimationOverride",

    "llReturnObjectsByOwner",
    "llReturnObjectsByID",
}

# All functions that have implementations that live in manager.lsl
SPECIAL_FUNCTIONS = sorted({
    *MANAGER_AUTO_FUNCTIONS,
    # These have special implementations that can't be autogenerated. They're written
    # directly in manager.lsl.
    "llDie",
    "llResetScript",
    "llDetectedKey",
    "llDetectedOwner",
})
