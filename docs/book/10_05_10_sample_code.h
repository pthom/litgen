
// This will trigger a warning:
//     Ignoring template function. You might need to set LitgenOptions.fn_template_options
//     While parsing a "function_decl", corresponding to this C++ code:
//    Position:4:1
//        template<typename T> void MyOperation(T value);
template<typename T> void MyOperation(T value);


struct Foo {};


// This will generate a warning:
//    operators are supported only when implemented as a member functions
// And this operator will not be exported
bool operator==(const Foo& v1, const Foo& v2);


// litgen does not support C-style function parameters
// This function will trigger a warning: "Can't use a function_decl as a param"
int CallOperation(int (*functionPtr)(int, int), int a, int b) {
    return (*functionPtr)(a, b);
}
