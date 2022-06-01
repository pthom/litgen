import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/../.."] + sys.path

from litgen.internal import code_utils
from litgen.internal import srcml
from litgen.internal.srcml import srcml_filter_preprocessor_regions, srcml_caller


def test_preprocessor_test_state_and_inclusion_guards():
    header_guard_suffixes = ["_H"]
    code = srcml_filter_preprocessor_regions._EXAMPLE_HEADER_FILE
    xml_header = srcml.code_to_srcml(code)
    xml_header_filtered = srcml_filter_preprocessor_regions.filter_preprocessor_regions(xml_header, header_guard_suffixes)
    header_filtered = srcml_caller.srcml_to_code(xml_header_filtered)
    code_utils.assert_are_codes_equal(header_filtered, srcml_filter_preprocessor_regions._EXPECTED_FILTERED_HEADER)
