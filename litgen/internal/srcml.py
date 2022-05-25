"""
Interface to srcML (https://www.srcml.org/)
"""

import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
import time
import traceback, inspect
from dataclasses import dataclass
from typing import Callable


from srcml_types import *


def _preprocess_imgui_code(code):
    import re
    new_code = code
    new_code  = re.sub(r'IM_FMTARGS\(\d\)', '', new_code)
    new_code  = re.sub(r'IM_FMTLIST\(\d\)', '', new_code)
    return new_code


@dataclass
class SrmlCppOptions:
    header_guard_suffixes: List[str]
    api_suffixes: List[str]
    ignored_block_types: List[str]
    encoding = "utf-8"
    code_preprocess_function: Callable[[str], str] = None
    filter_preprocessor_regions: bool = False

    flag_quiet = False           # if quiet, all warning messages are discarded
    flag_short_message = True
    dump_srcml_tree_on_error: bool = False

    def __init__(self):
        self.header_guard_suffixes: List[str] = []
        self.api_suffixes: List[str] = []
        self.ignored_block_types: List[str] = []
        self.filter_preprocessor_regions = False

        self.flag_short_message = True
        self.dump_srcml_tree_on_error: bool = False

    @staticmethod
    def options_litgen():
        result = SrmlCppOptions()
        result.header_guard_suffixes: List[str] = ["_H", "HPP", "HXX", "IMGUI_DISABLE"]
        result.api_suffixes: List[str] = ["API"]
        result.ignored_block_types: List[str] = [
            "empty_stmt",
            "pragma", "include", "macro", "define",             # preprocessor
            "struct_decl",                                      # struct forward decl (ignored)
            "typedef",
            "destructor", "destructor_decl",                    # destructors are not published in bindings
            "union"
        ]
        result.filter_preprocessor_regions = True

        result.flag_short_message = False
        result.dump_srcml_tree_on_error: bool = False
        return result

    @staticmethod
    def options_litgen_imgui_implot():
        result = SrmlCppOptions.options_litgen()
        result.code_preprocess_function = _preprocess_imgui_code
        return result

    @staticmethod
    def options_preserve_code():
        result = SrmlCppOptions()
        result.header_guard_suffixes: List[str] = []
        result.api_suffixes: List[str] = ["API"]
        result.ignored_block_types: List[str] = []
        result.filter_preprocessor_regions = False

        result.flag_short_message = True
        result.dump_srcml_tree_on_error: bool = False
        return result


OPTIONS = SrmlCppOptions.options_litgen()
# OPTIONS = SrmlCppOptions.options_preserve_code()


###########################################
#
# main API
#
###########################################


_CURRENT_PARSED_FILE: str = ""


def parse_code(code: str = "", filename: str = "") -> CppUnit:
    """Parse the given code, and returns it under the form of a CppUnit (which contains the parsed code)
    Note:
        * if `code` is not empty, the code will be taken from it.
          In this case, the `filename` param will still be used to display code source position in warning messages.
          This can be used when you need to preprocess the code before parsing it.
        * if `code`is empty, the code will be read from `filename`
    """
    global _CURRENT_PARSED_FILE

    if len(code) == 0:
        with open(filename, "r", encoding=OPTIONS.encoding) as f:
            code = f.read()

    if OPTIONS.code_preprocess_function is not None:
        code = OPTIONS.code_preprocess_function(code)

    _CURRENT_PARSED_FILE = filename

    element_srcml = code_to_srcml(code, True)
    cpp_unit = parse_unit(element_srcml)
    return cpp_unit


def parse_file(filename: str) -> CppUnit:
    return parse_code(code="", filename=filename)

###########################################
#
# Error and warning messages
#
###########################################

def _output_cpp_code_position(filename: str, line: int, column: int):
    """Failed attemps to make the code location clickable"""
    # if len(function_name) > 0:
    #     return f"<FrameSummary file {filename}, line {line} in {function_name}>"
    # else:
    #     return f"<FrameSummary file {filename}, line {line}, in foo>"

    return f'{filename}:{line}:{column}'


