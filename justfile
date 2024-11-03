# List all available commands
default:
    just --list


# Builds the integration tests for pybind
build_integration_tests_pybind:
    python src/litgen/integration_tests/autogenerate_mylib.py no_generate_file_by_file pybind
    export LITGEN_USE_NANOBIND=OFF && cd src/litgen/integration_tests &&  pip install -v -e . && cd -
    python -c "import lg_mylib"

# Builds the integration tests for nanobind
build_integration_tests_nanobind:
    python src/litgen/integration_tests/autogenerate_mylib.py no_generate_file_by_file nanobind
    export LITGEN_USE_NANOBIND=ON && cd src/litgen/integration_tests &&  pip install -v -e . && cd -
    python -c "import lg_mylib"


# Runs all tests for pybind, after building the integration tests
integration_tests_pybind: build_integration_tests_pybind
    pytest

# Runs all tests for nanobind, after building the integration tests
integration_tests_nanobind: build_integration_tests_nanobind
    pytest

# Runs all tests for pybind and nanobind (after building the integration tests)
integration_tests:
    just integration_tests_pybind
    just integration_tests_nanobind


# Just runs pytest (requires that the integration tests have been built)
pytest:
    pytest


# Runs mypy on the top level folder (see mypy.ini)
mypy:
    mypy .
