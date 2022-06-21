from srcmlcpp import srcml_main
from srcmlcpp.srcml_types import *

import litgen
from litgen.internal.adapted_types import *
from litgen.options import LitgenOptions


def to_adapted_decl(code, options: LitgenOptions) -> AdaptedDecl:
    cpp_decl = srcml_main.code_first_decl(options.srcml_options, code)
    adapted_decl = AdaptedDecl(cpp_decl, options)
    return adapted_decl


def test_c_array_fixed_size_to_std_array():
    options = litgen.LitgenOptions()
    options.srcml_options.named_number_macros = {"COUNT": 3}

    code = "const int v[COUNT]"
    adapted_decl = to_adapted_decl(code, options)
    new_adapted_decl = adapted_decl.c_array_fixed_size_to_const_std_array()
    code_utils.assert_are_codes_equal(str(new_adapted_decl.cpp_element()), "const std::array<int, 3>& v")

    code = "const unsigned int v[3]"
    adapted_decl = to_adapted_decl(code, options)
    new_adapted_decl = adapted_decl.c_array_fixed_size_to_const_std_array()
    code_utils.assert_are_codes_equal(str(new_adapted_decl.cpp_element()), "const std::array<unsigned int, 3>& v")

    code = "int v[2]"
    adapted_decl = to_adapted_decl(code, options)
    new_decls = adapted_decl.c_array_fixed_size_to_mutable_new_boxed_decls()
    assert len(new_decls) == 2
    code_utils.assert_are_codes_equal(str(new_decls[0].cpp_element()), "BoxedInt & v_0")
    code_utils.assert_are_codes_equal(str(new_decls[1].cpp_element()), "BoxedInt & v_1")


def test_adapted_enum():
    options = litgen.LitgenOptions()
    options.srcml_options.named_number_macros = {"MY_VALUE": 256}

    code = """
// Doc about Foo
// On several lines
enum Foo
{
    Foo_a, // This is a

    // And this is b and c's comment
    Foo_b,
    Foo_c = MY_VALUE,

    Foo_d = Foo_a | Foo_b + Foo_c, // And a computed value

    Foo_e = 4,

    Foo_count, // And this is count
};
    """
    enum = srcml_main.code_first_enum(options.srcml_options, code)
    adapted_enum = AdaptedEnum(enum, options)
    decls = adapted_enum.get_adapted_decls()

    # Test parsing and adapt: count should be removed, members should be renamed, comment should be processed
    assert len(decls) == 5  # Foo_count should have been removed (becua
    assert decls[0].cpp_element().initial_value_code == "0"
    assert decls[0].cpp_element().cpp_element_comments.comment_end_of_line == " This is a"
    assert decls[1].cpp_element().initial_value_code == "1"
    assert decls[2].cpp_element().initial_value_code == "256"
    assert decls[3].cpp_element().initial_value_code == "Foo_a | Foo_b + Foo_c"

    # Test generated stub code (with python_reproduce_cpp_layout=True)
    options.python_reproduce_cpp_layout = True
    stub_code = str(adapted_enum)
    # logging.warning("\n>>>" + stub_code + "<<<")
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo(Enum):
            """ Doc about Foo
             On several lines
            """
            a = 0                                                 # This is a

            #  And this is b and c's comment
            b = 1
            c = 256

            d = Literal[Foo.a] | Literal[Foo.b] + Literal[Foo.c]  # And a computed value

            e = 4
    ''',
    )

    # Test generated stub code (with python_reproduce_cpp_layout=False)
    options.python_reproduce_cpp_layout = False
    stub_code = str(adapted_enum)
    # logging.warning("\n>>>" + stub_code + "<<<")
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo(Enum):
            """ Doc about Foo
             On several lines
            """
            #  This is a
            a = 0
            #  And this is b and c's comment
            b = 1
            c = 256
            #  And a computed value
            d = Literal[Foo.a] | Literal[Foo.b] + Literal[Foo.c]
            e = 4
        ''',
    )

    # Test generated pydef code
    options.original_location_flag_show = True
    pydef_code = adapted_enum.str_pydef()
    # logging.warning("\n>>>" + pydef_code + "<<<")
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        py::enum_<Foo>(m, "Foo", py::arithmetic(), " Doc about Foo\\n On several lines")    // Line:4
            .value("a", Foo_a, "This is a")
            .value("b", Foo_b, "")
            .value("c", Foo_c, "")
            .value("d", Foo_d, "And a computed value")
            .value("e", Foo_e, "");
    """,
    )


def test_adapted_function_stub():
    options = litgen.LitgenOptions()
    options.original_location_flag_show = True

    code = """
    // This is foo's doc:
    //     :param buffer & count: modifiable buffer and its size
    //     :param out_values: output double values
    //     :param in_flags: input bool flags
    //     :param text and ... : formatted text
    void Foo(uint8_t * buffer, size_t count, double out_values[2], const bool in_flags[2], const char* text, ...);
    """
    fn = srcml_main.code_first_function_decl(options.srcml_options, code)
    struct_name = ""
    adapted_function = AdaptedFunction(fn, struct_name, options)

    stub_code = adapted_function.str_stub()
    # logging.warning("\n>>>" + stub_code + "<<<")
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        def foo(    # Line:7
            buffer: numpy.ndarray,
            out_values_0: BoxedDouble,
            out_values_1: BoxedDouble,
            in_flags: List[bool],
            text: str
            ) -> None:
            """ This is foo's doc:
                 :param buffer  count: modifiable buffer and its size
                 :param out_values: output float values
                 :param in_flags: input bool flags
                 :param text and ... : formatted text
            """
            pass
    ''',
    )


def test_adapted_function_pydef_simple():
    options = litgen.LitgenOptions()
    code = """
    int add(int a, int b) { return a + b; }
    """
    fn = srcml_main.code_first_function_decl(options.srcml_options, code)
    struct_name = ""
    adapted_function = AdaptedFunction(fn, struct_name, options)

    pydef_code = adapted_function.str_pydef()
    # logging.warning("\n>>>" + pydef_code + "<<<")
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        m.def("add",
            [](int a, int b)
            {
                return add(a, b);
            },
            py::arg("a"), py::arg("b")
        );
    """,
    )


def test_adapted_struct():
    options = litgen.LitgenOptions()
    options.srcml_options.named_number_macros = {"MY_VALUE": 256}

    code = """
// Doc about Foo
struct Foo
{
    int a;
    int add(int v) { return v + a; }
};
    """
    class_ = srcml_main.code_first_struct(options.srcml_options, code)
    adapted_class = AdaptedClass(class_, options)

    pydef_code = adapted_class.str_pydef()
    # logging.warning("\n>>>" + pydef_code + "<<<")
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        auto pyClassFoo = py::class_<Foo>
            (m, "Foo", "Doc about Foo")
            .def(py::init<>()) // implicit default constructor
            .def_readwrite("a", &Foo::a, "")
            .def("add",
                [](Foo & self, int v)
                {
                    return self.add(v);
                },
                py::arg("v")
            )
            ;
    """,
    )
