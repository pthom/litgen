import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
import code_region_comment_parser
import find_functions_structs_enums
from code_types import *
from options import CodeStyleOptions


def test_extract_code_region_comments():
    # Policy 1 (for Enums only): if members_title_on_previous_line==False:
    code = """
            // Plot style structure
            // Another line in the title
            enum ImPlotStyle {
                // item styling variables
                float   LineWeight;              // = 1, item line weight  <=== member title begins after //
                int     Marker;                  // = ImPlotMarker_None, marker specification
                // plot styling variables
                float   PlotBorderSize;          // = 1,      line thickness of border around plot area
            };
    """
    options = CodeStyleOptions()
    options.enum_title_on_previous_line = False
    pydef_enums = find_functions_structs_enums.find_functions_struct_or_enums(code, CppCodeType.ENUM_CPP_98, options)
    assert len(pydef_enums) == 1
    pydef_enum = pydef_enums[0]
    code_region_comments = code_region_comment_parser.extract_code_region_comments(pydef_enum, options)
    assert len(code_region_comments) == 2
    assert code_region_comments[1].docstring_cpp == "plot styling variables"
    assert code_region_comments[1].line_number == 4


    # Policy 2, if members_title_on_previous_line==True:
    code = """
            // Set of display parameters and options for an Image
            struct ImageParams  // IMMVISION_API_STRUCT
            {
                //
                // ImageParams store the parameters for a displayed image
                // Bla, bla, bla
                //


                // Refresh Image: set to true if your image matrix/buffer has changed
                // (for example, for live video images)
                bool RefreshImage = false;
            };
            """
    options = CodeStyleOptions()
    options.enum_title_on_previous_line = True
    pydef_enums = find_functions_structs_enums.find_functions_struct_or_enums(code, CppCodeType.STRUCT, options)
    assert len(pydef_enums) == 1
    pydef_enum = pydef_enums[0]
    code_region_comments = code_region_comment_parser.extract_code_region_comments(pydef_enum, options)
    assert len(code_region_comments) == 1
    assert code_region_comments[0].docstring_cpp == "ImageParams store the parameters for a displayed image\nBla, bla, bla"
    assert code_region_comments[0].line_number == 1
