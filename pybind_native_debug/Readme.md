This project enables to debug python script using the C++ debugger.
Simply edit `pybind_native_debug.py`, add the code you want to test and run the debugger.

Note: it is recommended to do an editable install before, like this:

````
cd immvision
source venv/bin/activate
cd pybind
pip install -v -e .
````


This way you can modify your C++ code, build it (not pip install), and instantly use it in python.
