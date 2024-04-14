"""Workaround for https://github.com/srcML/srcML/issues/1833

    void Foo(int v = 0 );
is correctly parsed as a function_decl

However,
    void Foo(int v = {} );
is parsed as a decl_stmt

These are painful hacks, which should removed as soon as this is fixed inside srcML.
"""
from __future__ import annotations


from typing import Optional
import copy
import srcmlcpp
from srcmlcpp.cpp_types import (
    CppFunctionDecl,
    CppConstructorDecl,
    CppDeclStatement,
    CppUnprocessed,
    CppPublicProtectedPrivate,
    CppBlock,
    CppStruct,
)
from srcmlcpp.internal.code_to_srcml import srcml_to_code


def _elt_text_and_tail(v: srcmlcpp.SrcmlWrapper) -> str:
    r = ""
    if v.srcml_xml.text is not None:
        r += v.srcml_xml.text

    children = v.make_wrapped_children()
    if len(children) > 0:
        last_child = children[-1]
        last_child_tail = last_child.srcml_xml.tail
        if last_child_tail is not None:
            r += last_child_tail

    return r


def _hack_block_replace_braces(orig_block: srcmlcpp.SrcmlWrapper) -> srcmlcpp.SrcmlWrapper:
    block = copy.deepcopy(orig_block)
    block.srcml_xml = copy.deepcopy(orig_block.srcml_xml)

    assert block.srcml_xml.text is not None
    if block.srcml_xml.text.replace(" ", "") == "{}":
        block.srcml_xml.text = "__srcmlcpp_brace_init__()"
        return block

    if block.srcml_xml.text.strip().startswith("{"):
        block.srcml_xml.text = "__srcmlcpp_brace_init__(" + block.srcml_xml.text.strip()[1:]

    children = block.make_wrapped_children()
    assert len(children) > 0
    last_child = children[-1]
    last_child_tail = last_child.srcml_xml.tail
    if last_child_tail is not None:
        if last_child_tail.strip().endswith("}"):
            last_child.srcml_xml.tail = last_child_tail.strip()[:-1] + ")"

    return block


def _rewrite_decl_if_suspicious_fn_decl(decl_stmt: CppDeclStatement) -> Optional[str]:
    """
    See https://github.com/srcML/srcML/issues/1833
        srcmlcpp xml "int f(P p={});"
    is wrongly parsed as a decl_stmt.

    Here is the parse result:

        <?xml version="1.0" ?>
        <unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0" language="C++" hash="ab36c570f6a3092d25620cded830ba3ce9bb7c76">
           <decl_stmt>
              <decl>
                <type> <name>int</name></type>
                <name>f</name>
                 <argument_list> (      <== the presence of argument_list it the first suspicion
                    <argument>
                       <expr>
                          <name>P</name> <name>p</name> <== then, the presence of two "name" nodes
                          <operator>=</operator>        <==  + "operator" with text=="=" child confirms the suspicion
                          <block>{}</block>             <== we also verify that there is a block child
                       </expr>
                    </argument>
                 ) </argument_list>
              </decl>
              ;
           </decl_stmt>
        </unit>
    """

    decl = decl_stmt.wrapped_child_with_tag("decl")
    if decl is None:
        return None

    arg_lists = decl.wrapped_children_with_tag("argument_list")
    if len(arg_lists) == 0:
        return None

    hacked_decl = copy.deepcopy(decl)
    arg_lists = hacked_decl.wrapped_children_with_tag("argument_list")
    if len(arg_lists) == 0:
        return None
    arg_list = arg_lists[0]

    was_hacked = False
    arguments = arg_list.wrapped_children_with_tag("argument")
    for argument in arguments:
        expr = argument.wrapped_child_with_tag("expr")
        if expr is not None:
            names = expr.wrapped_children_with_tag("name")
            operators = expr.wrapped_children_with_tag("operator")
            block = expr.wrapped_child_with_tag("block")
            if len(names) == 2 and len(operators) > 0 and block is not None:
                has_one_equal_operator = False
                for operator in operators:
                    operator_text = operator.srcml_xml.text
                    if operator_text is not None and operator_text.strip() == "=":
                        has_one_equal_operator = True

                block_text_tail = _elt_text_and_tail(block).strip()
                if has_one_equal_operator and block_text_tail.startswith("{") and block_text_tail.endswith("}"):
                    hacked_block = _hack_block_replace_braces(block)
                    expr.srcml_xml.remove(block.srcml_xml)
                    expr.srcml_xml.append(hacked_block.srcml_xml)
                    was_hacked = True

    if was_hacked:
        hacked_code = srcml_to_code(hacked_decl.srcml_xml)
        return hacked_code
    else:
        return None


def _change_fn_params_default_to_brace_init(fn: CppFunctionDecl) -> None:
    for param in fn.parameter_list.parameters:
        token = "__srcmlcpp_brace_init__("
        if param.decl.initial_value_code.startswith(token):
            param.decl.initial_value_code = "{" + param.decl.initial_value_code[len(token) : -1] + "}"


def change_decl_stmt_to_function_decl_if_suspicious(
    options: srcmlcpp.SrcmlcppOptions, decl_stmt: CppDeclStatement
) -> Optional[CppFunctionDecl]:
    if not options.fix_brace_init_default_value:
        return None
    fixed_code = _rewrite_decl_if_suspicious_fn_decl(decl_stmt)
    if fixed_code is None:
        return None
    else:
        fixed_cpp_unit = srcmlcpp.code_to_cpp_unit(options, fixed_code)
        fixed_functions = fixed_cpp_unit.all_functions_recursive()
        assert len(fixed_functions) == 1
        fixed_function = fixed_functions[0]
        _change_fn_params_default_to_brace_init(fixed_function)
        return fixed_function


def change_macro_to_constructor(options: srcmlcpp.SrcmlcppOptions, macro: CppUnprocessed) -> Optional[CppFunctionDecl]:
    macro_code = macro.str_code_verbatim()
    if not isinstance(macro.parent, CppPublicProtectedPrivate):
        return None
    parent_block = macro.parent.parent
    if not isinstance(parent_block, CppBlock):
        return None
    parent_struct = parent_block.parent
    if not isinstance(parent_struct, CppStruct):
        return None
    class_name = parent_struct.class_name
    if not macro_code.strip().startswith(class_name):
        return None

    fixed_macro_code = "void blah" + macro_code[len(class_name) :] + ";"
    fixed_cpp_unit = srcmlcpp.code_to_cpp_unit(options, fixed_macro_code)
    fixed_functions = fixed_cpp_unit.all_functions_recursive()
    if len(fixed_functions) != 1:
        macro.raise_exception(f"Expected one function, got {len(fixed_functions)}")
    fixed_function = fixed_functions[0]
    fixed_function.function_name = class_name
    fixed_function.return_type.typenames = []

    fixed_constructor = CppConstructorDecl(fixed_function, fixed_function.cpp_element_comments)
    fixed_constructor._parameter_list = fixed_function.parameter_list
    fixed_constructor.function_name = class_name
    return fixed_constructor
