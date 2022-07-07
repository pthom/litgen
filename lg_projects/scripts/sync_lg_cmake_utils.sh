SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

set -e  # Exit on error
#set -x  # Trace commands

LG_PROJECTS_DIR=$SCRIPT_DIR/..

for project in lg_*; do
  echo $project;
  cd $LG_PROJECTS_DIR
  cd $project/lg_cmake_utils
  git pull
  cd ..
  git add lg_cmake_utils
  (git commit -m "update lg_cmake_utils" && git push) || true
done
