from typing import Callable, Iterable

import xml.etree.ElementTree as ET
import copy
from typing import List

import srcml_utils, srcml_caller
from litgen.internal.srcml.srcml_types import CppElementAndComment, CppElement, CppElementComments


COMMENT_NEW_LINE_TOKEN = "_SRCML_LINEFEED_"
EMPTY_LINE_COMMENT_CONTENT = "_SRCML_EMPTY_LINE_"
EMPTY_LINE_COMMENT = "// " + EMPTY_LINE_COMMENT_CONTENT


##################################################
#
#   Group consecutive comments
#
#################################################

_EXAMPLE_COMMENTS_TO_GROUPS = """
/*
A multiline C comment
about Foo1
*/
void Foo1();

// First line of comment on Foo2()
// Second line of comment on Foo2()
void Foo2();

// A lonely comment

//
// Another lonely comment, on two lines
// which ends on this second line, but has surrounding empty lines
//

// A comment on top of Foo3() & Foo4(), which should be kept as a standalone comment
// since Foo3 and Foo4 have end of line comments
Void Foo3(); // Comment on end of line for Foo3()
Void Foo4(); // Comment on end of line for Foo4()
// A comment that shall not be grouped to the previous (which was an EOL comment for Foo4())
"""


EXPECTED_CHILDREN_WITH_COMMENTS = """
{'tag': 'comment', 'name': '', 'text': '_SRCML_EMPTY_LINE_', 'start': '1:1', 'end': '1:21', 'comment_top': '', 'comment_eol': ''}
{'tag': 'function_decl', 'name': 'Foo1', 'text': '', 'start': '6:1', 'end': '6:12', 'comment_top': '\\nA multiline C comment\\nabout Foo1\\n', 'comment_eol': ''}
{'tag': 'comment', 'name': '', 'text': '_SRCML_EMPTY_LINE_', 'start': '7:1', 'end': '7:21', 'comment_top': '', 'comment_eol': ''}
{'tag': 'function_decl', 'name': 'Foo2', 'text': '', 'start': '10:1', 'end': '10:12', 'comment_top': 'First line of comment on Foo2()\\nSecond line of comment on Foo2()', 'comment_eol': ''}
{'tag': 'comment', 'name': '', 'text': '_SRCML_EMPTY_LINE_', 'start': '11:1', 'end': '11:21', 'comment_top': '', 'comment_eol': ''}
{'tag': 'comment', 'name': '', 'text': 'A lonely comment', 'start': '12:1', 'end': '12:19', 'comment_top': '', 'comment_eol': ''}
{'tag': 'comment', 'name': '', 'text': '_SRCML_EMPTY_LINE_', 'start': '13:1', 'end': '13:21', 'comment_top': '', 'comment_eol': ''}
{'tag': 'comment', 'name': '', 'text': '\\nAnother lonely comment, on two lines\\nwhich ends on this second line, but has surrounding empty lines\\n', 'start': '14:1', 'end': '17:2', 'comment_top': '', 'comment_eol': ''}
{'tag': 'comment', 'name': '', 'text': '_SRCML_EMPTY_LINE_', 'start': '18:1', 'end': '18:21', 'comment_top': '', 'comment_eol': ''}
{'tag': 'comment', 'name': '', 'text': 'A comment on top of Foo3() & Foo4(), which should be kept as a standalone comment\\nsince Foo3 and Foo4 have end of line comments', 'start': '19:1', 'end': '20:48', 'comment_top': '', 'comment_eol': ''}
{'tag': 'function_decl', 'name': 'Foo3', 'text': '', 'start': '21:1', 'end': '21:12', 'comment_top': '', 'comment_eol': 'Comment on end of line for Foo3()'}
{'tag': 'function_decl', 'name': 'Foo4', 'text': '', 'start': '22:1', 'end': '22:12', 'comment_top': '', 'comment_eol': 'Comment on end of line for Foo4()'}
{'tag': 'comment', 'name': '', 'text': 'A comment that shall not be grouped to the previous (which was an EOL comment for Foo4())', 'start': '23:1', 'end': '23:92', 'comment_top': '', 'comment_eol': ''}
{'tag': 'comment', 'name': '', 'text': '_SRCML_EMPTY_LINE_', 'start': '24:1', 'end': '24:21', 'comment_top': '', 'comment_eol': ''}
"""


