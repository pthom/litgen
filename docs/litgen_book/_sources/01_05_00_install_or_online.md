# Installation or online usage

You can either use litgen online, or install it locally.

## Use litgen online

You do not to install anything. Simply:
1. Set some conversion options
2. Paste the API of the code for which you want to generate bindings
3. Generate the binding code (C++ and python stubs), which you can then copy and paste into your project.

[Access the online tool](https://mybinder.org/v2/gh/pthom/litgen/main?urlpath=lab/tree/litgen-book/01_05_05_online.ipynb)

## Install litgen locally

If installing locally, you can integrate liten into your building process, and it can generate full C++ bindings files, as well as python stubs (API documentation and declaration).

Install litgen with pip:
```bash
pip install "litgen@git+https://github.com/pthom/litgen"
```

Then, follow the instructions in [Quickstart with litgen](litgen_template/README) section.
