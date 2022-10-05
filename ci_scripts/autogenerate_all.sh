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

title "python ./lg_projects/lg_skbuild_template/autogenerate_lg_examplelib.py"
python ./lg_projects/lg_skbuild_template/autogenerate_lg_examplelib.py

title "python ./packages/litgen/integration_tests/autogenerate_mylib.py"
python ./packages/litgen/integration_tests/autogenerate_mylib.py

title "python ./lg_projects/lg_imgui/autogenerate_imgui.py"
python ./lg_projects/lg_imgui/autogenerate_imgui.py

title "python ./lg_projects/lg_imgui_bundle/autogenerate_imgui_bundle/autogenerate_imgui_bundle.py"
python ./lg_projects/lg_imgui_bundle/autogenerate_imgui_bundle/autogenerate_imgui_bundle.py
