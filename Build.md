# Prepare build environment

## Create virtual environment

```bash
python3 -m venv venv       # At least python 3.10
source venv/bin/activate
```

## Install dev requirements

```bash
pip install -r requirements-dev.txt
```

## Activate pre-commit hooks for this repository

```bash
pre-commit install
```

# Build the project

## Install litgen in editable mode

```bash
pip install -v -e .
```

## Install integration test library in editable mode

```bash
cd src/litgen/integration_tests
pip install -v -e .
cd -
```

Then you can also add them as a C++ CMake project.

```
mkdir build && cb build
cmake ..
make
```

(Each time you compile the project, the bindings for the integration tests will be regenerated and recompiled)


## Run tests
```bash
./ci_scripts/devel/run_all_checks.sh
```

(This will run mypy, black, ruff and pytest)

# Misc advices

## Profiling

You can use snakeviz to visualize the profiling results.
http://jiffyclub.github.io/snakeviz/

```bash
pip install snakeviz
python -m cProfile -o profile.prof your_test.py
snakeviz profile.prof
```

## C++ advices
Don't use {} in function default params !!! It is wrongly parsed by srcML.
