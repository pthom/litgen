from code_types import *
from options import CodeStyleOptions


def extract_code_region_comments(struct_or_enum_code: PydefCode, code_style_options: CodeStyleOptions) -> List[CodeRegionComment]:
    """
    If code_doc_style.flag_attribute_comment_on_line_before == True,
        then code region comments look like this
            //
            // This is a code region comment.
            // It can have several lines, but needs to have an empty comment before and after
            //
    If code_doc_style.flag_attribute_comment_on_line_before == False,
        then code region comments look like this
            // This is a code region comment. It can span a single line. It will not be considered a doc for the next attribute
    """
    code_lines = struct_or_enum_code.body_code_cpp.split("\n")
    code_lines = map(lambda s: s.strip(), code_lines)
    numbered_code_lines = list(enumerate(code_lines))

    def get_code_line(line_number: int) -> str:
        return numbered_code_lines[line_number][1]

    def is_comment_line(line_number):
        return get_code_line(line_number).startswith("//")

    def is_new_comment_line(line_number):
        if line_number < 1:
            return False
        this_line = get_code_line(line_number)
        previous_line = get_code_line(line_number - 1)
        r = this_line.startswith("//") and not previous_line.startswith("//")
        return r

    def is_end_comment_line(line_number):
        return line_number > 1 and not is_comment_line(line_number) and is_comment_line(line_number - 1)

    def is_empty_comment(line_number):
        return get_code_line(line_number).strip() == "//"

    def is_filled_comment(line_number):
        c = get_code_line(line_number)
        return c.strip().startswith("//") and len(c[2:].strip()) > 0

    def get_filled_comment(line_number):
        assert (is_filled_comment(line_number))
        c = get_code_line(line_number)
        return c.strip()[2:].strip()

    def append_line(str1, str2):
        if len(str1) == 0:
            return str2
        else:
            return str1 + "\n" + str2

    flag_title_on_previous_line = (code_style_options.enum_title_on_previous_line
                                   or (struct_or_enum_code.code_type == CppCodeType.STRUCT))

    if flag_title_on_previous_line:
        all_code_region_comments = []
        current_code_region_comment = None
        for line_number, code_line in numbered_code_lines:
            if is_empty_comment(line_number) and current_code_region_comment is None:
                current_code_region_comment = CodeRegionComment()
                current_code_region_comment.line_number = line_number
            elif is_empty_comment(line_number) and current_code_region_comment is not None:
                all_code_region_comments.append(current_code_region_comment)
                current_code_region_comment = None
            elif is_filled_comment(line_number) and current_code_region_comment is not None:
                current_code_region_comment.comment_cpp = \
                    append_line(current_code_region_comment.comment_cpp, get_filled_comment(line_number))
    else:
        all_code_region_comments = []
        current_code_region_comment = None
        for line_number, code_line in numbered_code_lines:
            if current_code_region_comment is None and is_new_comment_line(line_number):
                current_code_region_comment = CodeRegionComment()
                current_code_region_comment.line_number = line_number
            elif is_end_comment_line(line_number) and current_code_region_comment is not None:
                all_code_region_comments.append(current_code_region_comment)
                current_code_region_comment = None
            if is_filled_comment(line_number) and current_code_region_comment is not None:
                current_code_region_comment.comment_cpp = \
                    append_line(current_code_region_comment.comment_cpp, get_filled_comment(line_number))

    return all_code_region_comments
