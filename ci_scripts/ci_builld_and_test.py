import os
import chain_commands

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.realpath(THIS_DIR + "/..")

cmd = f"""

# Create virtual env
cd {REPO_DIR}
python3 -m venv venv_ci
. venv_ci/bin/activate 
which python

# install requirements
cd {REPO_DIR}
pip install -r requirements-dev.txt
pip install -r requirements.txt

# install litgen
cd {REPO_DIR}
pip install -v .

# Run srcmlcpp tests
cd {REPO_DIR}/srcmlcpp
pytest

# Run litgen tests
cd {REPO_DIR}/litgen
pytest

# Build example
cd {REPO_DIR}/example
pip install -v .

# Test example
python -c "import litgensample; print(litgensample.add(59, 41));"

"""

chain_commands.chain_commands(cmd)
