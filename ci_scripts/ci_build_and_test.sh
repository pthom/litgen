SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

set -e  # Exit on error
set -x  # Trace commands

REPO_DIR=$SCRIPT_DIR/..

function title {
  set +x
  decoration="================================================"
  echo "


$decoration
   $1
$decoration
"
  set -x
}


title "Create virtual env"
rm -rf venv_ci/
python3 -m venv venv_ci
. venv_ci/bin/activate
which python

title "Install requirements"
pip install -r requirements-dev.txt
pip install -r requirements.txt

title "Run mypy static checker"
cd "$REPO_DIR"
mypy .

title "Install litgen and its sub-packages (codemanip, srcmlcpp and litgen)"
cd "$REPO_DIR"
pip install .

title "Build litgensample"
cd "$REPO_DIR"/example
pip install .

title "Run pytest (will test codemanip, srcmlcpp, litgen, and litgensample)"
cd "$REPO_DIR"
pytest

title "Build lg-imgui"
cd "$REPO_DIR"/examples_real_libs/imgui
pip install .
