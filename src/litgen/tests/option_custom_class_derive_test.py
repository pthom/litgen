from __future__ import annotations
from codemanip import code_utils
import litgen

def test_custom_classes_base_option():
    """
    Example of how the callback mechanism could be used in practice to handle reference return policies
    """

    def handle_classes_base(cls, for_python_stub):
        
        bases = []

        elem = cls.cpp_element()
        
        if elem.class_name == "SecondClass":
            bases.append("FirstClass" if for_python_stub else "CustomNS::FirstClass")

        return bases
    
    """
    ## First class is in another file, and won't be handled by litgen for another files

        namespace CustomNS {
            class FirstClass {
            public:
                FirstClass();
            private:
                int _value1;
            };
        }
    """

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

    options = litgen.LitgenOptions()
    options.class_base_custom_derivation__callback = handle_classes_base
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
