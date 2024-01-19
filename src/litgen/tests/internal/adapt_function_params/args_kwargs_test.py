from __future__ import annotations
from codemanip import code_utils

import litgen


# cf https://pybind11.readthedocs.io/en/stable/advanced/functions.html#accepting-args-and-kwargs
def test_args_kwarg() -> None:
    code = """
    void generic(py::args args, const py::kwargs& kwargs)
    {
        /// .. do something with args
        // if (kwargs)
            /// .. do something with kwargs
    }
    """
    options = litgen.LitgenOptions()
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("generic",
            generic);
        """,
    )
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def generic(*args, **kwargs) -> None:
            pass
        """,
    )
