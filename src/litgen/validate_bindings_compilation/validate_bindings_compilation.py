import logging
import sys
import tempfile
import os
import subprocess
import litgen
from codemanip import code_utils
import shutil


def validate_bindings_compilation(
    cpp_code: str,
    options: litgen.LitgenOptions,
    python_test_code: str | None = None,
    python_module_name: str = "validate_bindings_compilation",
    work_dir: str | None = None,
    remove_build_dir_on_success: bool = True,
    remove_build_dir_on_failure: bool = False,
    show_logs: bool = False,
    enable_hack_code: bool = False,
) -> bool:
    """
    Validates that the cpp code can be compiled into bindings and that the generated Python bindings work as expected.
    **This test is slow**, do not use it extensively in CI.

     The process will run in succession:
        - litgen.generate() to generate the bindings code and stubs
        - CMake configure
        - CMake build
        - run pytest

    :param cpp_code: C++ code that is bound to Python.
    :param options: Options for the code generation.
    :param python_test_code: If provided, run this test code via pytest after successful build.
    :param python_module_name: Name of the Python module to create.
                               (a native module with "_" + same name will be created and imported in the Python module)
    :param work_dir: Directory to build the code in. If None, a temporary directory is created.
                      (warning: if provided, the directory will be deleted and recreated)
    :param remove_build_dir_on_success: If True, the build directory is removed after a successful build.
    :param remove_build_dir_on_failure: If True, the build directory is removed after a failed build.
    :param show_logs: If True, show CMake and build logs in the console.
    :return: True if bindings compile and tests pass successfully, False otherwise (errors are logged).
    """

    python_native_module_name = "_" + python_module_name

    INCLUDE_NANOBIND = """
#include <memory>
#include <array>
#include <vector>
#include <tuple>
#include <nanobind/nanobind.h>
#include <nanobind/trampoline.h>
#include <nanobind/stl/array.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/function.h>
#include <nanobind/stl/shared_ptr.h>
#include <nanobind/stl/unique_ptr.h>
#include <nanobind/stl/map.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/make_iterator.h>
#include <nanobind/ndarray.h>
#include <nanobind/trampoline.h>
#include <nanobind/ndarray.h>

namespace nb = nanobind;
"""

    INCLUDE_PYBIND = """
#include <memory>
#include <array>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>

namespace py = pybind11;
"""

    CMAKE_CODE_NANOBIND = f"""
cmake_minimum_required(VERSION 3.18)
project({python_module_name})
set(CMAKE_CXX_STANDARD 17)

find_package(Python 3.8 COMPONENTS Interpreter Development.Module REQUIRED)

# Detect the installed nanobind package and import it into CMake
execute_process(
    COMMAND "${{Python_EXECUTABLE}}" -m nanobind --cmake_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module({python_native_module_name} code.cpp)

# Copy PYTHON_NATIVE_MODULE_NAME target output to source dir
add_custom_command(TARGET {python_native_module_name}
    POST_BUILD
    COMMAND ${{CMAKE_COMMAND}} -E copy $<TARGET_FILE:{python_native_module_name}> ${{CMAKE_SOURCE_DIR}}
)
"""

    CMAKE_CODE_PYBIND = f"""
cmake_minimum_required(VERSION 3.18)
project({python_module_name})
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
pybind11_add_module({python_native_module_name} code.cpp)

# Copy PYTHON_NATIVE_MODULE_NAME target output to source dir
add_custom_command(TARGET {python_native_module_name}
    POST_BUILD
    COMMAND ${{CMAKE_COMMAND}} -E copy $<TARGET_FILE:{python_native_module_name}> ${{CMAKE_SOURCE_DIR}}
)

"""

    generated_code = litgen.generate_code(options, cpp_code)

    # Select the appropriate include statements and CMake code based on the binding library
    include_bindings = INCLUDE_NANOBIND if options.bind_library == litgen.BindLibraryType.nanobind else INCLUDE_PYBIND
    cmake_code = CMAKE_CODE_NANOBIND if options.bind_library == litgen.BindLibraryType.nanobind else CMAKE_CODE_PYBIND

    # Combine the C++ bound code, include statements, and generated pydef code
    instantiate_module_macro = (
        "NB_MODULE" if options.bind_library == litgen.BindLibraryType.nanobind else "PYBIND11_MODULE"
    )
    full_code = f"""
{code_utils.unindent_code(cpp_code)}

{include_bindings}

{generated_code.glue_code}

{instantiate_module_macro}({python_native_module_name}, m)
{{
    {generated_code.pydef_code}
}}
"""

    # Create a temporary directory to hold the code and build files
    if work_dir is None:
        work_dir = tempfile.mkdtemp()
    else:
        if not enable_hack_code:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)
            os.mkdir(work_dir)
    build_dir = os.path.join(work_dir, "build")
    os.makedirs(build_dir, exist_ok=True)

    try:
        code_cpp_path = os.path.join(work_dir, "code.cpp")
        cmake_lists_path = os.path.join(work_dir, "CMakeLists.txt")

        # Write the full code to code.cpp
        if not enable_hack_code:
            with open(code_cpp_path, "w") as f:
                f.write(full_code)

        # Write the CMake code to CMakeLists.txt
        with open(cmake_lists_path, "w") as f:
            f.write(cmake_code)

        # Write stub files and initialize the module directory
        module_dir = os.path.join(work_dir, python_module_name)
        os.makedirs(module_dir, exist_ok=True)
        stub_file = os.path.join(module_dir, "__init__.pyi")
        with open(stub_file, "w") as f:
            f.write(generated_code.stub_code)
        init_file = os.path.join(module_dir, "__init__.py")
        with open(init_file, "w") as f:
            # Import everything from the native submodule
            f.write(f"from {python_native_module_name} import *")

        # Compute path to currently running python
        python_executable_path = sys.executable

        # Run CMake to configure the project
        try:
            result_configure = subprocess.run(
                ["cmake", "..", "-DCMAKE_BUILD_TYPE=Release", f"-DPython_EXECUTABLE={python_executable_path}"],
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
            msg += f"Build failed. See temporary directory {work_dir} for details.\n"
            raise RuntimeError(msg)
        else:
            if show_logs:
                print("CMake configuration stdout:")
                print(result_configure.stdout)
                print("CMake configuration stderr:")
                print(result_configure.stderr)

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
            msg += f"Build failed. See build directory {work_dir} for details.\n"
            raise RuntimeError(msg)
        else:
            if show_logs:
                print("CMake build stdout:")
                print(result_build.stdout)
                print("CMake build stderr:")
                print(result_build.stderr)

        # Run python tests if provided
        # The module was built in the work_dir, it can be imported directly (no need to move it)
        if python_test_code:
            # Write test code to a test file
            test_file_name = "run_validate_bindings_compilation.py"
            test_file_path = os.path.join(work_dir, test_file_name)
            with open(test_file_path, "w") as f:
                f.write(code_utils.unindent_code(python_test_code))

            # Run pytest on the test file
            try:
                result_test = subprocess.run(
                    [sys.executable, "-m", "pytest", test_file_path],
                    cwd=work_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except Exception as e:
                raise RuntimeError("Error running pytest") from e

            # Check if the test was successful
            if result_test.returncode != 0:
                msg = f"Pytest failed with return code {result_test.returncode}\n"
                msg += f"stdout:\n{result_test.stdout}\n"
                msg += f"stderr:\n{result_test.stderr}\n"
                msg += f"Tests failed. See build directory {work_dir} for details.\n"
                raise RuntimeError(msg)
            else:
                if show_logs:
                    print("Pytest stdout:")
                    print(result_test.stdout)
                    print("Pytest stderr:")
                    print(result_test.stderr)

    except RuntimeError as e:
        logging.error(e)
        if remove_build_dir_on_failure:
            shutil.rmtree(work_dir)
        return False
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        if remove_build_dir_on_failure:
            shutil.rmtree(work_dir)
        return False

    if remove_build_dir_on_success:
        shutil.rmtree(work_dir)

    return True
