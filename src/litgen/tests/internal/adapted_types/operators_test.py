from __future__ import annotations
from codemanip import code_utils

import litgen


def test_operators():
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"
    code = """
        struct IntWrapper
        {
            int value;
            IntWrapper(int v) : value(v) {}

            // arithmetic operators
            MY_API IntWrapper operator+(IntWrapper b) { return IntWrapper{ value + b.value}; }
            MY_API IntWrapper operator-(IntWrapper b) { return IntWrapper{ value - b.value }; }

            // Unary minus operator
            MY_API IntWrapper operator-() { return IntWrapper{ -value }; }

            // Comparison operator
            MY_API bool operator<(IntWrapper b) { return value < b.value; }

            // Two overload of the += operator
            MY_API IntWrapper operator+=(IntWrapper b) { value += b.value; return *this; }
            MY_API IntWrapper operator+=(int b) { value += b; return *this; }

            // Two overload of the call operator, with different results
            MY_API int operator()(IntWrapper b) { return value * b.value + 2; }
            MY_API int operator()(int b) { return value * b + 3; }
        };
    """

    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class IntWrapper:
            value: int
            def __init__(self, v: int) -> None:
                pass

            # arithmetic operators
            def __add__(self, b: IntWrapper) -> IntWrapper:
                pass
            @overload
            def __sub__(self, b: IntWrapper) -> IntWrapper:
                pass

            @overload
            def __neg__(self) -> IntWrapper:
                """ Unary minus operator"""
                pass

            def __lt__(self, b: IntWrapper) -> bool:
                """ Comparison operator"""
                pass

            # Two overload of the += operator
            @overload
            def __iadd__(self, b: IntWrapper) -> IntWrapper:
                pass
            @overload
            def __iadd__(self, b: int) -> IntWrapper:
                pass

            # Two overload of the call operator, with different results
            @overload
            def __call__(self, b: IntWrapper) -> int:
                pass
            @overload
            def __call__(self, b: int) -> int:
                pass
    ''',
    )


def test_scoping():
    options = litgen.LitgenOptions()
    code = """
        struct S {
            S f(S& o);
        };
    """
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class S:
            def f(self, o: S) -> S:
                pass
            def __init__(self) -> None:
                """Auto-generated default constructor"""
                pass
     ''',
    )


def test_spaceship_operator():
    options = litgen.LitgenOptions()
    code = """
        struct IntWrapperSpaceship
        {
            int value;

            IntWrapperSpaceship(int v): value(v) {}

            int operator<=>(IntWrapperSpaceship& o) { return value - o.value; }
        };
    """

    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        class IntWrapperSpaceship:
            value: int

            def __init__(self, v: int) -> None:
                pass

            def __lt__(self, o: IntWrapperSpaceship) -> bool:
                pass
            def __le__(self, o: IntWrapperSpaceship) -> bool:
                pass
            def __eq__(self, o: IntWrapperSpaceship) -> bool:
                pass
            def __ge__(self, o: IntWrapperSpaceship) -> bool:
                pass
            def __gt__(self, o: IntWrapperSpaceship) -> bool:
                pass
    """,
    )

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassIntWrapperSpaceship =
            py::class_<IntWrapperSpaceship>
                (m, "IntWrapperSpaceship", "")
            .def_readwrite("value", &IntWrapperSpaceship::value, "")
            .def(py::init<int>(),
                py::arg("v"))
            .def("__lt__",
                [](IntWrapperSpaceship & self, IntWrapperSpaceship & o) -> bool
                {
                    auto cmp = [&self](auto&& other) -> bool {
                        return self.operator<=>(other)  < 0;
                    };

                    return cmp(o);
                },     py::arg("o"))
            .def("__le__",
                [](IntWrapperSpaceship & self, IntWrapperSpaceship & o) -> bool
                {
                    auto cmp = [&self](auto&& other) -> bool {
                        return self.operator<=>(other)  <= 0;
                    };

                    return cmp(o);
                },     py::arg("o"))
            .def("__eq__",
                [](IntWrapperSpaceship & self, IntWrapperSpaceship & o) -> bool
                {
                    auto cmp = [&self](auto&& other) -> bool {
                        return self.operator<=>(other)  == 0;
                    };

                    return cmp(o);
                },     py::arg("o"))
            .def("__ge__",
                [](IntWrapperSpaceship & self, IntWrapperSpaceship & o) -> bool
                {
                    auto cmp = [&self](auto&& other) -> bool {
                        return self.operator<=>(other)  >= 0;
                    };

                    return cmp(o);
                },     py::arg("o"))
            .def("__gt__",
                [](IntWrapperSpaceship & self, IntWrapperSpaceship & o) -> bool
                {
                    auto cmp = [&self](auto&& other) -> bool {
                        return self.operator<=>(other)  > 0;
                    };

                    return cmp(o);
                },     py::arg("o"))
            ;
    """,
    )
