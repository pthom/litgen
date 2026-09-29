"""The rules that decide which C++ comment documents which declaration (i.e. becomes its docstring), one case per rule.

The book explains them: chapter "Generated code layout", section "Comments and docstrings".
"""

from __future__ import annotations
from dataclasses import dataclass

import litgen
from codemanip import code_utils
from litgen.litgen_generator import LitgenGeneratorTestsHelper


@dataclass
class _CommentRule:
    rule: str
    cpp_code: str
    expected_stub: str
    # the option srcmlcpp_options.comment_above_is_doc_when_next_has_eol_comment
    with_option: bool = False


COMMENT_RULES = [
    _CommentRule(
        rule="A comment at the end of a declaration's line documents it",
        cpp_code="""
        void Foo(); // Doc of Foo
        """,
        expected_stub='''
        def foo() -> None:
            """ Doc of Foo"""
            pass
        ''',
    ),
    _CommentRule(
        rule="A comment on the lines directly above a declaration documents it",
        cpp_code="""
        // Doc of Foo,
        // on two lines
        void Foo();
        """,
        expected_stub='''
        def foo() -> None:
            """ Doc of Foo,
             on two lines
            """
            pass
        ''',
    ),
    _CommentRule(
        rule="When the declaration also has an end-of-line comment, it wins: the comment above stays standalone",
        cpp_code="""
        // A title
        void Foo(); // Doc of Foo
        """,
        expected_stub='''
        # A title
        def foo() -> None:
            """ Doc of Foo"""
            pass
        ''',
    ),
    _CommentRule(
        rule="A comment followed by an empty line is standalone (a section title)",
        cpp_code="""
        // A section title

        void Foo();
        """,
        expected_stub="""
        # A section title

        def foo() -> None:
            pass
        """,
    ),
    _CommentRule(
        rule="A comment directly above several declarations of the same kind, on consecutive lines, "
        "is a group comment: it stays standalone",
        cpp_code="""
        // About Foo and Bar
        void Foo();
        void Bar();
        """,
        expected_stub="""
        # About Foo and Bar
        def foo() -> None:
            pass
        def bar() -> None:
            pass
        """,
    ),
    _CommentRule(
        rule="By default, it is a group comment also when the next declaration has an end-of-line comment "
        "(imgui.h writes its section titles this way)",
        cpp_code="""
        // About Foo and Bar
        void Foo();
        void Bar(); // Doc of Bar
        """,
        expected_stub='''
        # About Foo and Bar
        def foo() -> None:
            pass
        def bar() -> None:
            """ Doc of Bar"""
            pass
        ''',
    ),
    _CommentRule(
        rule="With the option, the comment above documents the declaration when the next one has an end-of-line comment",
        with_option=True,
        cpp_code="""
        // Doc of Foo
        void Foo();
        void Bar(); // Doc of Bar
        """,
        expected_stub='''
        def foo() -> None:
            """ Doc of Foo"""
            pass
        def bar() -> None:
            """ Doc of Bar"""
            pass
        ''',
    ),
    _CommentRule(
        rule="With the option, when the next declaration has no end-of-line comment, it is still a group comment",
        with_option=True,
        cpp_code="""
        // About Foo and Bar
        void Foo();
        void Bar();
        """,
        expected_stub="""
        # About Foo and Bar
        def foo() -> None:
            pass
        def bar() -> None:
            pass
        """,
    ),
    _CommentRule(
        rule="The overloads are grouped (mypy needs them adjacent): the comment above a later overload moves with it",
        cpp_code="""
        void Foo(int a);
        void Bar();
        // About Foo(int, float)
        void Foo(int a, float b);
        void Baz();
        """,
        expected_stub="""
        @overload
        def foo(a: int) -> None:
            pass
        # About Foo(int, float)
        @overload
        def foo(a: int, b: float) -> None:
            pass
        def bar() -> None:
            pass
        def baz() -> None:
            pass
        """,
    ),
    _CommentRule(
        rule="With the option, each overload keeps the comment above it as its docstring",
        with_option=True,
        cpp_code="""
        // Doc of Foo(int)
        void Foo(int a);
        // Doc of Foo(int, float)
        void Foo(int a, float b);
        void Bar(); // Doc of Bar
        """,
        expected_stub='''
        @overload
        def foo(a: int) -> None:
            """ Doc of Foo(int)"""
            pass
        @overload
        def foo(a: int, b: float) -> None:
            """ Doc of Foo(int, float)"""
            pass
        def bar() -> None:
            """ Doc of Bar"""
            pass
        ''',
    ),
    _CommentRule(
        rule="The same rules hold for a class; a member's comment stays a comment next to it (a field has no docstring)",
        cpp_code="""
        // Doc of Point
        struct Point
        {
            int x = 0; // The x coordinate
        };
        """,
        expected_stub='''
        class Point:
            """ Doc of Point"""
            x: int = 0  # The x coordinate
            def __init__(self, x: int = 0) -> None:
                """Auto-generated default constructor with named params"""
                pass
        ''',
    ),
]


def test_comment_rules() -> None:
    for case in COMMENT_RULES:
        options = litgen.LitgenOptions()
        options.srcmlcpp_options.comment_above_is_doc_when_next_has_eol_comment = case.with_option
        generated_stub = LitgenGeneratorTestsHelper.code_to_stub(options, case.cpp_code)
        try:
            code_utils.assert_are_codes_equal(generated_stub, case.expected_stub)
        except AssertionError as e:
            raise AssertionError(f"Comment rule broken: {case.rule}") from e
