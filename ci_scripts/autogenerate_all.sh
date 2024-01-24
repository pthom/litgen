SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

set -e  # Exit on error
set -x  # Trace commands

REPO_DIR=$SCRIPT_DIR/..

cd "$REPO_DIR"


function title {
  set +x
  decoration="=============================================================="
  echo "


$decoration
   $1
$decoration
"
  set -x
}

title "python ./_litgen_template/tools/autogenerate_bindings.py"
python ./_litgen_template/tools/autogenerate_bindings.py

title "python ./src/litgen/integration_tests/autogenerate_mylib.py"
python ./src/litgen/integration_tests/autogenerate_mylib.py
