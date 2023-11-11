from __future__ import annotations
import litgen
from codemanip import code_utils


def test_post_process():
    options = litgen.LitgenOptions()
    code = """
        struct Foo
        {
            int Blah = 0;
        };
    """

    def postprocess_stub(s: str) -> str:
        return s.replace("Foo", "FooPost")

    def postprocess_pydef(s: str) -> str:
        return s.replace("Blah", "BlahPost")

    options.postprocess_pydef_function = postprocess_pydef
    options.postprocess_stub_function = postprocess_stub

    generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class FooPost:
            blah: int = 0
            def __init__(self, blah: int = 0) -> None:
                """Auto-generated default constructor with named params"""
                pass
        ''',
    )

    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassFoo =
            py::class_<Foo>
                (m, "Foo", "")
            .def(py::init<>([](
            int BlahPost = 0)
            {
                auto r = std::make_unique<Foo>();
                r->BlahPost = BlahPost;
                return r;
            })
            , py::arg("blah") = 0
            )
            .def_readwrite("blah", &Foo::BlahPost, "")
            ;
    """,
    )
