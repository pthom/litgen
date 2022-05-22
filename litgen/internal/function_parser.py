import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR] + sys.path
import re
from dataclasses import dataclass

from code_types import *
from options import CodeStyleOptions
import struct_parser, enum_parser, function_parser
import code_utils
import find_functions_structs_enums


@dataclass
class _ScopeObserver:
    _nb_chevrons: int = 0
    _is_in_sub_scope: bool = False
    _struct_start_nb_chevrons: int = -1

    def __init__(self):
        self.reset()

    def reset(self):
        self._nb_chevrons = 0
        self._struct_start_nb_chevrons = -1
        self._is_in_sub_scope = False

    def parse_line(self, line):
        if line.startswith("struct"):
            self._is_in_sub_scope = True
            self._struct_start_nb_chevrons = self._nb_chevrons

        self._nb_chevrons += line.count("{")
        self._nb_chevrons -= line.count("}")

        if self._is_in_sub_scope and self._nb_chevrons == self._struct_start_nb_chevrons:
            self._is_in_sub_scope = False

    def is_in_main_scope(self):
        return self._is_in_sub_scope == False


_SCOPE_OBSERVER = _ScopeObserver()


def is_function_in_excludes(function_name: str, options: CodeStyleOptions) -> bool:
    for regex in options.function_name_exclude_regexes:
        matches = list(re.finditer(regex, function_name, re.MULTILINE))
        if len(matches) > 0:
            return True
    return False


def _try_parse_function_name_from_declaration(code: str, options: CodeStyleOptions) -> Optional[PydefCode]:
    full_line = code
    code = code_utils.remove_end_of_line_cpp_comments(code)
    code = code_utils.force_one_space(code)

    # update state
    _SCOPE_OBSERVER.parse_line(code)

    def is_prefix_found():
        nonlocal code
        if len(options.functions_api_prefixes) == 0:
            return True
        for possible_prefix in options.functions_api_prefixes:
            if code.startswith(possible_prefix):
                code = code.replace(possible_prefix, "").strip()
                return True
        return False

    for exclude_comment in options.function_exclude_by_comment:
        if exclude_comment in full_line:
            return None

    if is_prefix_found() and _SCOPE_OBSERVER.is_in_main_scope():
        function_definition = code_utils.parse_function_declaration(code)
        if function_definition is None:
            return None

        if is_function_in_excludes(function_definition.name_cpp, options):
            return None

        return PydefCode(code_type=CppCodeType.FUNCTION,
                         name_cpp=function_definition.name_cpp,
                         return_type_cpp=function_definition.return_type_cpp,
                         declaration_line = full_line
                         )
    return None


def _reset_parse_state():
    global _SCOPE_OBSERVER
    _SCOPE_OBSERVER = _ScopeObserver()



def _split_function_parameters(function_decl_body_code):
    function_decl_body_code = function_decl_body_code.replace("\n", " ").replace("\t", " ")
    split_indexes = [1] # function_decl_body_code starts with a "("
    nb_parentheses = 0
    nb_chevrons = 0
    for char_position, char  in enumerate(function_decl_body_code):
        if char == "(":
            nb_parentheses += 1
        if char == ")":
            nb_parentheses -= 1
        if char == "<":
            nb_parentheses += 1
        if char == ">":
            nb_parentheses -= 1
        if char == "," and nb_chevrons == 0 and nb_parentheses == 1:
            split_indexes.append(char_position)
    split_indexes.append(len(function_decl_body_code) - 1)

    intervals = list(code_utils.overlapping_pairs(split_indexes))
    items = []
    for interval in intervals:
        item = function_decl_body_code[interval[0] : interval[1]]
        if len(item) == 0:
            continue
        if item[0] == ",":
            item = item[1:]
        item_strip = item.strip()
        if len(item_strip) > 0:
            items.append(item.strip())
    return items


def _extract_function_parameters(function_decl_body_code: str, code_style_options: CodeStyleOptions) -> List[PydefAttribute]:
    """
    can parse a string like:
        const cv::Mat& image,
        const cv::Size& imageDisplaySize = cv::Size(),
        bool refreshImage = false,
        bool showOptions = true,
        bool isBgrOrBgra = true
    """
    parameters_strs = _split_function_parameters(function_decl_body_code)

    def parse_one_function_parameter(param_def_string: str) -> Optional[PydefAttribute]:
        if param_def_string == "...":
            return PydefAttribute(name_cpp="...")
        param = PydefAttribute()
        if "=" in param_def_string:
            items = param_def_string.split("=")
            if len(items) > 2:
                raise RuntimeError(f"parse_one_function_parameter({param_def_string}): expected at most on = sign")
            param.default_value_cpp = items[1].strip()
            param_def_string = items[0].strip()
        if " " not in param_def_string:
            raise RuntimeError(f"parse_one_function_parameter({param_def_string}): expected at least one space")
        last_space_pos = param_def_string.rindex(" ")
        param.type_cpp = param_def_string[:last_space_pos]
        param.name_cpp = param_def_string[last_space_pos + 1:]
        return param

    all_parameters = []
    for parameter_str in parameters_strs:
        parse_result = parse_one_function_parameter(parameter_str)
        if parse_result is not None:
            all_parameters.append(parse_result)

    return all_parameters


def parse_function_declaration_pydef(pydef_code: PydefCode, code_style_options: CodeStyleOptions) -> FunctionsInfos:
    r = FunctionsInfos()
    r.function_code = pydef_code
    r.parameters = _extract_function_parameters(pydef_code.body_code_cpp, code_style_options)

    ret_policy_str = "return_value_policy::"
    if ret_policy_str in pydef_code.declaration_line:
        rest_of_line = pydef_code.declaration_line[
                            pydef_code.declaration_line.index(ret_policy_str) + len(ret_policy_str) : ]
        policy_name, _ = code_utils.parse_c_identifier_at_start(rest_of_line)
        r.return_value_policy = ret_policy_str + policy_name

    return r


def parse_all_function_declarations(code: str, options: CodeStyleOptions) -> List[FunctionsInfos]:
    functions_pydefs = find_functions_structs_enums.find_functions_struct_or_enums(code, CppCodeType.FUNCTION, options)
    functions_infos = list(map(lambda function_pydef: parse_function_declaration_pydef(function_pydef, options), functions_pydefs))
    return functions_infos


def parse_one_function_declaration(code: str, options: CodeStyleOptions) -> FunctionsInfos:
    found_functions = parse_all_function_declarations(code, options)
    assert len(found_functions) == 1
    return found_functions[0]
