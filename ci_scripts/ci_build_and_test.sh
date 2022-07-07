SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

set -e  # Exit on error
set -x  # Trace commands

REPO_DIR=$SCRIPT_DIR/..

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


title "Check that lg_imgui, lg_hello_imgui and lg_implot use the same imgui version"
lg_projects_dir=$REPO_DIR/lg_projects
lg_project=lg_imgui
cd "$lg_projects_dir"/$lg_project/external/imgui && git --no-pager log --format="%H" -n 1 > "$lg_projects_dir"/"$lg_project".githead && cd "$lg_projects_dir"
lg_project=lg_hello_imgui
cd "$lg_projects_dir"/$lg_project/external/imgui && git --no-pager log --format="%H" -n 1 > "$lg_projects_dir"/"$lg_project".githead && cd "$lg_projects_dir"
lg_project=lg_implot
cd "$lg_projects_dir"/$lg_project/external/imgui && git --no-pager log --format="%H" -n 1 > "$lg_projects_dir"/"$lg_project".githead && cd "$lg_projects_dir"
# those diffs fail if they differ and the script will exit
diff lg_imgui.githead lg_hello_imgui.githead
diff lg_imgui.githead lg_implot.githead


title "Create virtual env"
cd $REPO_DIR
rm -rf venv_ci/
python3 -m venv venv_ci
. venv_ci/bin/activate
which python


title "Install requirements"
cd $REPO_DIR
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


title "Build lg_imgui python module"
cd "$REPO_DIR"/lg_projects/lg_imgui
pip install .


title "Build lg_hello_imgui python modules"
cd "$REPO_DIR"/lg_projects/lg_hello_imgui
pip install .


title "Build lg_implot python modules"
cd "$REPO_DIR"/lg_projects/lg_implot
pip install .

title "Build lg_template python modules"
cd "$REPO_DIR"/lg_projects/lg_template
pip install .
