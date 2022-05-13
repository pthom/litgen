import code_replacements
from code_types import *
from options import CodeStyleOptions
import code_utils
import function_generator


def make_struct_doc(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
    doc = f"{struct_infos.struct_code.title_python(options)}\n\n"

    for info in struct_infos.get_attr_and_regions():
        if info.code_region_comment is not None:
            doc = doc + "\n" + info.code_region_comment.comment_python(options) + "\n"
        elif info.attribute is not None:
            attr = info.attribute
            attr_doc = f"{attr.name_python()}:  {attr.type_python(options)}"
            if len(attr.default_value_cpp) > 0:
                attr_doc = attr_doc + " = " + attr.default_value_python(options)

            if len(attr.comment_python(options)) > 0:
                comment_lines = attr.comment_python(options).split("\n")
                comment_lines = map(lambda l: "            " + l, comment_lines)
                comment = "\n".join(comment_lines)
                attr_doc = attr_doc + "\n" + comment
            doc = doc + "    * " + attr_doc + "\n"

    return doc


def generate_python_wrapper_class_code(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
    """
    Should generate a python class that wraps the native code, and looks like this:

class ColorAdjustmentsValues(_cpp_immvision.ColorAdjustmentsValues):
    '''
    {docstring}
    '''
    def __init__(
        self,
        # Pre-multiply values by a Factor before displaying
        factor : float=1.,
        # Add a delta to the values before displaying
        delta: float = 0.
    ):
        _cpp_immvision.ColorAdjustmentsValues.__init__(self)
        self.factor = factor
        self.delta = delta


_cpp_immvision.ColorAdjustmentsValues.__doc__ == "{docstring}"
    """

    struct_name = struct_infos.struct_name()
    docstring = make_struct_doc(struct_infos, options)

    code_intro  = f'''
class {struct_name}(_cpp_immvision.{struct_name}):
    """{docstring}
    """
    
    def __init__(
        self,
'''

    code_inner_param = "        ATTR_NAME_PYTHON: ATTR_TYPE = ATTR_DEFAULT,\n"
    code_outro_1 = f"\n    ):\n        _cpp_immvision.{struct_name}.__init__(self)\n"
    code_inner_set = "        self.ATTR_NAME_PYTHON = ATTR_NAME_PYTHON\n"
    code_outro_2 = f'\n\n'

    def do_replace(s: str, attr: PydefAttribute):
        out = s
        out = out.replace("ATTR_NAME_PYTHON", attr.name_python())
        out = out.replace("ATTR_TYPE", attr.type_python(options))
        out = out.replace("ATTR_DEFAULT", attr.default_value_python(options))
        return out

    def split_comment(comment: str):
        lines = comment.split("\n")
        out = ""
        for line in lines:
            out += "        # " + line + "\n"
        return out

    final_code = code_intro
    for info in struct_infos.get_attr_and_regions():
        if info.attribute is not None:
            attr = info.attribute
            final_code += split_comment(attr.comment_python(options))
            final_code += do_replace(code_inner_param, attr)
    final_code += code_outro_1
    for info in struct_infos.attr_and_regions:
        if info.attribute is not None:
            attr = info.attribute
            final_code += do_replace(code_inner_set, attr)
    final_code += code_outro_2

    return final_code


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


def generate_pyi_python_code(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
    title = code_utils.indent_code(struct_infos.struct_code.title_python(options), 4, skip_first_line=True)
    code_intro = f'''class {struct_infos.struct_name()}:
    """{title}"""
    '''
    attr_inner = """    NAME_PYTHON: TYPE_PYTHON = DEFAULT_VALUE_PYTHON"""
    code_outro = "\n\n"

    r = code_intro + "\n";

    def add_line(l):
        nonlocal r
        r = r + l + "\n"

    for info in struct_infos.get_attr_and_regions():
        if info.code_region_comment is not None:
            add_line("")
            add_line("    #")
            for line in info.code_region_comment.comment_python(options).split("\n"):
                add_line("    # " + line)
            add_line("    #")

        if info.attribute is not None:
            attr = info.attribute
            attr_comment = attr.comment_python(options)
            if len(attr_comment) > 0:
                for line in attr_comment.split("\n"):
                    add_line("    # " + line)
            line = attr_inner
            line = line.replace("NAME_PYTHON", attr.name_python())
            line = line.replace("TYPE_PYTHON", attr.type_python(options))
            line = line.replace("DEFAULT_VALUE_PYTHON", attr.default_value_python(options))
            add_line(line)

        if info.method_infos is not None:
            aux = code_utils.indent_code(info.method_infos.declaration_python(options), 4)
            r = r + aux + "\n"

    r = r + code_outro
    return r


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