def _warning_detailed_info(
        srcml_element: ET.Element,
        parent_cpp_element: CppElement,
        additional_message: str = ""):

    def _get_python_call_info():
        stack_lines = traceback.format_stack()
        error_line = stack_lines[-4]
        frame = inspect.currentframe()
        caller_function_name = inspect.getframeinfo(frame.f_back.f_back.f_back).function
        return caller_function_name, error_line
    python_caller_function_name, python_error_line = _get_python_call_info()


    if len(_CURRENT_PARSED_FILE) > 0:
        header_filename = _CURRENT_PARSED_FILE
    else:
        header_filename = "Position:"
    cpp_code_location = _output_cpp_code_position(header_filename, parent_cpp_element.start.line, parent_cpp_element.start.column)

    if OPTIONS.dump_srcml_tree_on_error and srcml_element is not None and not OPTIONS.flag_short_message:
        child_xml_str = f"""
    Which corresponds to this xml tree:
    {code_utils.indent_code(srcml_to_str(srcml_element), 8)}
    """
    else:
        child_xml_str = ""

    srcml_element_tag = clean_tag_or_attrib(srcml_element.tag) if srcml_element is not None else ""

    if parent_cpp_element is not None:

        detailed_message = f"""
        Original C++ code: 
        {cpp_code_location}
        {code_utils.indent_code(srcml_to_code(parent_cpp_element.srcml_element), 8)}
        """

        if not OPTIONS.flag_short_message:
            detailed_message += f"""
            Issue inside parent cpp_element of type {type(parent_cpp_element)} (parsed by litgen.internal.srcml.{python_caller_function_name})

            Issue found in its srcml child, with tag "{srcml_element_tag}" with this C++ code:
            {code_utils.indent_code(srcml_to_code(srcml_element), 8)}{child_xml_str}

            Parent cpp_element code, as currently parsed by litgen (of type {type(parent_cpp_element)})
            {code_utils.indent_code(str(parent_cpp_element), 4)}
        
            Python call stack info:
            {code_utils.indent_code(python_error_line, 4)}
    
            (Note for litgen developers: add `dump_xml_tree=True` in order to see the corresponding srcml xml tree)
            """

    else:
        code_position = ""
        for k, v in srcml_element.attrib.items():
            if clean_tag_or_attrib(k) == "start":
                code_position = v

        detailed_message = f"""
        Issue found in srcml child, with this C++ code: {header_filename}:{code_position} 
        {code_utils.indent_code(srcml_to_code(srcml_element), 8)}{child_xml_str}
        """

        if not OPTIONS.flag_short_message:
            detailed_message += f"""
            Issue inside {python_caller_function_name})
                    
            Python call stack info:
            {code_utils.indent_code(python_error_line, 4)}
        
                (Note for litgen developers: add `dump_xml_tree=True` in order to see the corresponding srcml xml tree)
            """

    if len(additional_message) > 0:
        detailed_message = additional_message + "\n" + code_utils.indent_code(detailed_message, 4)

    return detailed_message


class SrcMlException(Exception):
    def __init__(self,
                 srcml_element: ET.Element,
                 parent_cpp_element: CppElement,
                 additional_message = ""):
        message = _warning_detailed_info(srcml_element, parent_cpp_element, additional_message)
        super().__init__(message)


def emit_srcml_warning(
        srcml_element: ET.Element,
        parent_cpp_element: CppElement,
        additional_message = ""):
    if OPTIONS.flag_quiet:
        return
    message = _warning_detailed_info(srcml_element, parent_cpp_element, additional_message)
    logging.warning(message)


def emit_warning(message: str):
    if OPTIONS.flag_quiet:
        return
    logging.warning(message)


###########################################
#
# code_to_srcml / srcml_to_code, etc (call program srcml)
#
###########################################


def _embed_element_into_unit(element: ET.Element) -> ET.Element:
    if element.tag.endswith("unit"):
        return element
    else:
        new_element = ET.Element("unit")
        new_element.append(element)
        return new_element


