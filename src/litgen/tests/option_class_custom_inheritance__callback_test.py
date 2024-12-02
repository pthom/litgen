from __future__ import annotations
from codemanip import code_utils
import litgen
from litgen.internal.adapted_types import AdaptedClass
from litgen import GeneratedCodeType


def test_class_custom_inheritance__callback():
    """Example of how the callback mechanism `options.class_custom_inheritance__callback`
    can be used in practice to add a base class
    """

    # Let's suppose that we have the following C++ code in another file,
    # which was not processed by litgen (or not yet)
    """
        namespace CustomNS {
            class FirstClass {
            public:
                FirstClass();
            private:
                int _value1;
            };
        }
    """

    # And we are processing the following code:
    code = """
        class SecondClass : CustomNS::FirstClass {
        public:
            SecondClass();
        private:
            int _value2;
        };

        class ThirdClass : SecondClass {
        public:
            ThirdClass();
        private:
            int _value3;
        };
    """

    # This will be our callback to add the base class: it returns the base class which we should add
    # (with a syntax that depends slightly on the generated code type)
    def handle_classes_base(cls: AdaptedClass, generated_code_type: GeneratedCodeType) -> list[str]:
        bases = []
        elem = cls.cpp_element()
        if elem.class_name == "SecondClass":
            bases.append("FirstClass" if generated_code_type == GeneratedCodeType.stub else "CustomNS::FirstClass")
        return bases

    options = litgen.LitgenOptions()
    options.class_custom_inheritance__callback = handle_classes_base
    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassSecondClass =
            py::class_<SecondClass, CustomNS::FirstClass>
                (m, "SecondClass", "")
            .def(py::init<>())
            ;


        auto pyClassThirdClass =
            py::class_<ThirdClass, SecondClass>
                (m, "ThirdClass", "")
            .def(py::init<>())
            ;
      """,
    )

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        class SecondClass(FirstClass):
            def __init__(self) -> None:
                pass

        class ThirdClass(SecondClass):
            def __init__(self) -> None:
                pass
      """,
    )
