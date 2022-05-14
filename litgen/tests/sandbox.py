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


def test_struct():
    code = '''
    // A superb struct
    struct Foo            // MY_API_STRUCT
    {
        // default constructor
        Foo(int x) {}
        ~Foo() {}

        // Do some math
        //int calc(int x) { return x * factor + delta; }
        
        static Foo& Instance() { static Foo instance; return instance; } // return_value_policy::reference

    };
        '''
    struct_info = struct_parser.parse_one_struct_testonly(code, options)
    generated_code = struct_generator.generate_pydef_struct_cpp_code(struct_info, options)
    print(generated_code)


test_struct()