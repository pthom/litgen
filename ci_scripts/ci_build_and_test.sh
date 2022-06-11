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

title "Install litgen"
pip install .

title "Run srcmlcpp tests"
cd "$REPO_DIR"/srcmlcpp
pytest

title "Run litgen tests"
cd "$REPO_DIR"/litgen
pytest

title "Build litgensample"
cd "$REPO_DIR"/example
pip install .

title "Test litgensample"
cd "$REPO_DIR"/litgen/tests_litgensample
python test_litgensample.py

title "Build lg-imgui"
cd "$REPO_DIR"/examples_real_libs/imgui
pip install .

