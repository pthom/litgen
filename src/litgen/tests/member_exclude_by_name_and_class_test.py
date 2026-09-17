import litgen
from codemanip import code_utils


def test_member_exclude_by_name_and_class_applies_to_members_and_methods():
    code = """
    struct Foo { int bar(); int baz(); int Size; };
    struct Other { int bar(); int Size; };
    """
    options = litgen.LitgenOptions()
    options.member_exclude_by_name_and_class__regex = {"Foo": r"^bar$|^Size$"}
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        class Foo:
            def baz(self) -> int:
                pass
            def __init__(self) -> None:
                \"\"\"Auto-generated default constructor\"\"\"
                pass
        class Other:
            def bar(self) -> int:
                pass
            size: int
            def __init__(self, size: int = int()) -> None:
                \"\"\"Auto-generated default constructor with named params\"\"\"
                pass
        """,
    )


def test_member_exclude_by_name_and_class_applies_to_template_specializations():
    code = """
    template<typename T>
    struct ImVector {
        int Size; T* Data;
        inline int size() const { return Size; }
        inline T* begin() { return Data; }
    };
    """
    options = litgen.LitgenOptions()
    options.class_template_options.add_specialization(
        name_regex="^ImVector$", cpp_types_list_str=["int"], cpp_synonyms_list_str=[]
    )
    options.member_exclude_by_name_and_class__regex = {"ImVector": r"^Size$|^Data$|^begin$"}
    generated_code = litgen.generate_code(options, code)
    assert "def size(self) -> int:" in generated_code.stub_code
    assert "begin" not in generated_code.stub_code
    assert "data" not in generated_code.stub_code.replace("Auto-generated", "")
