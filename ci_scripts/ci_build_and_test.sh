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
pip install -v .

title "Run srcmlcpp tests"
cd $REPO_DIR/srcmlcpp
pytest

title "Run litgen tests"
cd $REPO_DIR/litgen
pytest

title "Build example"
cd $REPO_DIR/example
pip install -v .

title "Test example"
python -c "import litgensample; print(litgensample.add(59, 41));"