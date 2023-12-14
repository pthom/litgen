from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import List, Optional
from xml.etree import ElementTree as ET  # noqa

from munch import Munch  # type: ignore

from codemanip import code_utils

import srcmlcpp
from srcmlcpp.cpp_types import (
    CppAccessType,
    CppClass,
    CppConstructorDecl,
    CppEmptyLine,
    CppFunctionDecl,
    CppStruct,
    CppComment,
)
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions

import os

# Todo: const, constexpr, and other methods specifiers


@dataclass
class PimplResult:
    header_code: str = ""
    glue_code: str = ""


@dataclass
class PimplOptions:
    pimpl_suffixes: List[str]
    indent_str: str = "    "
    indent_public: str = "  "
    max_consecutive_empty_lines = 2
    line_feed_before_block: bool = True
    impl_member_name = "mPImpl"

    def __init__(self) -> None:
        self.pimpl_suffixes = [
            "_pimpl",
            "_impl",
            "pimpl",
            "impl",
            "_PImpl",
            "_Impl",
            "PImpl",
            "Impl",
            "_Pimpl",
            "Pimpl",
        ]


class PimplMyClass:
    impl_class: CppStruct
    options: PimplOptions

    def __init__(self, options: PimplOptions, impl_class: CppStruct) -> None:
        self.impl_class = impl_class
        self.options = options

    def _impl_class_name(self) -> str:
        return self.impl_class.class_name

    def _published_class_name(self) -> str:
        impl_class_name = self._impl_class_name()
        for suffix in self.options.pimpl_suffixes:
            if impl_class_name.endswith(suffix):
                return impl_class_name[: -len(suffix)]
        raise Exception(f"pImpl class name needs to end with a suffix among {self.options.pimpl_suffixes}")

    def _published_method_glue_impl(self, cpp_function: CppFunctionDecl) -> str:
        if cpp_function.has_return_type() and "static" in cpp_function.return_type.specifiers:
            cpp_function = copy.deepcopy(cpp_function)
            # C++ peculiarity: static is not allowed for the implementation, only for decl
            cpp_function.return_type.specifiers.remove("static")
            is_static = True
        else:
            is_static = False

        cpp_function = self._remove_published_incompatible_specifiers(cpp_function)
        if is_static:
            template = code_utils.unindent_code(
                """
            {return_type} {class_published}::{method_name}({params_list}) {maybe_const}{
            {_i_}{maybe_return}{class_impl}::{method_name}({param_names}); }
            """,
                flag_strip_empty_lines=True,
            )
        else:
            template = code_utils.unindent_code(
                """
            {return_type} {class_published}::{method_name}({params_list}) {maybe_const}{
            {_i_}{maybe_return}{impl_name}->{method_name}({param_names}); }
            """,
                flag_strip_empty_lines=True,
            )

        replacements = Munch()
        replacements._i_ = self.options.indent_str
        replacements.class_published = self._published_class_name()
        replacements.class_impl = self._impl_class_name()
        replacements.impl_name = self.options.impl_member_name
        replacements.return_type = cpp_function.return_type.str_code() if cpp_function.has_return_type() else ""
        replacements.method_name = cpp_function.function_name
        replacements.params_list = cpp_function.parameter_list.str_code()
        replacements.maybe_return = (
            "" if (not cpp_function.has_return_type() or cpp_function.return_type.is_void()) else "return "
        )
        replacements.param_names = cpp_function.parameter_list.str_names_only_for_call()
        replacements.maybe_const = "const " if "const" in cpp_function.specifiers else ""

        replacements_by_line = Munch()

        r = code_utils.process_code_template(template, replacements, replacements_by_line)
        return r

    @staticmethod
    def _remove_published_incompatible_specifiers(cpp_function: CppFunctionDecl) -> CppFunctionDecl:
        unwanted_specifiers = ["inline", "constexpr"]
        for unwanted_specifier in unwanted_specifiers:
            if cpp_function.has_return_type() and unwanted_specifier in cpp_function.return_type.specifiers:
                cpp_function = copy.deepcopy(cpp_function)  # clone in order not to modify caller value?
                cpp_function.return_type.specifiers.remove(unwanted_specifier)
        return cpp_function

    def _published_method_decl(self, cpp_function: CppFunctionDecl) -> str:
        cpp_function = self._remove_published_incompatible_specifiers(cpp_function)
        unwanted_specifiers = ["inline", "constexpr"]
        for unwanted_specifier in unwanted_specifiers:
            if cpp_function.has_return_type() and unwanted_specifier in cpp_function.return_type.specifiers:
                # cpp_function = copy.deepcopy(cpp_function) # clone in order not to modify caller value?
                cpp_function.return_type.specifiers.remove(unwanted_specifier)

        template = code_utils.unindent_code(
            """
        {top_comment}{return_type} {method_name}({params_list}){maybe_const};{maybe_eol_comment}
        """,
            flag_strip_empty_lines=True,
        )

        replacements = Munch()
        replacements.top_comment = cpp_function.cpp_element_comments.top_comment_code(add_eol=True)
        replacements.return_type = cpp_function.return_type.str_code() if cpp_function.has_return_type() else ""
        replacements.method_name = cpp_function.function_name
        replacements.params_list = cpp_function.parameter_list.str_code()
        replacements.maybe_eol_comment = cpp_function.cpp_element_comments.eol_comment_code()
        replacements.maybe_const = " const" if "const" in cpp_function.specifiers else ""

        replacements_by_line = Munch()
        replacements_by_line.top_comment = cpp_function.cpp_element_comments.top_comment_code(add_eol=False)

        r = code_utils.process_code_template(template, replacements, replacements_by_line)
        return r

    def _published_constructor_impl(self, cpp_constructor: CppConstructorDecl) -> str:
        template = code_utils.unindent_code(
            """
        {class_published}::{class_published}({param_list})
        {_i_}: {impl_name}(std::make_unique<{class_impl}>({param_names})) { }
        """,
            flag_strip_empty_lines=True,
        )

        replacements = Munch()
        replacements._i_ = self.options.indent_str
        replacements.param_list = str(cpp_constructor.parameter_list)
        replacements.class_published = self._published_class_name()
        replacements.class_impl = self._impl_class_name()
        replacements.impl_name = self.options.impl_member_name
        replacements.param_names = cpp_constructor.parameter_list.str_names_only_for_call()

        replacements_by_line = Munch()

        r = code_utils.process_code_template(template, replacements, replacements_by_line)
        return r

    def _published_constructor_decl(self, cpp_constructor: CppConstructorDecl) -> str:
        template = code_utils.unindent_code(
            """
    {top_comment}{class_published}({param_list});{maybe_eol_comment}
        """,
            flag_strip_empty_lines=True,
        )

        replacements = Munch()
        replacements.top_comment = cpp_constructor.cpp_element_comments.top_comment_code(add_eol=True)
        replacements.class_published = self._published_class_name()
        replacements.param_list = str(cpp_constructor.parameter_list)
        replacements.maybe_eol_comment = cpp_constructor.cpp_element_comments.eol_comment_code()

        replacements_by_line = Munch()
        replacements_by_line.top_comment = cpp_constructor.cpp_element_comments.top_comment_code(add_eol=False)

        r = code_utils.process_code_template(template, replacements, replacements_by_line)
        return r

    def _glue_code(self) -> str:
        r = ""
        for public_block in self.impl_class.get_access_blocks(CppAccessType.public):
            for child in public_block.block_children:
                if isinstance(child, CppConstructorDecl):
                    r += self._published_constructor_impl(child) + "\n"
                elif isinstance(child, CppFunctionDecl):
                    if child.is_destructor():
                        continue
                    r += self._published_method_glue_impl(child) + "\n"

        r += f"{self._published_class_name()}::~{self._published_class_name()}() = default;\n"
        return r

    def _published_method_decls(self) -> str:
        published_methods = ""
        for public_block in self.impl_class.get_access_blocks(CppAccessType.public):
            for child in public_block.block_children:
                if isinstance(child, CppConstructorDecl):
                    published_methods += self._published_constructor_decl(child) + "\n"
                elif isinstance(child, CppFunctionDecl):
                    if child.is_destructor():
                        continue
                    published_methods += self._published_method_decl(child) + "\n"
                elif isinstance(child, CppEmptyLine):
                    published_methods += "\n"
                elif isinstance(child, CppComment):
                    published_methods += str(child) + "\n"
        if published_methods.endswith("\n"):
            published_methods = published_methods[:-1]
        return code_utils.indent_code(published_methods, indent_str=self.options.indent_str)

    def _header_code(self) -> str:
        template = code_utils.unindent_code(
            """
        {class_or_struct} {impl_class_name};

        {top_comment}
        {class_or_struct} {published_class_name}{maybe_eol_comment}{linefeed_or_space}{
        {i}{maybe_public}
        {published_methods}
        {_i_}~{published_class_name}();
        {i}private:
        {_i_}std::unique_ptr<{impl_class_name}> {impl_name};
        };
        """,
            flag_strip_empty_lines=True,
        )

        is_class = isinstance(self.impl_class, CppClass)

        replacements = Munch()
        replacements.linefeed_or_space = "\n" if self.options.line_feed_before_block else " "
        replacements._i_ = self.options.indent_str
        replacements.i = self.options.indent_public
        replacements.class_or_struct = "class" if is_class else "struct"
        replacements.maybe_eol_comment = self.impl_class.cpp_element_comments.eol_comment_code()
        replacements.published_class_name = self._published_class_name()
        replacements.impl_class_name = self._impl_class_name()
        replacements.impl_name = self.options.impl_member_name
        replacements.published_methods = self._published_method_decls()

        replacements_by_line = Munch()
        replacements_by_line.top_comment = self.impl_class.cpp_element_comments.top_comment_code(add_eol=False)
        replacements_by_line.maybe_public = "public:" if is_class else ""

        r = code_utils.process_code_template(template, replacements, replacements_by_line)

        if self.options.max_consecutive_empty_lines >= 0:
            r = code_utils.code_set_max_consecutive_empty_lines(r, self.options.max_consecutive_empty_lines)

        return r

    def result(self) -> PimplResult:
        r = PimplResult()
        r.glue_code = self._glue_code()
        r.header_code = self._header_code()
        return r


