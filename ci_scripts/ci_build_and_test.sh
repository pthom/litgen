SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

set -e  # Exit on error
set -x  # Trace commands

REPO_DIR=$SCRIPT_DIR/..
# PIP_INSTALL_EDITABLE="-e"
PIP_INSTALL_EDITABLE=""

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


title "Poetry install / add to PATH"
cd "$REPO_DIR"
poetry install
poetry_python_path=$(poetry run which python)
poetry_python_folder=$(dirname $poetry_python_path)
export PATH=$poetry_python_folder:$PATH
echo poetry_python_folder=$poetry_python_folder


title "Run black"
cd "$REPO_DIR"
black .


title "Run mypy static checker"
cd "$REPO_DIR"
mypy .


title "autogenerate_all"
cd "$REPO_DIR"
./ci_scripts/autogenerate_all.sh


title "Build litgen/integration_tests pip package (lg_mylib)"
cd "$REPO_DIR"/packages/litgen/integration_tests
pip install -v $PIP_INSTALL_EDITABLE .


title "Run pytest (will test codemanip srcmlcpp litgen, and litgensample)"
cd "$REPO_DIR"
pytest


title "cmake build all"
cd "$REPO_DIR"
mkdir -p build_ci
cd build_ci
cmake ..
make -j 4


title "pip build lg_skbuild_template python modules"
cd "$REPO_DIR"/demos/litgen/lg_skbuild_template
pip install -v $PIP_INSTALL_EDITABLE .
