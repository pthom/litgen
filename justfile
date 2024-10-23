default:
    just --list


build_integration_tests:
    python src/litgen/integration_tests/autogenerate_mylib.py
    cd src/litgen/integration_tests &&  pip install -v -e . && cd -
    python -c "import lg_mylib"


integration_tests: build_integration_tests
    # Runs all tests, after building the integration tests
    pytest


pytest:
    # Will not build the integration tests!
    pytest

mypy:
    # Runs mypy on the top level folder (see mypy.ini)
    mypy .
