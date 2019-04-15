#!/bin/bash
echo "Running pre-commit tests"
python3 -m unittest discover tests/
if [ $? -ne 0 ]; then
  echo "Tests must pass before commit!"
  exit 1
fi
