from __future__ import annotations
import litgen
from codemanip import code_utils


def test_tpl_with_iterable():
    options = litgen.LitgenOptions()
    options.class_template_options.add_specialization(
        name_regex="MyData", cpp_types_list_str=["int"], cpp_synonyms_list_str=[]
    )
    options.class_iterables_infos.add_iterable_class("^MyData", "int")
    code = """
            struct MyData {
                int* begin();
                int* end();
                int size();
            };
                """
    generated_code = litgen.generate_code(options, code)

    # print("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassMyData =
            py::class_<MyData>
                (m, "MyData", "")
            .def(py::init<>()) // implicit default constructor
            .def("begin",
                &MyData::begin)
            .def("end",
                &MyData::end)
            .def("size",
                &MyData::size)
            .def("__iter__", [](const MyData &v) { return py::make_iterator(v.begin(), v.end()); }, py::keep_alive<0, 1>())
            .def("__len__", [](const MyData &v) { return v.size(); })
            ;
        """,
    )

    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class MyData:
            def begin(self) -> int:
                pass
            def end(self) -> int:
                pass
            def size(self) -> int:
                pass
            def __init__(self) -> None:
                """Auto-generated default constructor"""
                pass
            def __iter__(self) -> Iterator[int]:
                pass
            def __len__(self) -> int:
                pass
        ''',
    )
