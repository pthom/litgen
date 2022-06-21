import os
import sys

from codemanip import code_utils

import srcmlcpp
from srcmlcpp import srcml_comments, srcml_utils


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def test_mark_empty_lines():
    code = srcml_comments._EXAMPLE_COMMENTS_TO_GROUPS
    code2 = srcml_comments.mark_empty_lines(code)
    lines2 = code2.split("\n")
    lines2_empty = list(filter(lambda line: line == srcml_comments.EMPTY_LINE_COMMENT, lines2))
    assert len(lines2_empty) > 4


def test_group_consecutive_comment():
    code = srcml_comments.mark_empty_lines(srcml_comments._EXAMPLE_COMMENTS_TO_GROUPS)
    srcml_code = srcmlcpp.srcml_caller.code_to_srcml(code)
    srcml_grouped = srcml_comments._group_consecutive_comments(srcml_code)
    grouped_str = srcml_utils.srcml_to_str_readable(srcml_grouped)
    # logging.warning("\n" + grouped_str)
    code_utils.assert_are_codes_equal(grouped_str, srcml_comments._EXPECTED_COMMENTS_GROUPED)


def test_iterate_children_simple():
    code = """

    void Boo1();
    void Boo2(); // get y
    void Boo3();

    """
    code = srcml_comments.mark_empty_lines(code)
    srcml_code = srcmlcpp.srcml_caller.code_to_srcml(code)
    children_and_comments = srcml_comments.get_children_with_comments(srcml_code)
    msgs = [str(child.as_dict()) for child in children_and_comments]
    msg = "\n".join(msgs)
    # logging.warning("\n" + msg)
    expected = """
        {'tag': 'comment', 'name': '__NONE__', 'text': ' _SRCML_EMPTY_LINE_', 'start': '1:1', 'end': '1:21', 'comment_top': '', 'comment_eol': ''}
        {'tag': 'comment', 'name': '__NONE__', 'text': ' _SRCML_EMPTY_LINE_', 'start': '2:1', 'end': '2:21', 'comment_top': '', 'comment_eol': ''}
        {'tag': 'function_decl', 'name': 'Boo1', 'text': '', 'start': '3:5', 'end': '3:16', 'comment_top': '', 'comment_eol': ''}
        {'tag': 'function_decl', 'name': 'Boo2', 'text': '', 'start': '4:5', 'end': '4:16', 'comment_top': '', 'comment_eol': ' get y'}
        {'tag': 'function_decl', 'name': 'Boo3', 'text': '', 'start': '5:5', 'end': '5:16', 'comment_top': '', 'comment_eol': ''}
        {'tag': 'comment', 'name': '__NONE__', 'text': ' _SRCML_EMPTY_LINE_', 'start': '6:1', 'end': '6:21', 'comment_top': '', 'comment_eol': ''}
        {'tag': 'comment', 'name': '__NONE__', 'text': ' _SRCML_EMPTY_LINE_', 'start': '7:1', 'end': '7:21', 'comment_top': '', 'comment_eol': ''}
    """

    code_utils.assert_are_codes_equal(msg, expected)


def test_iterate_children_with_comments():
    code = srcml_comments.mark_empty_lines(srcml_comments._EXAMPLE_COMMENTS_TO_GROUPS)
    srcml_code = srcmlcpp.srcml_caller.code_to_srcml(code)
    children_and_comments = srcml_comments.get_children_with_comments(srcml_code)
    msgs = [str(child.as_dict()) for child in children_and_comments]
    msg = "\n".join(msgs)
    # logging.warning("\n" + msg)
    code_utils.assert_are_codes_equal(msg, srcml_comments._EXPECTED_CHILDREN_WITH_COMMENTS)


def test_group_comment():
    code = """
    // A comment about
    // several functions
    MY_API void Foo();
    MY_API void Foo2();
    MY_API void Foo3();
    """[
        1:
    ]
    code = srcml_comments.mark_empty_lines(code)
    srcml_code = srcmlcpp.srcml_caller.code_to_srcml(code)
    children_and_comments = srcml_comments.get_children_with_comments(srcml_code)
    assert children_and_comments[0].tag() == "comment"
    assert children_and_comments[1].tag() == "function_decl"
    assert children_and_comments[2].tag() == "function_decl"
    assert children_and_comments[3].tag() == "function_decl"
