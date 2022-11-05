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

## Usage

You don't want to use this.

## License

the LSL code is MIT licensed. The tests and Python code are GPL licensed because
they use Lummao, which is also GPL'd.
