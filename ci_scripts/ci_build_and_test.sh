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


title "Install requirements"
python3 -m venv venv
source venv/bin/activate
pip install -r "$REPO_DIR"/requirements-dev.txt


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
cd "$REPO_DIR"/src/litgen/integration_tests
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
cd "$REPO_DIR"/_litgen_template
pip install -v $PIP_INSTALL_EDITABLE .