class _TimeStats:
    nb_calls: int  = 0
    total_time: float = 0.
    _last_start_time: float = 0.
    def start(self):
        self.nb_calls += 1
        self._last_start_time = time.time()
    def stop(self):
        self.total_time += time.time() - self._last_start_time
    def stats_string(self) -> str:
        if self.nb_calls == 0:
            return ""
        return f"calls: {self.nb_calls} total time: {self.total_time:.3f}s average: {self.total_time / self.nb_calls * 1000:.0f}ms"



class _SrcmlCaller:
    _stats_code_to_srcml: _TimeStats = _TimeStats()
    _stats_srcml_to_code: _TimeStats = _TimeStats()

    def _call_subprocess(self, input_filename, output_filename, dump_positions: bool):
        position_arg = "--position" if dump_positions else ""

        shell_command = f"srcml -l C++ {input_filename} {position_arg} --xml-encoding {OPTIONS.encoding} --src-encoding {OPTIONS.encoding} -o {output_filename}"
        logging.debug(f"_SrcmlCaller.call: {shell_command}")
        try:
            subprocess.check_call(shell_command, shell=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"_SrcmlCaller.call, error {e}")
            raise

    def code_to_srcml(self, input_str, dump_positions: bool = False) -> ET.Element:
        """
        Calls srcml with the given code and return the srcml as xml Element
        """
        self._stats_code_to_srcml.start()
        with tempfile.NamedTemporaryFile(suffix=".h", delete=False) as input_header_file:
            input_header_file.write(input_str.encode(OPTIONS.encoding))
            input_header_file.close()
            with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as output_xml_file:
                self._call_subprocess(input_header_file.name, output_xml_file.name, dump_positions)
                output_bytes = output_xml_file.read()
                os.remove(output_xml_file.name)
            os.remove(input_header_file.name)

        output_str = output_bytes.decode(OPTIONS.encoding)
        element = ET.fromstring(output_str)
        self._stats_code_to_srcml.stop()
        return element

    def srcml_to_code(self, element: ET.Element) -> str:
        """
        Calls srcml with the given srcml xml element and return the corresponding code
        """
        if element is None:
            return "<srcml_to_code(None)>"

        # print(f"""
        # srcml_to_code with
        #     {code_utils.indent_code(srcml_to_str(element), 12, skip_first_line=True)}
        # """)

        self._stats_srcml_to_code.start()
        unit_element = _embed_element_into_unit(element)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as input_xml_file:
            element_tree = ET.ElementTree(unit_element)
            element_tree.write(input_xml_file.name)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".h") as output_header_file:
                self._call_subprocess(input_xml_file.name, output_header_file.name, False)
                output_bytes = output_header_file.read()
                os.remove(output_header_file.name)
        os.remove(input_xml_file.name)

        code_str = output_bytes.decode(OPTIONS.encoding)
        self._stats_srcml_to_code.stop()
        return code_str


    def __del__(self):
        print(f"_SrcmlCaller: code_to_srcml {self._stats_code_to_srcml.stats_string()}    |    srcml_to_code {self._stats_srcml_to_code.stats_string()}")


_SRCML_CALLER = _SrcmlCaller()


def code_to_srcml(code: str, dump_positions: bool = True) -> ET.Element:
    return _SRCML_CALLER.code_to_srcml(code, dump_positions)


def srcml_to_code(element: ET.Element) -> str:
    return _SRCML_CALLER.srcml_to_code(element)


###########################################
#
# Parsing
#
###########################################


def element_code_position(element: ET.Element) -> Tuple[CodePosition, CodePosition]:
    start = None
    end = None
    for key, value in element.attrib.items():
        if clean_tag_or_attrib(key) == "start":
            start = CodePosition.from_string(value)
        if clean_tag_or_attrib(key) == "end":
            end = CodePosition.from_string(value)
    return start, end


def fill_cpp_element_data(element: ET.Element, inout_cpp_element: CppElement):
    inout_cpp_element.srcml_element = element
    start, end = element_code_position(element)
    inout_cpp_element.start = start
    inout_cpp_element.end = end
    inout_cpp_element.tag = clean_tag_or_attrib(element.tag)