_EXPECTED_COMMENTS_GROUPED = """
unit
    comment text="// _SRCML_EMPTY_LINE_"                    line  1
    comment text="/* A multiline C comment about Foo1 */"   lines 2-5
    function_decl                                           line  6
        type
            name text="void"
        name text="Foo1"
        parameter_list text="()"
    comment text="// _SRCML_EMPTY_LINE_"                    line  7
    comment text="// First line of comment on Foo2()_SRCML_LINEFEED_Second line of comment on Foo2()"lines 8-9
    function_decl                                           line  10
        type
            name text="void"
        name text="Foo2"
        parameter_list text="()"
    comment text="// _SRCML_EMPTY_LINE_"                    line  11
    comment text="// A lonely comment"                      line  12
    comment text="// _SRCML_EMPTY_LINE_"                    line  13
    comment text="//_SRCML_LINEFEED_Another lonely comment, on two lines_SRCML_LINEFEED_which ends on this second line, but has surrounding empty lines_SRCML_LINEFEED_"lines 14-17
    comment text="// _SRCML_EMPTY_LINE_"                    line  18
    comment text="// A comment on top of Foo3() & Foo4(), which should be kept as a standalone comment_SRCML_LINEFEED_since Foo3 and Foo4 have end of line comments"lines 19-20
    function_decl                                           line  21
        type
            name text="Void"
        name text="Foo3"
        parameter_list text="()"
    comment text="// Comment on end of line for Foo3()"
    function_decl                                           line  22
        type
            name text="Void"
        name text="Foo4"
        parameter_list text="()"
    comment text="// Comment on end of line for Foo4()"
    comment text="// A comment that shall not be grouped to the previous (which was an EOL comment for Foo4())"line  23
    comment text="// _SRCML_EMPTY_LINE_"                    line  24
"""


def _mark_empty_lines(code: str) -> str:
    lines = code.split("\n")
    lines2 = list(map(lambda line: EMPTY_LINE_COMMENT if len(line.strip()) == 0 else line, lines))
    result = "\n".join(lines2)
    return result


def _group_consecutive_comments(srcml_code: ET.Element) -> ET.Element:
    srcml_grouped = ET.Element(srcml_code.tag)

    previous_previous_child: ET.Element = None
    previous_child: ET.Element = None

    for child in srcml_code:

        def add_child():
            nonlocal previous_child, previous_previous_child
            child_copy = copy.deepcopy(child)
            srcml_grouped.append(child_copy)
            previous_previous_child = previous_child
            previous_child = child_copy

        def concat_comment():
            current_comment = child.text.strip()[2:].strip()
            previous_child.text += COMMENT_NEW_LINE_TOKEN + current_comment
            srcml_utils.copy_element_end_position(child, previous_child)

        shall_concat_comment = False

        if child.text is not None:
            t = child.text

        if previous_child is not None:
            child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
            previous_tag = srcml_utils.clean_tag_or_attrib(previous_child.tag)
            line = srcml_utils.element_start_position(child).line
            previous_line = srcml_utils.element_end_position(previous_child).line

            # if this statement is a comment and the previous line was also a comment statement
            if (previous_tag == "comment" and child_tag == "comment" and line ==  previous_line + 1):
                # We are almost certain that we should concatenate the comment
                shall_concat_comment = True
                # However, if the previous comment was an end-of-line comment for another C++ statement on the same line
                # we shall not concat
                if previous_previous_child is not None:
                    previous_previous_tag = srcml_utils.clean_tag_or_attrib(previous_previous_child.tag)
                    previous_previous_line = srcml_utils.element_end_position(previous_previous_child).line
                    if previous_previous_line == previous_line and previous_previous_tag != "comment":
                        shall_concat_comment = False
                # Also, if the previous comment was an `EMPTY_LINE_COMMENT` i.e it indicates a voluntarily empty line
                # we shall not concat
                current_comment = child.text
                previous_comment = previous_child.text
                if "_SRCML_EMPTY_LINE_" in previous_comment or "_SRCML_EMPTY_LINE_" in current_comment: # == EMPTY_LINE_COMMENT:
                    shall_concat_comment = False

        if shall_concat_comment:
            concat_comment()
        else:
            add_child()

    children_r = []
    for child_r in srcml_grouped:
        children_r.append(child_r)
    return srcml_grouped


