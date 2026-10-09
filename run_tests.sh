#!/bin/bash
# Test runner script for kurucz-torch project
# Sets up PYTHONPATH and runs unittest discovery

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/python"
TESTS_DIR="$SCRIPT_DIR/tests"

# Determine Python executable (try conda environment first)
if [ -n "$CONDA_PREFIX" ]; then
    PYTHON="$CONDA_PREFIX/bin/python"
elif [ -x "/srv/local/tmp/dobos/gapipe/stack/conda/envs/kurucz-torch/bin/python" ]; then
    PYTHON="/srv/local/tmp/dobos/gapipe/stack/conda/envs/kurucz-torch/bin/python"
else
    PYTHON="python"
fi

# Export PYTHONPATH to include python directory
export PYTHONPATH="$PYTHON_DIR:${PYTHONPATH}"

# Run tests
echo "Running tests from $TESTS_DIR"
echo "Python: $PYTHON"
echo "PYTHONPATH: $PYTHONPATH"
echo ""

cd "$SCRIPT_DIR"

# Run specific test directory if provided
if [ $# -eq 0 ]; then
    # Run all tests
    "$PYTHON" -m unittest discover "$TESTS_DIR/kurucz" -v
else
    # Run specific tests
    "$PYTHON" -m unittest "$@"
fi
