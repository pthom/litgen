import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
import litgen
from litgen.internal import function_generator, function_parser


options = litgen.code_style_implot()
options.functions_api_prefixes = ["MY_API"]

code = '''
    MY_API inline void add_inside_array(int8_t* array, int array_size, int number_to_add);
    '''
function_info = function_parser.parse_one_function_declaration(code, options)
generated_code = function_generator.generate_pydef_function_cpp_code(function_info, options)
print(generated_code)
