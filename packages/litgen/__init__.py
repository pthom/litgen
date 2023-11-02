from litgen.options import LitgenOptions

from litgen.code_to_adapted_unit import code_to_adapted_unit
from litgen.internal.cpp_to_python import (
    standard_type_replacements,
    standard_value_replacements,
    opencv_replacements,
    standard_comment_replacements,
)
from litgen.litgen_generator import (
    LitgenGenerator,
    GeneratedCodes,
    write_generated_code_for_files,
    write_generated_code_for_file,
    generate_code,
    generate_code_for_file,
)

__all__ = [
    # Main API
    "LitgenOptions",
    "generate_code",
    "code_to_adapted_unit",
    "TemplateNamingScheme",
    "write_generated_code_for_file",
    "write_generated_code_for_files",
    # When it is needed to have different options per c++ header file
    "LitgenGenerator",
    "GeneratedCodes",
    "generate_code_for_file",
    # Configure replacements
    "standard_type_replacements",
    "opencv_replacements",
    "standard_comment_replacements",
]
