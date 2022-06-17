# import code_replacements
# from code_types import *
# from options import LitgenOptions
# import code_utils, cpp_to_python
# import function_generator
# import copy
# from function_wrapper_lambda import (
#     is_buffer_size_name_at_idx,
#     is_param_variadic_format,
#     _is_param_buffer_at_idx_template_or_not,
# )
#
#
# def _indent_spacing(indent_level: int, options: LitgenOptions):
#     return " " * indent_level * options.python_indent_size
#
#
# def _py_layout_comment(
#     comment,
#     indent_level: int,
#     options: LitgenOptions,
#     nb_empty_comment_lines_around: int = 0,
#     nb_empty_lines_around: int = 0,
# ) -> List[str]:
#     r = []
#     spacing = _indent_spacing(indent_level, options)
#     for i in range(nb_empty_lines_around):
#         r.append("")
#     for i in range(nb_empty_comment_lines_around):
#         r.append(spacing + "#")
#     for line in comment.split("\n"):
#         r.append(spacing + "# " + line)
#     for i in range(nb_empty_comment_lines_around):
#         r.append(spacing + "#")
#     for i in range(nb_empty_lines_around):
#         r.append("")
#     return r
#
#
# def _py_layout_region_comment(comment, indent_level: int, options: LitgenOptions) -> List[str]:
#     return _py_layout_comment(
#         comment,
#         indent_level,
#         options,
#         nb_empty_comment_lines_around=1,
#         nb_empty_lines_around=1,
#     )
#
#
# def _py_layout_title(title: str, indent_level: int, options: LitgenOptions) -> List[str]:
#     lines = title.splitlines(keepends=False)
#     spacing = _indent_spacing(indent_level, options)
#     if len(lines) == 0:
#         return [spacing + '""""""']
#     r = []
#     r.append(spacing + '"""' + lines[0])
#     for line in lines[1:]:
#         r.append(spacing + line)
#     r.append(spacing + '"""')
#     return r
#
#
# def _py_dump_attr(attr: PydefAttribute, indent_level: int, options: LitgenOptions) -> List[str]:
#     spacing = _indent_spacing(indent_level, options)
#
#     comment_python = cpp_to_python.docstring_python(attr.docstring_cpp, options)
#     comment_lines = _py_layout_comment(comment_python, indent_level, options)
#
#     attr_decl_line = spacing + """NAME_PYTHON: TYPE_PYTHON DEFAULT_VALUE_PYTHON"""
#     attr_decl_line = attr_decl_line.replace("NAME_PYTHON", cpp_to_python.var_name_to_python(attr.name_cpp, options))
#     attr_decl_line = attr_decl_line.replace("TYPE_PYTHON", cpp_to_python.type_to_python(attr.type_cpp, options))
#
#     default_value_python = cpp_to_python.default_value_to_python(attr.default_value_cpp, options)
#     if len(default_value_python) > 0:
#         attr_decl_line = attr_decl_line.replace("DEFAULT_VALUE_PYTHON", " = " + default_value_python)
#     else:
#         attr_decl_line = attr_decl_line.replace("DEFAULT_VALUE_PYTHON", "")
#
#     return comment_lines + [attr_decl_line]
#
#
# def _py_filter_function_args(function_infos: FunctionsInfos, options: LitgenOptions) -> List[PydefAttribute]:
#     out_params: List[PydefAttribute] = []
#     initial_params = function_infos.get_parameters()
#     for idx_param, param in enumerate(initial_params):
#         if is_buffer_size_name_at_idx(initial_params, options, idx_param):
#             continue
#         if is_param_variadic_format(initial_params, options, idx_param):
#             continue
#         if _is_param_buffer_at_idx_template_or_not(initial_params, options, idx_param):
#             param_copy = copy.deepcopy(param)
#             param_copy.type_cpp = "py::array"
#             out_params.append(param_copy)
#             continue
#
#         out_params.append(param)
#
#     return out_params
#
#
# def py_function_declaration(function_infos: FunctionsInfos, options: LitgenOptions) -> str:
#     function_name_python = cpp_to_python.function_name_to_python(function_infos.function_name_cpp(), options)
#     params_str = cpp_to_python.attrs_python_name_type_default(function_infos.get_parameters(), options)
#     return_type_python = cpp_to_python.type_to_python(function_infos.return_type_cpp(), options)
#
#     code = f"def {function_name_python}({params_str})"
#     if len(return_type_python) > 0:
#         code += " -> " + return_type_python
#     code += ":"
#     return code
#
#
# def _py_dump_function(function: FunctionsInfos, indent_level: int, options: LitgenOptions):
#     spacing = _indent_spacing(indent_level, options)
#     function_params_filtered = copy.deepcopy(function)
#     function_params_filtered.parameters = _py_filter_function_args(function_params_filtered, options)
#
#     declaration_line = spacing + py_function_declaration(function_params_filtered, options)
#     title = cpp_to_python.docstring_python(function.function_code.docstring_cpp, options)
#
#     return [declaration_line] + _py_layout_title(title, indent_level + 1, options) + [""]
#
#
# def _py_dump_method(
#     struct_name: str,
#     method: FunctionsInfos,
#     indent_level: int,
#     options: LitgenOptions,
# ):
#     # skip destructors
#     if method.function_name_cpp() == "~" + struct_name:
#         return []
#     # process constructors
#     if method.function_name_cpp() == struct_name:
#         method = copy.deepcopy(method)
#         method.function_code.name_cpp = "__init__"
#
#     if code_utils.contains_word(method.function_code.declaration_line, "static"):
#         is_static_method = True
#     else:
#         is_static_method = False
#
#     if not is_static_method:
#         method = copy.deepcopy(method)
#         self_param = PydefAttribute(name_cpp="self")
#         method.parameters = [self_param] + method.parameters
#
#     method_code_lines = _py_dump_function(method, indent_level, options)
#
#     if is_static_method:
#         method_code_lines = ["    @staticmethod"] + method_code_lines
#
#     return method_code_lines
#
#
# def generate_struct_stub(struct_infos: StructInfos, options: LitgenOptions) -> str:
#     code_lines = []
#
#     code_lines.append(f"class {struct_infos.struct_name()}:")
#
#     title = cpp_to_python.docstring_python(struct_infos.struct_code.docstring_cpp, options)
#     code_lines += _py_layout_title(title, indent_level=1, options=options)
#
#     for info in struct_infos.get_attr_and_regions():
#         if info.code_region_comment is not None:
#             code_lines += _py_layout_region_comment(
#                 cpp_to_python.docstring_python(info.code_region_comment.docstring_cpp, options),
#                 indent_level=1,
#                 options=options,
#             )
#         if info.attribute is not None:
#             code_lines += _py_dump_attr(info.attribute, indent_level=1, options=options)
#         if info.method_infos is not None:
#             code_lines += _py_dump_method(
#                 struct_infos.struct_name(),
#                 info.method_infos,
#                 indent_level=1,
#                 options=options,
#             )
#
#     code_lines += ["", ""]
#     code = "\n".join(code_lines)
#     return code
#
#
# def generate_function_stub(function_infos: FunctionsInfos, options: LitgenOptions) -> str:
#     code_lines = []
#     code_lines += _py_dump_function(function_infos, indent_level=0, options=options)
#     code = "\n".join(code_lines)
#     return code
#
#
# ################# Oldies
#
#
# def oldie_generate_python_wrapper_class_code(struct_infos: StructInfos, options: LitgenOptions) -> str:
#     """
#         Should generate a python class that wraps the native code, and looks like this:
#
#     class ColorAdjustmentsValues(_cpp_immvision.ColorAdjustmentsValues):
#         '''
#         {docstring}
#         '''
#         def __init__(
#             self,
#             # Pre-multiply values by a Factor before displaying
#             factor : float=1.,
#             # Add a delta to the values before displaying
#             delta: float = 0.
#         ):
#             _cpp_immvision.ColorAdjustmentsValues.__init__(self)
#             self.factor = factor
#             self.delta = delta
#
#
#     _cpp_immvision.ColorAdjustmentsValues.__doc__ == "{docstring}"
#     """
#
#     struct_name = struct_infos.struct_name()
#     docstring = make_struct_doc(struct_infos, options)
#
#     code_intro = f'''
# class {struct_name}(_cpp_immvision.{struct_name}):
#     """{docstring}
#     """
#
#     def __init__(
#         self,
# '''
#
#     code_inner_param = "        ATTR_NAME_PYTHON: ATTR_TYPE = ATTR_DEFAULT,\n"
#     code_outro_1 = f"\n    ):\n        _cpp_immvision.{struct_name}.__init__(self)\n"
#     code_inner_set = "        self.ATTR_NAME_PYTHON = ATTR_NAME_PYTHON\n"
#     code_outro_2 = f"\n\n"
#
#     def do_replace(s: str, attr: PydefAttribute):
#         out = s
#         out = out.replace("ATTR_NAME_PYTHON", cpp_to_python.var_name_to_python(attr.name_cpp, options))
#         out = out.replace("ATTR_TYPE", cpp_to_python.type_to_python(attr.type_cpp, options))
#         out = out.replace(
#             "ATTR_DEFAULT",
#             cpp_to_python.default_value_to_python(attr.default_value_cpp, options),
#         )
#         return out
#
#     def split_comment(comment: str):
#         lines = comment.split("\n")
#         out = ""
#         for line in lines:
#             out += "        # " + line + "\n"
#         return out
#
#     final_code = code_intro
#     for info in struct_infos.get_attr_and_regions():
#         if info.attribute is not None:
#             attr = info.attribute
#             final_code += split_comment(cpp_to_python.docstring_python(attr.docstring_cpp, options))
#             final_code += do_replace(code_inner_param, attr)
#     final_code += code_outro_1
#     for info in struct_infos.attr_and_regions:
#         if info.attribute is not None:
#             attr = info.attribute
#             final_code += do_replace(code_inner_set, attr)
#     final_code += code_outro_2
#
#     return final_code
