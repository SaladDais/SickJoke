#!/usr/bin/env python
import sys

from lummao import convert_script_to_ir
from ir2asm import IRConverter
from assembler import Assembler


def main():
    with open(sys.argv[1], "rb") as f:
        converter = IRConverter(convert_script_to_ir(f.read()))

    assembler = Assembler()
    converted_ir = converter.convert()
    assembler.assemble(converted_ir)
    print(assembler.pack())


if __name__ == "__main__":
    main()