def pimpl_my_class(impl_class: CppStruct, options: Optional[PimplOptions] = None) -> PimplResult:
    if options is None:
        options = PimplOptions()
    c = PimplMyClass(options, impl_class)
    r = c.result()
    return r


def pimpl_my_code(
    code: str, pimpl_options: Optional[PimplOptions] = None, srcmlcpp_options: Optional[SrcmlcppOptions] = None
) -> Optional[PimplResult]:
    """Will parse the code and return the pimpl result of the *first* PImpl class in this code (if found)"""
    if pimpl_options is None:
        pimpl_options = PimplOptions()
    if srcmlcpp_options is None:
        srcmlcpp_options = SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(srcmlcpp_options, code)
    all_structs = cpp_unit.all_structs_recursive()
    return None if len(all_structs) == 0 else pimpl_my_class(all_structs[0], pimpl_options)


def pimpl_my_file(
    cpp_filename: str,
    header_filename: str | None = None,
    pimpl_options: Optional[PimplOptions] = None,
    srcmlcpp_options: Optional[SrcmlcppOptions] = None,
) -> None:
    """Will parse the file and return the pimpl result of the *first* PImpl class in this file (if found)"""

    # if header_filename is None, assume the header file is the same as the cpp file, but with .h extension
    if header_filename is None:
        possible_cpp_extensions = [".cpp", ".cc", ".cxx", ".c++", ".c", ".C"]
        for ext in possible_cpp_extensions:
            if cpp_filename.endswith(ext):
                header_filename = cpp_filename[: -len(ext)] + ".h"
                break
        if header_filename is None:
            raise Exception(f"Could not find header_filename for {cpp_filename}")

    # if header_filename or cpp_filename do not exist, raise
    if not os.path.isfile(header_filename):
        raise Exception(f"Header file {header_filename} does not exist")
    if not os.path.isfile(cpp_filename):
        raise Exception(f"C++ file {cpp_filename} does not exist")

    # Read code from file
    with open(cpp_filename, "r") as f:
        code = f.read()

    pimpl_result = pimpl_my_code(code, pimpl_options, srcmlcpp_options)
    if pimpl_result is None:
        print("No PImpl class found!")
    else:
        code_utils.write_generated_code_between_markers(
            cpp_filename,
            "pimpl_glue_code",
            pimpl_result.glue_code,
        )
        code_utils.write_generated_code_between_markers(
            header_filename,
            "pimpl_header_code",
            pimpl_result.header_code,
        )


