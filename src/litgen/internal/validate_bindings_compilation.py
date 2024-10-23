import logging
import sys
import tempfile
import os
import subprocess
import litgen
import shutil


PYTHON_MODULE_NAME = "validate_bindings_compilation"

INCLUDE_NANOBIND = """
#include <memory>
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/trampoline.h>
#include <nanobind/ndarray.h>

namespace py = nanobind;
"""

INCLUDE_PYBIND = """
#include <memory>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
"""

CMAKE_CODE_NANOBIND = f"""
cmake_minimum_required(VERSION 3.18)
project({PYTHON_MODULE_NAME})
set(CMAKE_CXX_STANDARD 17)

find_package(Python 3.8 COMPONENTS Interpreter Development.Module REQUIRED)

# Detect the installed nanobind package and import it into CMake
execute_process(
    COMMAND "${{Python_EXECUTABLE}}" -m nanobind --cmake_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module({PYTHON_MODULE_NAME} code.cpp)
"""

CMAKE_CODE_PYBIND = f"""
cmake_minimum_required(VERSION 3.18)
project({PYTHON_MODULE_NAME})
set(CMAKE_CXX_STANDARD 17)

find_package(Python 3.8 COMPONENTS Interpreter Development.Module REQUIRED)

# Detect the installed pybind11 package and import it into CMake
execute_process(
    COMMAND "${{Python_EXECUTABLE}}" -c
    "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_cmake_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT
    RESULT_VARIABLE _result
)
set(CMAKE_PREFIX_PATH ${{CMAKE_PREFIX_PATH}} "${{pybind11_cmake_dir}}")

find_package(pybind11 CONFIG REQUIRED)
pybind11_add_module({PYTHON_MODULE_NAME} code.cpp)
"""

def validate_bindings_compilation(
        cpp_bound_code: str,
        bind_library_type: litgen.BindLibraryType,
        generated_code: litgen.GeneratedCodes,
        build_dir: str | None = None,
        remove_build_dir_on_success: bool = True,
        remove_build_dir_on_failure: bool = False,
) -> bool:
    """
    Validates that generated bindings correctly compile with standard options.

    :param cpp_bound_code: C++ code that is bound to Python.
    :param bind_library_type: The binding library type (nanobind or pybind11).
    :param generated_code: Generated code (produced by litgen).
    :param build_dir: Directory to build the code in. If None, a temporary directory is created.
                      (warning: if provided, the directory will be deleted and recreated)
    :param remove_build_dir_on_success: If True, the build directory is removed after a successful build.
    :param remove_build_dir_on_failure: If True, the build directory is removed after a failed build.
    :return: True if bindings compile successfully, False otherwise (errors are logged).
    """

    # Select the appropriate include statements and CMake code based on the binding library
    include_bindings = (
        INCLUDE_NANOBIND if bind_library_type == litgen.BindLibraryType.nanobind else INCLUDE_PYBIND
    )
    cmake_code = (
        CMAKE_CODE_NANOBIND if bind_library_type == litgen.BindLibraryType.nanobind else CMAKE_CODE_PYBIND
    )

    # Combine the C++ bound code, include statements, and generated pydef code
    instantiate_module_macro = "NB_MODULE" if bind_library_type == litgen.BindLibraryType.nanobind else "PYBIND11_MODULE"
    full_code = f"""
{cpp_bound_code}

{generated_code.glue_code}

{include_bindings}

{instantiate_module_macro}(validate_bindings_compilation, m)
{{
    {generated_code.pydef_code}
}}
"""

    # Create a temporary directory to hold the code and build files
    if build_dir is None:
        build_dir = tempfile.mkdtemp()
    else:
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        os.mkdir(build_dir)

    try:
        code_cpp_path = os.path.join(build_dir, "code.cpp")
        cmake_lists_path = os.path.join(build_dir, "CMakeLists.txt")

        # Write the full code to code.cpp
        with open(code_cpp_path, "w") as f:
            f.write(full_code)

        # Write the CMake code to CMakeLists.txt
        with open(cmake_lists_path, "w") as f:
            f.write(cmake_code)

        # Write stub file
        os.mkdir(os.path.join(build_dir, PYTHON_MODULE_NAME))
        stub_file = os.path.join(build_dir, PYTHON_MODULE_NAME, "__init__.pyi")
        with open(stub_file, "w") as f:
            f.write(generated_code.stub_code)

        # Compute path to currently running python
        python_executable_path = sys.executable

        # Run CMake to configure the project
        try:
            result_configure = subprocess.run(
                ["cmake", ".", "-DPython_EXECUTABLE=" + python_executable_path],
                cwd=build_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except Exception as e:
            raise RuntimeError("Error running CMake configure") from e

        # Check if CMake configuration was successful
        if result_configure.returncode != 0:
            msg = f"CMake configuration failed with return code {result_configure.returncode}\n"
            msg += f"stdout:\n{result_configure.stdout}\n"
            msg += f"stderr:\n{result_configure.stderr}\n"
            msg += f"Build failed. See temporary directory {build_dir} for details.\n"
            raise RuntimeError(msg)

        # Run CMake to build the project
        try:
            result_build = subprocess.run(
                ["cmake", "--build", "."],
                cwd=build_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except Exception as e:
            raise RuntimeError("Error running CMake build") from e

        # Check if the build was successful
        if result_build.returncode != 0:
            msg = f"CMake build failed with return code {result_build.returncode}\n"
            msg += f"stdout:\n{result_build.stdout}\n"
            msg += f"stderr:\n{result_build.stderr}\n"
            msg += f"Build failed. See build directory {build_dir} for details.\n"
            raise RuntimeError(msg)

    except RuntimeError as e:
        logging.error(e)
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if remove_build_dir_on_failure:
            shutil.rmtree(build_dir)
        return False

    if remove_build_dir_on_success:
        shutil.rmtree(build_dir)

    return True
