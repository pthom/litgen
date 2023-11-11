from __future__ import annotations
import os
import sys

from codemanip import code_utils

from srcmlcpp.internal import filter_preprocessor_regions, code_to_srcml


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def test_preprocessor_test_state_and_inclusion_guards():
    header_acceptable_ifndef__regex = "_H$|ACCEPTED$"
    code = filter_preprocessor_regions._EXAMPLE_HEADER_FILE
    xml_header = code_to_srcml.code_to_srcml(code)
    xml_header_filtered = filter_preprocessor_regions.filter_preprocessor_regions(
        xml_header, header_acceptable_ifndef__regex
    )
    header_filtered = code_to_srcml.srcml_to_code(xml_header_filtered)
    code_utils.assert_are_codes_equal(header_filtered, filter_preprocessor_regions._EXPECTED_FILTERED_HEADER)
