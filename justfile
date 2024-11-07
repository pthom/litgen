# List all available commands
default:
    just --list

# install dev requirements
install_requirements_dev:
    pip install -r requirements-dev.txt

# install litgen in editable mode
install_litgen_editable:
    pip install --verbose  -e .

# run black formatter
black:
    black .

# Builds the integration tests for pybind
build_integration_tests_pybind:
    python src/litgen/integration_tests/autogenerate_mylib.py no_generate_file_by_file pybind
    export LITGEN_USE_NANOBIND=OFF && cd src/litgen/integration_tests &&  pip install -v -e . && cd -
    python -m lg_mylib.use pybind
    python -c "import lg_mylib._lg_mylib_pybind"

# Builds the integration tests for nanobind
build_integration_tests_nanobind:
    python src/litgen/integration_tests/autogenerate_mylib.py no_generate_file_by_file nanobind
    export LITGEN_USE_NANOBIND=ON && cd src/litgen/integration_tests &&  pip install -v -e . && cd -
    python -m lg_mylib.use nanobind
    python -c "import lg_mylib._lg_mylib_nanobind"

# Runs all tests for pybind, after building the integration tests
integration_tests_pybind: build_integration_tests_pybind
    just pytest pybind

# Runs all tests for nanobind, after building the integration tests
integration_tests_nanobind: build_integration_tests_nanobind
    just pytest nanobind

# Runs all tests for pybind and nanobind (after building the integration tests)
integration_tests:
    just integration_tests_pybind
    just integration_tests_nanobind

# Just runs pytest (requires that the integration tests have been built)
pytest binding_type:
    python -m lg_mylib.use {{binding_type}}
    pytest

# Runs mypy on the top level folder (see mypy.ini)
mypy:
    mypy .

# Build documentation
docs:
    ./litgen-book/generate_litgen_book.sh