def _is_comment_end_of_line(children: List[ET.Element], idx: int):
    if not 0 <= idx < len(children):
        return False
    if idx == 0:
        return False
    element = CppElement(children[idx])
    previous_element = CppElement(children[idx - 1])
    if element.tag() == "comment" and previous_element.tag() != "comment":
        if EMPTY_LINE_COMMENT_CONTENT in element.text():
            return False
        if element.start().line == previous_element.end().line:
            return True

    return False


def _is_comment_on_previous_line(children: List[ET.Element], idx: int):
    if not 0 <= idx < len(children):
        return False
    if idx == len(children) - 1:
        return False
    if _is_comment_end_of_line(children, idx):
        return False

    element = CppElement(children[idx])
    next_element = CppElement(children[idx + 1])
    if element.tag() == "comment" and next_element.tag() != "comment":
        if EMPTY_LINE_COMMENT_CONTENT in element.text():
            return False
        if element.end().line + 1 == next_element.start().line:
            if idx == len(children) - 2:
                return True
            else:
                next_next_element = CppElement(children[idx +  2])
                if (next_next_element.tag() == "comment" and next_next_element.start().line == next_element.end().line
                    and "return_value_policy::" not in next_next_element.text() ):

                    return False
                else:
                    return True
    return False




def _remove_comment_tokens(comment: str) -> str:
    comment = comment.replace(COMMENT_NEW_LINE_TOKEN, "\n")
    if comment.startswith("/*") and comment.endswith("*/"):
        return comment[2 : -2]
    else:
        lines = comment.split("\n")
        lines_processed = []
        for line in lines:
            if line.lstrip().startswith("// "):
                lines_processed.append(line.lstrip()[3:])
            elif line.lstrip().startswith("//"):
                lines_processed.append(line.lstrip()[2:])
            else:
                lines_processed.append(line.lstrip())
        return "\n".join(lines_processed)


def _group_comments_and_remove_comment_markers(srcml_code: ET.Element) -> ET.Element:
    srcml_code_grouped = _group_consecutive_comments(srcml_code)
    children_comments_grouped: List[ET.Element] = []
    for element in srcml_code_grouped:
        children_comments_grouped.append(element)
    for element in children_comments_grouped:
        if srcml_utils.clean_tag_or_attrib(element.tag) == "comment":
            element.text = _remove_comment_tokens(element.text)
    return children_comments_grouped


def get_children_with_comments(srcml_code: ET.Element) -> List[CppElementAndComment]:
    result = []
    children = _group_comments_and_remove_comment_markers(srcml_code)

    for i, element in enumerate(children):
        cpp_element_comments = CppElementComments()

        shall_append = True

        # Add "comment_on_previous_lines" if applicable...
        if _is_comment_on_previous_line(children, i - 1):
            cpp_element_comments.comment_on_previous_lines = children[i - 1].text
        # and symmetrically, skip if this is a "comment_on_previous_lines"
        if _is_comment_on_previous_line(children, i):
            shall_append = False

        # Add "comment_end_of_line" if applicable
        if _is_comment_end_of_line(children, i + 1):
            cpp_element_comments.comment_end_of_line = children[i + 1].text
        # and symmetrically, skip if this is a "comment_end_of_line"
        if _is_comment_end_of_line(children, i):
            shall_append = False

        if shall_append:
            element_with_comment = CppElementAndComment(element, cpp_element_comments)
            result.append(element_with_comment)

    return result
