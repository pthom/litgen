# CMake helpers

Building python bindings, and ensuring that they build on all platforms can be challenging.

You can use the [lg_skbuild_template template repository](https://github.com/pthom/lg_skbuild_template) as a starting point.

This template repository provides:

* A template which you can customize: change the name of the C++ library, and the name of the python module, as well as the name of the pypi module
* Build systems for pip, conda and wheels, tested on windows, linux and macOS
