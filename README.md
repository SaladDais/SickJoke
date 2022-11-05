# SickJoke

[![codecov](https://codecov.io/github/SaladDais/SickJoke/branch/master/graph/badge.svg?token=ZSRLNVAK05)](https://codecov.io/github/SaladDais/SickJoke)

SickJoke is a [meta-circular interpreter](https://en.wikipedia.org/wiki/Meta-circular_evaluator)
for LSL written in LSL. Basically, it's a set of LSL scripts that run LSL scripts.
It passes all the official LSL conformance tests, and can run non-trivial LSL scripts,
albeit slowly.

I made the mistake making a joke about writing an LSL interpreter in LSL that read scripts
from notecards. The joke went too far. I ended up writing most of the interpreter when I
had the flu, so... SickJoke, I guess.

For added fun, the tests are run in CI by transpiling the interpreter to Python, meaning
you're using LSL converted to Python to run LSL converted to IR converted to bytecode. Oy!

## Compiling the interpreter

* `pip install lummao`
* Clone https://github.com/Sei-Lisa/LSL-PyOptimizer and set the `LSL_PYOPTIMIZER_PATH`
  env var to its path
* `bash compile.sh` to compile the scripts
* `pip install pytest` and run `pytest` if you want to run the unit and integration tests

Everything in the `compiled/` directory should be a script in a prim in SL.

## Compiling an LSL script to a notecard

* `python lsl_to_notecard.py some_script.lsl`
* Copy the output to a notecard named "script" in the same prim.

## Design

### Manager Script

* Handles all inbound events (touch, listen, etc) and queues to send to the interpreter
* Reads code sections from the code notecard and feeds them to the interpreter as needed
* Knows what event handlers live where in the code notecard
* Maintains a cache of recently-read sections to speed up jumps around the script
* The script that actually handles perms and things given script-specific calls like `llRequestPermissions()`

### Interpreter Script

* The thing that actually runs all the code, other than library functions
* Only holds and executes a small slice of the code at a time, asks the Manager when it needs more
* Has one list for code, another for the stack and local vars, and another for globals
* Yields execution and sends a link message whenever it runs into a command like `llSay()`

### Library Scripts

* Only exist to receive and handle arbitrary `llWhatever()` calls from the Interpreter
* There are three of them to avoid violating script size limits.

### Compiler

* LSL -> IR step at https://github.com/SaladDais/Lummao/blob/master/src/json_ir_pass.cc
* IR -> Assembly step at https://github.com/SaladDais/SickJoke/blob/master/ir2asm.py
* Assembly -> packed notecard at https://github.com/SaladDais/SickJoke/blob/master/assembler.py

## Example Converted Script

```lsl
default {
    state_entry() {
        llSay(0, "Hello, Avatar!");
    }

    touch_start(integer total_number) {
        llSay(0, "Touched.");
    }
}
```

Above script converted with `python lsl_to_notecard.py hello_avatar.lsl`:

```
[31,1,36,7]
[0,0]
[14,6,0,134,"<Hello, Avatar!>",354447,14,6,0,134,"<Touched.>",354447,78]
```

## Usage

You don't want to use this.

## License

the LSL code is MIT licensed. The tests and Python code are GPL licensed because
they use Lummao, which is also GPL'd.