def parse_type(element: ET.Element, previous_decl: CppDecl) -> CppType:
    """
    https://www.srcml.org/doc/cpp_srcML.html#type

    A type name can be composed of several names, for example:

        "unsigned int" -> ["unsigned", "int"]

        MY_API void Process() declares a function whose return type will be ["MY_API", "void"]
                             (where "MY_API" could for example be a dll export/import macro)

    Note:
        For composed types, like `std::map<int, std::string>` srcML returns a full tree.
        In order to simplify the process, we recompose this kind of type names into a simple string
    """

    def recompose_type_name(element: ET.Element) -> str:
        is_composed_type = (element.text is None)
        return srcml_to_code(element).strip() if is_composed_type else element.text

    assert clean_tag_or_attrib(element.tag) == "type"
    result = CppType()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            typename = recompose_type_name(child)
            result.names.append(typename)
        elif child_tag == "specifier":
            result.specifiers.append(child.text)
        elif child_tag == "modifier":
            modifier = child.text
            if modifier not in CppType.authorized_modifiers():
                raise SrcMlException(child, result, f'modifier "{modifier}" is not authorized')
            result.modifiers.append(child.text)
        elif child_tag == "argument_list":
            result.argument_list.append(child.text)
        else:
            raise SrcMlException(child, result)

    if len(result.names) == 0 and "..." not in result.modifiers:
        if previous_decl is None:
            raise SrcMlException(
                None, result,
                additional_message="Can't find type name")
        assert previous_decl is not None
        result.names = previous_decl.cpp_type.names

    if len(result.names) == 0 and "..." not in result.modifiers:
        raise SrcMlException(None, result, "len(result.names) == 0!")

    # process api names
    for name in result.names:
        is_api_name = False
        for api_suffix in OPTIONS.api_suffixes:
            if name.endswith(api_suffix):
                is_api_name = True
        if is_api_name:
            result.names.remove(name)
            result.specifiers = [name] + result.specifiers

    return result


def parse_init_expr(element: ET.Element) -> str:
    """
    Can parse simple literals, like "hello", whose tree looks like:
            <ns0:expr>
               <ns0:literal type="string">&quot;hello&quot;</ns0:literal>
            </ns0:expr>

    But for more complete expressions, like "1<<20", whose tree looks like:
            <ns0:expr>
                <ns0:literal type="number">1</ns0:literal>
                <ns0:operator><</ns0:operator>
                <ns0:literal type="number">20</ns0:literal>
            </ns0:expr>
    we will call srcml_to_code, which will invoke the executable srcml
    """
    assert clean_tag_or_attrib(element.tag) == "init"
    expr = child_with_tag(element, "expr")

    # Case for simple literals
    if len(expr) == 1:
        for child in expr:
            if clean_tag_or_attrib(child.tag) in ["literal", "name"]:
                if child.text is not None:
                    r = child.text
                    return r

    # More complex cases
    r = srcml_to_code(expr)
    return r


def parse_decl(element: ET.Element, previous_decl: CppDecl) -> CppDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """

    def recompose_decl_name(element: ET.Element) -> str:
        is_composed = (element.text is None)
        return srcml_to_code(element).strip() if is_composed else element.text

    assert clean_tag_or_attrib(element.tag) == "decl"
    result = CppDecl()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "type":
            result.cpp_type = parse_type(child, previous_decl)
        elif child_tag == "name":
            result.name = recompose_decl_name(child)
        elif child_tag == "init":
            result.init = parse_init_expr(child)
        elif child_tag == "range":
            pass # this is for C bit fields
        else:
            raise SrcMlException(child, result)

    # if not result.has_name_or_ellipsis():
    #     raise SrcMlException(child, result, "This decl has no name, and is not an ellipsis (...)!")

    return result


def parse_decl_stmt(element: ET.Element) -> CppDeclStatement:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration
    """
    assert clean_tag_or_attrib(element.tag) == "decl_stmt"

    previous_decl: CppDecl = None
    result = CppDeclStatement()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "decl":
            cpp_decl = parse_decl(child, previous_decl)
            result.cpp_decls.append(cpp_decl)
            previous_decl = cpp_decl
        else:
            raise _bad_tag_exception(child)
    return result


