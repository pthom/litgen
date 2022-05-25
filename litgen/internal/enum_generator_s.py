from code_types import *
from options import CodeStyleOptions
import code_utils
import cpp_to_python


def generate_pydef_enum_cpp_98(enum_infos: EnumCpp98Infos, options: CodeStyleOptions) -> str:
    enum_name = enum_infos.enum_name()

    code_intro = f'    py::enum_<{enum_name}>(m, "{enum_name}", py::arithmetic(),\n'
    comment = cpp_to_python.docstring_python_one_line(enum_infos.enum_code.docstring_cpp, options)
    code_intro += f'        "{comment}")\n'
    code_inner = f'        .value("ATTR_NAME_PYTHON", ATTR_NAME_CPP, "(ATTR_COMMENT)")\n'
    code_outro = "    ;\n\n"
    final_code = code_intro

    def make_value_code(enum_value: PydefEnumCpp98Value):
        code = code_inner
        code = code.replace("ATTR_NAME_PYTHON", enum_value.name_python)
        code = code.replace("ATTR_NAME_CPP", enum_value.name_cpp)
        code = code.replace("ATTR_COMMENT", code_utils.format_cpp_comment_on_one_line(enum_value.docstring_cpp))
        return code

    for info in enum_infos.get_attr_and_regions():
        if info.code_region_comment is not None:
            final_code += f"        // {info.code_region_comment.docstring_cpp}\n"
        if info.enum_cpp_98_value is not None:
            final_code = final_code + make_value_code(info.enum_cpp_98_value)
    final_code = final_code + code_outro
    return final_code

