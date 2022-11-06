#!/usr/bin/env python
"""
Build an equivalent LSL constants file based on the constants
defined in Python. Also generates stubs to dynamically call
LSL library functions based on received link messages.
"""

import enum

import constants


def _to_chunks(chunkable, chunk_size: int):
    while chunkable:
        yield chunkable[:chunk_size]
        chunkable = chunkable[chunk_size:]


def _gen_func_wrapper(func_name, func):
    str_val = ""
    str_val += f"else if (lib_num == LIBFUNC_{func_name.upper()}) {{\n"
    str_val += "\t"
    if func.ret_type != "void":
        str_val += f"ret = (list)"
    str_val += f"{func_name}("
    for j, arg_type in enumerate(func.arg_types):
        if j:
            str_val += ", "
        real_arg_type = arg_type
        if arg_type == "list":
            arg_type = "string"
        elif arg_type == "rotation":
            arg_type = "rot"

        args_specifier = "args"

        # Allow the list to be GC'd
        if j == len(func.arg_types) - 1:
            args_specifier = "CLEARABLE_LIST(args)"

        accessor = f"llList2{arg_type.title()}({args_specifier}, {j})"
        if real_arg_type == "list":
            accessor = f"DESERIALIZE_LIST({accessor})"
        str_val += accessor
    str_val += ");\n"
    if func.ret_type == "list":
        str_val += f"\tret_type = LIBFUNCRET_LIST;\n"
    elif func.ret_type != "void":
        str_val += f"\tret_type = LIBFUNCRET_SIMPLE;\n"
    str_val += "} "
    return str_val


def main():
    # Convert our constants from Python to LSL so that we know we're using the same values in both
    with open("generated/constants.inc.lsl", "w") as f:
        for func_name, func in constants.LIBRARY_FUNCS.items():
            f.write(f"integer LIBFUNC_{func_name.upper()} = {func.num};\n")
        f.write("\n")
        for event_name, event in constants.EVENTS.items():
            f.write(f"integer EH_{event_name.upper()} = {event.num};\n")
        f.write("\n")

        for name, val in constants.__dict__.items():
            if name.startswith("_"):
                continue
            # Look through the "constants" module for any IntEnums
            if isinstance(val, type):
                if getattr(val, "_is_lsl_namedtuple", False):
                    # This is a typed stride for a strided list. Pull out the inner enum
                    # and generate a definition for the stride as well.
                    val = val.indices
                    f.write(f"integer {name.upper()}_STRIDE = {len(val)};\n")
                if issubclass(val, (enum.IntEnum, enum.IntFlag)):
                    # Splat out their values
                    for enum_val in val:
                        f.write(f"integer {name.upper()}_{enum_val.name} = {int(enum_val)};\n")
            elif isinstance(val, int):
                f.write(f"integer {name.upper()} = {int(val)};\n")
            else:
                continue

            f.write("\n")

        f.write("\n\n")

        # Include the list of functions blacklisted for execution by library scripts,
        # they need to be handled specifically by a state-aware script (probably the manager)
        special_nums = [constants.LIBRARY_FUNCS[x].num for x in constants.SPECIAL_FUNCTIONS]
        f.write(f"list SPECIAL_FUNCTIONS = {special_nums};")

        f.write("\n\n")

        # Figure out where in gDetectedStack a Detected data should live given the function num
        detected_func_offsets = [f"LIBFUNC_LLDETECTED{x.name}" for x in constants.DetectEntry.indices]
        f.write(f"list DETECTED_FUNC_OFFSETS = [{', '.join(detected_func_offsets)}];")

        f.write("\n\n")

        # Get default return types for each of the llDetected functions we support
        uppercase_funcs = {k.upper(): v for (k, v) in constants.LIBRARY_FUNCS.items()}
        detected_func_types = []
        for entry in constants.DetectEntry.indices:
            ret_type = uppercase_funcs[f"LLDETECTED{entry.name}"].ret_type
            detected_func_types.append(f"LSLTYPE_{ret_type.upper()}")
        f.write(f"list DETECTED_FUNC_TYPES = [{', '.join(detected_func_types)}];")

        f.write("\n\n")

    # Generate function call for every function in LSL, split across multiple scripts
    # so that we don't run out of bytecode space. Since LSL doesn't have reflection, anywhere
    # we might want to dynamically call a function by ID we need a "real" call to that function
    # somewhere. That's all these "library" script chunks do.
    for i, funcs_chunk in enumerate(_to_chunks(list(constants.LIBRARY_FUNCS.items()), 200)):
        with open(f"generated/library_funcs_{i}.inc.lsl", "w") as f:
            for func_name, func in funcs_chunk:
                if func_name in constants.SPECIAL_FUNCTIONS:
                    # This function will be handled specially by the manager, we can't use
                    # an auto-generated invocation wrapper for it.
                    continue
                f.write(_gen_func_wrapper(func_name, func))

    with open(f"generated/manager_funcs.inc.lsl", "w") as f:
        for func_name in sorted(constants.MANAGER_AUTO_FUNCTIONS):
            func = constants.LIBRARY_FUNCS[func_name]
            f.write(_gen_func_wrapper(func_name, func))


if __name__ == "__main__":
    main()
