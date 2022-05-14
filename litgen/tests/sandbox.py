import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
import litgen
from litgen.internal import function_generator, function_parser, struct_parser, struct_generator


options = litgen.code_style_implot()
options.functions_api_prefixes = ["MY_API"]


def test_function():
    code = '''
        int Foo() { return 43; }
        '''
    function_info = function_parser.parse_one_function_declaration(code, options)
    generated_code = function_generator.generate_pydef_function_cpp_code(function_info, options)
    print(generated_code)


struct_code = '''
struct Foo            // MY_API_STRUCT
{
        //
        // And these are our calculations
        //

        // Do some math
        int calc(int x) { return x * factor + delta; }
};
'''


def test_struct_pydef():
    struct_info = struct_parser.parse_one_struct_testonly(struct_code, options)
    generated_code = struct_generator.generate_pydef_struct_cpp_code(struct_info, options)
    print(generated_code)


def test_struct_stub():
    struct_info = struct_parser.parse_one_struct_testonly(struct_code, options)
    generated_code = struct_generator.generate_stub_pyi(struct_info, options)
    print(generated_code)


# test_struct_pydef()
test_struct_stub()