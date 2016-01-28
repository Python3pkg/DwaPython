#!/bin/bash
set -e
find dwa tests -name '*.py' -exec autopep8 --in-place --max-line-length=120 '{}' \;
./code-check.sh
python setup.py test
python3 setup.py test
