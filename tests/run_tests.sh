#!/bin/sh

PYTHON=python3

# Run all the tests
for i in $(ls test_*.py); do
    ${PYTHON} $i

    if [ $? -ne 0 ]; then
        printf "%s exited with error code %d\n" "${i}" "$?"
    fi
done