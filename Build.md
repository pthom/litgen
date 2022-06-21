
````bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
````

Regularly run [importanize](https://github.com/miki725/importanize), to reorder the imports:
````
cd packages
importanize
````

Remove unused imports via
````
cd packages
zimports . --multi-imports
# Manual check needed after this (+mypy +pytest)
# Re-run of importanize needed after this
````


Use monkeytype to add annotations: https://github.com/Instagram/MonkeyType
