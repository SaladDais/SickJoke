#!/bin/bash

set -e

# This is the crap I write instead of figuring out how to write Makefiles.

# Comment this out if you don't want to build the python testcases,
# or set BUILD_PYTHON_HARNESSES env var to 0.
BUILD_PYTHON_HARNESSES="${BUILD_PYTHON_HARNESSES:-1}"

shopt -s nullglob

if [[ -z "${LSL_PYOPTIMIZER_PATH}" ]]; then
	>&2 echo "LSL_PYOPTIMIZER_PATH environment variable must be set"
	exit 1
fi

if [[ -z "$(which cpp)" ]]; then
	>&2 echo "GNU C Preprocessor must be installed"
	exit 1
fi

if [[ -z "$(which lummao)" && "${BUILD_PYTHON_HARNESSES}" == 1 ]]; then
	>&2 echo "lummao must be installed"
	exit 1
fi

pushd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null

python generate_code.py
mkdir -p compiled
mkdir -p pythonized
rm -f compiled/*
rm -rf pythonized/__pycache__
rm -f pythonized/*.py
touch pythonized/__init__.py

for f in *."lsl"; do
	echo "compiling $f"
	basef="$(basename "$f" ".lsl")"
	compiledf="compiled/${basef}.o.lsl"
	compiledforpyf="pythonized/${basef}.forpy.lsl"
	pythonizedf="pythonized/${basef}.py"

	# Compile a version of each script for upload to SL
	case "$basef" in
	  library)
	    # Don't build this for upload to SL, it's only for Python.
	    ;;
	  *)
	    python "${LSL_PYOPTIMIZER_PATH}/main.py" -P "-I" -P "." -y -H -O addstrings,-extendedglobalexpr -p gcpp --precmd=cpp "$f" -o "$compiledf"
	    ;;
	esac

	case "$basef" in
		# These don't need compiling to Python, they're only for upload to SL.
		library_*)
			# But they _do_ need fixing up so they're actually uploadable. They end up with such fucked
			# up deeply indented conditions that the viewer's text editor explodes. Never seen that in
			# my life, but just use sed to kill unnecessary leading spaces.
			echo "Stripping leading spaces from ${compiledf}"
			sed -i.bak -e 's/^[\t ]*//' "${compiledf}"
			rm "${compiledf}.bak"
			;;
		*)
		  # Potentially do a python-specific version of these scripts
			if [[ "${BUILD_PYTHON_HARNESSES}" == 1 ]]; then
			  # Python really doesn't like deeply nested branches like LSL-PyOptimizer might do
			  # to save bytecode space. Compile a separate version of the script just for converting
			  # to Python. We still want the ConstFold optimization in the typical case because that will
			  # throw away all the useless casts and save bytecode.
			  python "${LSL_PYOPTIMIZER_PATH}/main.py" -P "-I" -P "." -P "-DDEBUG" -y -H -O addstrings,-extendedglobalexpr,-ifelseswap -p gcpp --precmd=cpp "$f" -o "$compiledforpyf"
				echo "pythonizing $compiledforpyf"
				lummao "$compiledforpyf" "$pythonizedf"
			fi
			;;
	esac
done

popd > /dev/null
