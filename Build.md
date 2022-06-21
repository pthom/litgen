
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



Use monkeytype to add annotations: https://github.com/Instagram/MonkeyType