def parse_parameter(element: ET.Element) -> CppParameter:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert clean_tag_or_attrib(element.tag) == "parameter"
    result = CppParameter()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "decl":
            result.decl = parse_decl(child, None)
        elif child_tag == "type":
            result.template_type = parse_type(child, None) # This is only for template parameters
        elif child_tag == "name":
            result.template_name = child.text # This is only for template parameters
        elif child_tag == "function_decl":
            #result.decl = parse_function_decl(child)
            raise SrcMlException(
                child, result,
                f"A function uses a function_decl as a param. It was discarded")
        else:
            raise SrcMlException(child, result, f"unhandled tag {child_tag}")

    return result


def parse_parameter_list(element: ET.Element) -> CppParameterList:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert clean_tag_or_attrib(element.tag) == "parameter_list"
    result = CppParameterList()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "parameter":
            result.parameters.append(parse_parameter(child))
        else:
            raise SrcMlException(child, result)
    return result


def parse_template(element: ET.Element) -> CppTemplate:
    """
    Template parameters of a function, struct or class
    https://www.srcml.org/doc/cpp_srcML.html#template
    """
    assert clean_tag_or_attrib(element.tag) == "template"
    result = CppTemplate()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "parameter_list":
            result.parameter_list = parse_parameter_list(child)
        else:
            raise SrcMlException(child, result)
    return result


def fill_function_decl(element: ET.Element, function_decl: CppFunctionDecl):
    fill_cpp_element_data(element, function_decl)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "type":
            function_decl.type = parse_type(child, None)
        elif child_tag == "name":
            function_decl.name = child.text
        elif child_tag == "parameter_list":
            function_decl.parameter_list = parse_parameter_list(child)
        elif child_tag == "specifier":
            function_decl.specifiers.append(child.text)
        elif child_tag == "attribute":
            pass # compiler options, such as [[gnu::optimize(0)]]
        elif child_tag == "template":
            function_decl.template = parse_template(child)
        elif child_tag == "block":
            pass # will be handled by parse_function
        elif child_tag == "modifier":
            raise SrcMlException(
                child, function_decl, additional_message="C style function pointers are poorly supported")
        else:
            raise SrcMlException(child, function_decl)


def parse_function_decl(element: ET.Element) -> CppFunctionDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert clean_tag_or_attrib(element.tag) == "function_decl"
    result = CppFunctionDecl()
    fill_function_decl(element, result)
    return result


def parse_function(element: ET.Element) -> CppFunction:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """
    assert clean_tag_or_attrib(element.tag) == "function"
    result = CppFunction()
    fill_function_decl(element, result)

    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "block":
            # We do not parse inner function code
            # result.block = parse_block(child)
            pass
        elif child_tag in ["type", "name", "parameter_list", "specifier", "attribute", "template"]:
            pass # alread handled by fill_function_decl
        else:
            raise SrcMlException(child, result)

    return result


def fill_constructor_decl(element: ET.Element, constructor_decl: CppContructorDecl):
    fill_cpp_element_data(element, constructor_decl)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            constructor_decl.name = child.text
        elif child_tag == "parameter_list":
            constructor_decl.parameter_list = parse_parameter_list(child)
        elif child_tag == "specifier":
            constructor_decl.specifiers.append(child.text)
        elif child_tag == "attribute":
            pass # compiler options, such as [[gnu::optimize(0)]]
        elif child_tag == "block":
            pass # will be handled by parse_constructor
        else:
            raise SrcMlException(child, result)


def parse_constructor_decl(element: ET.Element) -> CppContructorDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor-declaration
    """
    assert clean_tag_or_attrib(element.tag) == "constructor_decl"
    result = CppContructorDecl()
    fill_constructor_decl(element, result)
    return result


