# Install requirement and create venv

Install global pre-commit
```
python3 -m pip install pre-commit
```

Install poetry: https://python-poetry.org/docs/#installation

```
curl -sSL https://install.python-poetry.org | python3 -
```


```bash
poetry shell
poetry install
pre-commit install
```


### Update requirements.txt

```
poetry export --without-hashes --dev > requirements.txt
```


# Build the pip modules

```
pip install -v -e .
cd example
pip install -v -e .
cd -
cd examples_real_libs/imgui
pip install -v -e .
cd -
```

# Tests & Sanity check
```
mypy .
black .
pytest
```

# Advices

Don't use {} in function default params !!! It is wrongly parsed by srcML.

# Importanize
Regularly run [importanize](https://github.com/miki725/importanize), to reorder the imports:

Install importanize (from master branch, in submodule)
```
cd ci_scripts
git clone https://github.com/miki725/importanize.git
cd importanize
pip install -v -e .
cd -
```

Run importanize
```
# From repository root
importanize
```

# Profiling
    http://jiffyclub.github.io/snakeviz/

        pip install snakeviz
        python -m cProfile -o profile.prof internal/srcml_types_parse_test.py
        snakeviz profile.prof


# Add annotations
    Use monkeytype: https://github.com/Instagram/MonkeyType
