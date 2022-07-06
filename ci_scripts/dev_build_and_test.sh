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


title "Create virtual env with poetry"
poetry install


title "Run mypy static checker"
cd "$REPO_DIR"
mypy .


title "Install litgen and its sub-packages (codemanip, srcmlcpp and litgen)"
cd "$REPO_DIR"
pip install -v -e .


title "Build litgensample"
cd "$REPO_DIR"/example
pip install -v -e .


title "Run pytest (will test codemanip, srcmlcpp, litgen, and litgensample)"
cd "$REPO_DIR"
pytest


title "Build lg-imgui python module"
cd "$REPO_DIR"/lg_projects/lg_imgui
pip install -v -e .


title "Build hello-imgui python modules"
cd "$REPO_DIR"/lg_projects/lg_hello_imgui
pip install -v -e .


title "Build lg-implot python modules"
cd "$REPO_DIR"/lg_projects/lg_implot
pip install -v -e .