def parse_constructor(element: ET.Element) -> CppContructor:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """
    assert clean_tag_or_attrib(element.tag) == "constructor"
    result = CppContructor()
    fill_constructor_decl(element, result)

    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "block":
            result.block = parse_block(child)
        elif child_tag in ["name", "parameter_list", "specifier", "attribute"]:
            pass # alread handled by fill_constructor_decl
        else:
            raise SrcMlException(child, result)

    return result


def parse_super(element: ET.Element) -> CppSuper:
    """
    Define a super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    assert clean_tag_or_attrib(element.tag) == "super"
    result = CppSuper()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "specifier":
            result.specifier = child.text
        elif child_tag == "name":
            result.name = child.text
        else:
            raise SrcMlException(child, result)

    return result


def parse_super_list(element: ET.Element) -> CppSuperList:
    """
    Define a list of super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    assert clean_tag_or_attrib(element.tag) == "super_list"
    result = CppSuperList()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "super":
            result.super_list.append(parse_super(child))
        else:
            raise SrcMlException(child, result)

    return result


def parse_struct_or_class(element: ET.Element) -> CppStruct:
    """
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    https://www.srcml.org/doc/cpp_srcML.html#class-definition
    """
    element_tag = clean_tag_or_attrib(element.tag)
    assert element_tag in ["struct", "class"]
    if element_tag == "struct":
        result = CppStruct()
    else:
        result = CppClass()
    fill_cpp_element_data(element, result)

    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            result.name = child.text
        elif child_tag == "super_list":
            result.super_list = parse_super_list(child)
        elif child_tag == "block":
            result.block = parse_block(child)
        elif child_tag == "template":
            result.template = parse_template(child)
        else:
            raise SrcMlException(child, result)

    return result


def parse_public_protected_private(element: ET.Element) -> CppPublicProtectedPrivate:
    """
    See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types
    """
    element_tag = clean_tag_or_attrib(element.tag)
    assert element_tag in ["public", "protected", "private"]

    block_content = CppPublicProtectedPrivate(element_tag)
    fill_cpp_element_data(element, block_content)
    fill_block(element, block_content)
    return block_content



def parse_block(element: ET.Element) -> CppBlock:
    """
    https://www.srcml.org/doc/cpp_srcML.html#block
    """
    assert clean_tag_or_attrib(element.tag) == "block"

    cpp_block = CppBlock()
    fill_cpp_element_data(element, cpp_block)
    fill_block(element, cpp_block)
    return cpp_block


class _PreprocessorTestState:
    """We ignore everything that is inside a #ifdef/#if/#ifndef  region
       but we try to keep what is inside the header inclusion guard ifndef region.

       We will test that a ifndef is an inclusion guard by checking comparing its suffix with HEADER_GUARD_SUFFIXES
    """

    nb_tests = 0

    def process_tag(self, element: ET.Element) -> bool:
        """Returns true if this tag was processed"""

        if not OPTIONS.filter_preprocessor_regions:
            return False

        def extract_ifndef_name():
            for child in element:
                if clean_tag_or_attrib(child.tag) == "name":
                    return child.text
            return ""

        def is_inclusion_guard_ifndef():
            ifndef_name = extract_ifndef_name()
            for suffix in OPTIONS.header_guard_suffixes:
                if ifndef_name.upper().endswith(suffix.upper()):
                    return True
            return False

        tag = clean_tag_or_attrib(element.tag)
        is_preprocessor_test = False
        if tag in ["ifdef", "if"]:
            self.nb_tests += 1
            is_preprocessor_test = True
        elif tag == "endif":
            self.nb_tests -= 1
            is_preprocessor_test = True
        elif tag in ["else", "elif"]:
            is_preprocessor_test = True
        elif tag == "ifndef":
            if not is_inclusion_guard_ifndef():
                self.nb_tests += 1
            is_preprocessor_test = True

        return is_preprocessor_test

    def is_inside_ignored_region(self) -> bool:
        if not OPTIONS.filter_preprocessor_regions:
            return False

        assert self.nb_tests >= -1 # -1 because we can ignore the inclusion guard
        if self.nb_tests > 0:
            return True
        else:
            return False


def fill_block(element: ET.Element, inout_block_content: CppBlock):
    """
    https://www.srcml.org/doc/cpp_srcML.html#block_content
    """

    last_ignored_child: ET.Element = None

    _preprocessor_tests_state = _PreprocessorTestState()

    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)

        if _preprocessor_tests_state.process_tag(child):
            pass
        elif _preprocessor_tests_state.is_inside_ignored_region():
            pass
        elif child_tag == "decl_stmt":
            try:
                inout_block_content.block_children.append(parse_decl_stmt(child))
            except SrcMlException as e:
                emit_warning(f"A decl_stmt was ignored. Details follow\n {e}")
        elif child_tag == "decl":
            inout_block_content.block_children.append(parse_decl(child, None))
        elif child_tag == "function_decl":
            try:
                inout_block_content.block_children.append(parse_function_decl(child))
            except SrcMlException as e:
                emit_warning(f"A function was ignored. Details follow\n {e}")
        elif child_tag == "function":
            try:
                inout_block_content.block_children.append(parse_function(child))
            except SrcMlException as e:
                emit_warning(f"A function was ignored. Details follow\n {e}")
        elif child_tag == "constructor_decl":
            inout_block_content.block_children.append(parse_constructor_decl(child))
        elif child_tag == "constructor":
            inout_block_content.block_children.append(parse_constructor(child))

        elif child_tag == "comment":
            cpp_comment = parse_comment(child)

            ignore_comment = False
            if last_ignored_child is not None:
                last_ignore_child_end_position = element_code_position(last_ignored_child)[1]
                if cpp_comment.start.line == last_ignore_child_end_position.line:
                    # When there is an explanation following a typedef or a struct forward decl,
                    # we keep both the code (as a comment) and its comment
                    if clean_tag_or_attrib(last_ignored_child.tag) in ["typedef", "struct_decl"]:
                        cpp_comment.text = "// " + srcml_to_code(last_ignored_child) + "    " + cpp_comment.text
                        ignore_comment = False
                    else:
                        ignore_comment = True

            if not ignore_comment:
                inout_block_content.block_children.append(cpp_comment)

        elif child_tag == "struct":
            inout_block_content.block_children.append(parse_struct_or_class(child))
        elif child_tag == "class":
            inout_block_content.block_children.append(parse_struct_or_class(child))
        elif child_tag == "namespace":
            inout_block_content.block_children.append(parse_namespace(child))
        elif child_tag == "enum":
            inout_block_content.block_children.append(parse_enum(child))
        elif child_tag == "expr_stmt":
            inout_block_content.block_children.append(parse_expr_stmt(child))
        elif child_tag == "return":
            inout_block_content.block_children.append(parse_return(child))
        elif child_tag == "block_content":
            inout_block_content.block_children.append(parse_block_content(child))
        elif child_tag in ["public", "protected", "private"]:
            inout_block_content.block_children.append(parse_public_protected_private(child))
        elif child_tag in OPTIONS.ignored_block_types:
            last_ignored_child = child
        else:
            # raise _bad_tag_exception(child)
            # emit_srcml_warning(child, None, f'Unhandled tag type in `fill_block`: "{child_tag}"')
            inout_block_content.block_children.append(parse_unprocessed(child))


def parse_unit(element: ET.Element) -> CppUnit:
    assert clean_tag_or_attrib(element.tag) == "unit"
    cpp_unit = CppUnit()
    fill_cpp_element_data(element, cpp_unit)
    fill_block(element, cpp_unit)
    return cpp_unit


def parse_unprocessed(element: ET.Element) -> CppUnit:
    result = CppUnprocessed()
    fill_cpp_element_data(element, result)
    result.code = srcml_to_code(element)
    result.tag = clean_tag_or_attrib(element.tag)
    return result


def parse_block_content(element: ET.Element) -> CppBlockContent:
    """
    https://www.srcml.org/doc/cpp_srcML.html#block_content
    """
    assert clean_tag_or_attrib(element.tag) == "block_content"

    block_content = CppBlockContent()
    fill_cpp_element_data(element, block_content)
    fill_block(element, block_content)
    return block_content


def parse_comment(element: ET.Element) -> CppComment:
    """
    https://www.srcml.org/doc/cpp_srcML.html#comment
    """
    assert clean_tag_or_attrib(element.tag) == "comment"
    assert len(element) == 0 # a comment has no child

    result = CppComment()
    fill_cpp_element_data(element, result)
    result.text = element.text

    return result


def parse_namespace(element: ET.Element) -> CppNamespace:
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """
    assert clean_tag_or_attrib(element.tag) == "namespace"
    result = CppNamespace()
    fill_cpp_element_data(element, result)
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            result.name = child.text
        elif child_tag == "block":
            result.block = parse_block(child)
        else:
            raise _bad_tag_exception(child)

    return result


