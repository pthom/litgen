import code_replacements
from code_types import *
from options import CodeStyleOptions
import code_utils, cpp_to_python
import function_generator
import copy


def generate_pydef_struct_cpp_code(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
    struct_name = struct_infos.struct_name()
    code_intro  = f'auto pyClass{struct_name} = py::class_<{struct_name}>\n    (m, "{struct_name}", \n'
    comment = cpp_to_python.docstring_python_one_line(struct_infos.struct_code.docstring_cpp, options)
    code_intro += f'    "{comment}")\n\n'
    code_intro += f'    .def(py::init<>()) \n'  # Yes, we require struct to be default constructible!

    code_inner_attribute  = f'    .def_readwrite("ATTR_NAME_PYTHON", &{struct_name}::ATTR_NAME_CPP, "ATTR_COMMENT")\n'

    if options.generate_to_string:
        code_outro  = f'    .def("__repr__", [](const {struct_name}& v) {{ return ToString(v); }}); \n\n'
    else:
        code_outro  = f'    ; \n\n'

    r = code_intro
    for info in struct_infos.get_attr_and_regions():
        if info.attribute is not None:
            attr = info.attribute
            code = code_inner_attribute
            code = code.replace("ATTR_NAME_PYTHON",  cpp_to_python.var_name_to_python(attr.name_cpp, options))
            code = code.replace("ATTR_NAME_CPP", attr.name_cpp)
            code = code.replace("ATTR_COMMENT", cpp_to_python.docstring_python_one_line(attr.docstring_cpp, options))
            r = r + code
        if info.code_region_comment is not None:
            r = r + code_utils.format_cpp_comment_multiline(info.code_region_comment.docstring_cpp, 4) + "\n"
        if info.method_infos is not None:
            r = r + function_generator.generate_pydef_method_cpp_code(info.method_infos, options, struct_name)
    r = r + code_outro

    r = code_utils.indent_code(r, 4)

    return r
