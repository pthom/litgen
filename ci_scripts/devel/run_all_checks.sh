#!/usr/bin/env bash
# set -e

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
repo_dir=$(realpath $this_dir/../..)

# Run all checks
cd $repo_dir

# Catch errors and display error message
trap 'echo "Error occured on line $LINENO"; exit 1' ERR

echo "Run mypy ."
mypy .
echo "Run black ."
black .
echo "Run ruff ."
ruff .
echo "Run pytest"
pytest
echo "Success!"