def parse_enum(element: ET.Element) -> CppEnum:
    """
    https://www.srcml.org/doc/cpp_srcML.html#enum-definition
    https://www.srcml.org/doc/cpp_srcML.html#enum-class
    """
    assert clean_tag_or_attrib(element.tag) == "enum"
    result = CppEnum()
    fill_cpp_element_data(element, result)

    if "type" in element.attrib.keys():
        result.type = element.attrib["type"]

    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            result.name = child.text
        elif child_tag == "block":
            result.block = parse_block(child)
        else:
            raise SrcMlException(child, result)

    return result


def parse_expr_stmt(element: ET.Element) -> CppExprStmt:
    assert clean_tag_or_attrib(element.tag) == "expr_stmt"
    result = CppExprStmt()
    fill_cpp_element_data(element, result)
    return result


def parse_return(element: ET.Element) -> CppReturn:
    assert clean_tag_or_attrib(element.tag) == "return"
    result = CppReturn()
    fill_cpp_element_data(element, result)
    return result



###########################################
#
# Utilities
#
###########################################


def children_with_tag(element: ET.Element, tag: str) -> List[ET.Element]:
    r = []
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == tag:
            r.append(child)
    return r


def child_with_tag(element: ET.Element, tag: str) -> ET.Element:
    children = children_with_tag(element, tag)
    if len(children) == 0:
        tags_strs = map(lambda c: '"' + clean_tag_or_attrib(c.tag) + '"', element)
        tags_str = ", ".join(tags_strs)
        message = f'child_with_tag: did not find child with tag "{tag}"  (found [{tags_str}])'
        logging.error(message)
        raise LookupError(message)
    elif len(children) > 1:
        message = f'child_with_tag: found more than one child with tag "{tag}" (found {len(children)})'
        logging.error(message)
        raise LookupError(message)
    return  children[0]


def first_code_element_with_tag(code: str, tag: str, dump_positions: bool = True) -> ET.Element:
    """
    Utility for tests: extracts the first xml element of type "decl_stmt"
    """
    root = code_to_srcml(code, dump_positions)
    return child_with_tag(root, tag)


def srcml_to_str(element: ET.Element, bare = False):
    xmlstr_raw = ET.tostring(element, encoding="unicode")
    if bare:
        return xmlstr_raw

    try:
        xmlstr = minidom.parseString(ET.tostring(element)).toprettyxml(indent="   ")
    except Exception as e:
        xmlstr = xmlstr_raw

    return xmlstr


def srcml_to_file(root: ET.Element, filename: str):
    element_tree = ET.ElementTree(root)
    element_tree.write(filename, encoding=OPTIONS.encoding)


def clean_tag_or_attrib(tag_name: str) -> str:
    if tag_name.startswith("{"):
        assert("}") in tag_name
        pos = tag_name.index("}") + 1
        tag_name = tag_name[ pos : ]
    tag_name = tag_name.replace("ns0:", "")
    tag_name = tag_name.replace("ns1:", "")
    return tag_name

