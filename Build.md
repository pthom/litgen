
````bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
````

Regularly run [importanize](https://github.com/miki725/importanize), to reorder the imports:

Install importanize (from master branch, in submodule)
````
cd ci_scripts/importanize
pip install -v -e .
cd -
````

Run importanize
````
# From repository root
importanize
````


Profiling
    http://jiffyclub.github.io/snakeviz/

        pip install snakeviz
        python -m cProfile -o profile.prof internal/srcml_types_parse_test.py
        snakeviz profile.prof


Add annotations
    Use monkeytype: https://github.com/Instagram/MonkeyType
