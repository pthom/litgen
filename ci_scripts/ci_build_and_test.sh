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


title "Check that lg_imgui and lg_hello_imgui use the same imgui version"
lg_projects_dir=$REPO_DIR/examples_real_libs
lg_project=imgui
cd "$lg_projects_dir"/$lg_project/external/imgui && git --no-pager log --format="%H" -n 1 > "$lg_projects_dir"/"$lg_project".githead && cd "$lg_projects_dir"
lg_project=hello_imgui
cd "$lg_projects_dir"/$lg_project/external/imgui && git --no-pager log --format="%H" -n 1 > "$lg_projects_dir"/"$lg_project".githead && cd "$lg_projects_dir"
diff imgui.githead hello_imgui.githead # this will fail if they differ


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


title "Build lg-imgui python module"
cd "$REPO_DIR"/examples_real_libs/imgui
pip install .


title "Build hello-imgui python modules"
cd "$REPO_DIR"/examples_real_libs/hello_imgui
pip install .
