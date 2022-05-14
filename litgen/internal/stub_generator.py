import code_replacements
from code_types import *
from options import CodeStyleOptions
import code_utils
import function_generator
import copy
from function_wrapper_lambda import is_buffer_size_name_at_idx, is_param_variadic_format, _is_param_buffer_at_idx_template_or_not


def _indent_spacing(indent_level: int, options: CodeStyleOptions):
    return " " * indent_level * options.indent_size_python


def _py_layout_comment(comment, indent_level: int, options: CodeStyleOptions,
                       nb_empty_comment_lines_around: int = 0, nb_empty_lines_around: int = 0) -> List[str]:
    r = []
    spacing = _indent_spacing(indent_level, options)
    for i in range(nb_empty_lines_around):
        r.append("")
    for i in range(nb_empty_comment_lines_around):
        r.append(spacing + "#")
    for line in comment.split("\n"):
        r.append(spacing + "# " + line)
    for i in range(nb_empty_comment_lines_around):
        r.append(spacing + "#")
    for i in range(nb_empty_lines_around):
        r.append("")
    return r


def _py_layout_region_comment(comment, indent_level: int, options: CodeStyleOptions ) -> List[str]:
    return _py_layout_comment(comment, indent_level, options, nb_empty_comment_lines_around=1, nb_empty_lines_around=1)


def _py_layout_title(title: str, indent_level: int, options: CodeStyleOptions) -> List[str]:
    lines = title.splitlines(keepends=False)
    spacing = _indent_spacing(indent_level, options)
    if len(lines) == 0:
        return [spacing + '""""""']
    r = []
    r.append(spacing + '"""' + lines[0])
    for line in lines[1:]:
        r.append(spacing + line)
    r.append(spacing + '"""')
    return r


def _py_dump_attr(attr: PydefAttribute, indent_level: int, options: CodeStyleOptions) -> List[str]:
    spacing = _indent_spacing(indent_level, options)

    comment_lines = _py_layout_comment(attr.comment_python(options), indent_level, options)

    attr_decl_line = spacing + """NAME_PYTHON: TYPE_PYTHON DEFAULT_VALUE_PYTHON"""
    attr_decl_line = attr_decl_line.replace("NAME_PYTHON", attr.name_python())
    attr_decl_line = attr_decl_line.replace("TYPE_PYTHON", attr.type_python(options))
    if len(attr.default_value_python(options)) > 0:
        attr_decl_line = attr_decl_line.replace("DEFAULT_VALUE_PYTHON", " = " + attr.default_value_python(options))
    else:
        attr_decl_line = attr_decl_line.replace("DEFAULT_VALUE_PYTHON", "")

    return comment_lines + [attr_decl_line]


def _py_filter_function_args(function_infos: FunctionsInfos, options: CodeStyleOptions) -> List[PydefAttribute]:
    out_params: List[PydefAttribute] = []
    initial_params = function_infos.get_parameters()
    for idx_param, param in enumerate(initial_params):
        if is_buffer_size_name_at_idx(initial_params, options, idx_param):
            continue
        if  is_param_variadic_format(initial_params, options, idx_param):
            continue
        if _is_param_buffer_at_idx_template_or_not(initial_params, options, idx_param):
            param_copy = copy.deepcopy(param)
            param_copy.type_cpp = "py::array"
            out_params.append(param_copy)
            continue

        out_params.append(param)

    return out_params


def py_function_declaration(function: FunctionsInfos, options: CodeStyleOptions) -> str:
    params_str = function.params_declaration_str_python(options)
    code = f"def {function.function_name_python(options)}({params_str})"
    if len(function.return_type_python(options)) > 0:
        code += " -> " + function.return_type_python(options)
    code += ":"
    return code


def _py_dump_function(function: FunctionsInfos, indent_level: int, options: CodeStyleOptions):
    spacing = _indent_spacing(indent_level, options)
    function_params_filtered = copy.deepcopy(function)
    function_params_filtered.parameters = _py_filter_function_args(function_params_filtered, options)

    declaration_line =  spacing + py_function_declaration(function_params_filtered, options)
    title = function.function_code.title_python(options)

    return [declaration_line] +_py_layout_title(title, indent_level + 1, options) + [""]


def _py_dump_method(struct_name: str, method: FunctionsInfos, indent_level: int, options: CodeStyleOptions):
    # skip destructors
    if method.function_name_cpp() == "~" + struct_name:
        return []
    # process constructors
    if method.function_name_cpp() == struct_name:
        method = copy.deepcopy(method)
        method.function_code.name_cpp = "__init__"

    if code_utils.contains_word(method.function_code.declaration_line, "static"):
        is_static_method = True
    else:
        is_static_method = False

    if not is_static_method:
        method = copy.deepcopy(method)
        self_param = PydefAttribute(name_cpp="self")
        method.parameters = [self_param] + method.parameters

    method_code_lines = _py_dump_function(method, indent_level, options)

    if is_static_method:
        method_code_lines = ["    @staticmethod"] + method_code_lines

    return method_code_lines


def generate_struct_stub(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
    code_lines = []

    code_lines.append(f"class {struct_infos.struct_name()}:")

    title = struct_infos.struct_code.title_python(options)
    code_lines += _py_layout_title(title, indent_level=1, options=options)

    for info in struct_infos.get_attr_and_regions():
        if info.code_region_comment is not None:
            code_lines += _py_layout_region_comment(
                                    info.code_region_comment.comment_python(options),
                                    indent_level=1, options=options)
        if info.attribute is not None:
            code_lines += _py_dump_attr(info.attribute, indent_level=1, options=options)
        if info.method_infos is not None:
            code_lines += _py_dump_method(struct_infos.struct_name(), info.method_infos, indent_level=1, options=options)

    code_lines += ["", ""]
    code = "\n".join(code_lines)
    return code


def generate_function_stub(function_infos: FunctionsInfos, options: CodeStyleOptions) -> str:
    code_lines = []
    code_lines += _py_dump_function(function_infos, indent_level=0, options=options)
    code = "\n".join(code_lines)
    return code


################# Oldies

def oldie_make_struct_doc(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
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


def oldie_generate_python_wrapper_class_code(struct_infos: StructInfos, options: CodeStyleOptions) -> str:
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

