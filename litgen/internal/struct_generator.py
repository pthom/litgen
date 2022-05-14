import code_replacements
from code_types import *
from options import CodeStyleOptions
import code_utils
import function_generator
import copy


def generate_pydef_struct_cpp_code(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
    classes_with_leaked_ptr = ["ImPlotStyle"]

    struct_name = struct_infos.struct_name()
    struct_name_possibly_leaked = struct_name
    if struct_name in classes_with_leaked_ptr:
        struct_name_possibly_leaked = f"{struct_name}, leaked_ptr<{struct_name}>"

    code_intro  = f'auto pyClass{struct_name} = py::class_<{struct_name_possibly_leaked}>\n    (m, "{struct_name}", \n'
    comment = code_utils.format_cpp_comment_on_one_line(struct_infos.struct_code.title_python(options))
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
            code = code.replace("ATTR_NAME_PYTHON", attr.name_python())
            code = code.replace("ATTR_NAME_CPP", attr.name_cpp)
            code = code.replace("ATTR_COMMENT", code_utils.escape_new_lines(attr.comment_python(options)))
            r = r + code
        if info.code_region_comment is not None:
            r = r + info.code_region_comment.as_multiline_cpp_comment(4) + "\n"
        if info.method_infos is not None:
            r = r + function_generator.generate_pydef_method_cpp_code(info.method_infos, options, struct_name)
    r = r + code_outro

    r = code_utils.indent_code(r, 4)

    return r


def generate_tostring_cpp_code(struct_infos: StructInfos, code_style_options: CodeStyleOptions) -> str:
    code_intro = f'''
    std::string ToString(const {struct_infos.struct_name()}& v)
    {{

        using namespace ImmVision::StringUtils;
        
        std::string r;
        r += "{struct_infos.struct_name()}\\n";
        r += "{{\\n";
    
        std::string inner;
'''

    code_inner = '        inner = inner + "ATTR_NAME: " + ToString(v.ATTR_NAME_CPP) + "\\n";'

    code_outro = f'''
        r = r + IndentLines(inner, 4);
        r += "}}";
        return r;
    }}
    '''

    def dump_attributes(is_python: bool):
        code = ""
        for info in struct_infos.get_attr_and_regions():
            if info.attribute is not None:
                #         r = r + MakeIndent(indent_size) + "ColorAdjustments: " + ToString(v.ColorAdjustments) + "\n";
                attr = info.attribute
                line = code_inner
                line = line.replace("ATTR_NAME_CPP", attr.name_cpp)
                if is_python:
                    line = line.replace("ATTR_NAME", attr.name_python())
                else:
                    line = line.replace("ATTR_NAME", attr.name_cpp)
                code = code + line + "\n"
        return code

    r = ""
    r += code_intro + "\n"
    r += "#ifdef IMMVISION_BUILD_PYTHON_BINDINGS\n"
    r += "\n"
    r += dump_attributes(True)
    r += "\n"
    r += "#else // #ifdef IMMVISION_BUILD_PYTHON_BINDINGS\n"
    r += "\n"
    r += dump_attributes(False)
    r += "\n"
    r += "#endif // #ifdef IMMVISION_BUILD_PYTHON_BINDINGS\n"

    r = r + code_outro
    return r


def generate_tostring_decl_h(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
    return f"    std::string ToString(const {struct_infos.struct_name()}& params);\n"