_PIMPL_DEMO_CPP_NO_MARKER = """
#include "my_class.h"

#include <string>
#include <future>

// Some doc about the class, that you want to see in the header file
class MyClassPImpl
{
public:
    //
    // Some doc you also want to see in the header file, since it is in a public block
    //

    // Construct an Instance
    MyClassPImpl(const std::string& someVar)
    {
        // Some code you provide in the C++ file, but do not want to see in the header file
    }

    // Some method
    bool SomeMethod() { /* ... */ }

    // Some public static method
    static bool SomeStaticMethod() { /* ... */ }

    // The destructor should not be published as is, but should use the unique_ptr default destructor
    ~MyClassPImpl() { /* ... */ }

private:
    //
    // Some private doc, which should not be published
    //

    bool SomePrivateMethod() { /* ... */ }

    std::string mSomePrivateMember;
    std::future<void> mAnoterPrivateMember;
};
"""


def demo_cpp_no_marker():
    return _PIMPL_DEMO_CPP_NO_MARKER


_PIMPL_DEMO_CPP = """
#include "my_class.h"

struct MyStructPImpl
{
    MyStructPImpl() { /* ...*/ }
    bool SomeMethod() { /* ... */ }
private:
    bool SomePrivateMethod() { /* ... */ }
    int mSomePrivateMember;
};

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// <pimpl_glue_code>  // Autogenerated code below! Do not edit!
// </pimpl_glue_code> // Autogenerated code end
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

"""


_PIMPL_DEMO_HEADER = """
#pragma once
#include <memory>

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// <pimpl_header_code>  // Autogenerated code below! Do not edit!
// </pimpl_header_code> // Autogenerated code end
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""


def create_pimpl_example_files():
    import tempfile

    temp_dir = tempfile.mkdtemp()
    cpp_filename = temp_dir + "/my_class.cpp"
    header_filename = temp_dir + "/my_class.h"
    with open(cpp_filename, "w") as f:
        f.write(_PIMPL_DEMO_CPP)
    with open(header_filename, "w") as f:
        f.write(_PIMPL_DEMO_HEADER)
    return cpp_filename, header_filename


def sandbox() -> None:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    cpp_filename = this_dir + "/cpp_tests/my_class_pimpl/my_class.cpp"
    pimpl_my_file(cpp_filename)


if __name__ == "__main__":
    sandbox()
