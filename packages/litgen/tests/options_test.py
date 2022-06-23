from codemanip import code_replacements
import litgen


def test_multiple_options_instances():
    options1 = litgen.options.code_style_implot()
    options2 = litgen.LitgenOptions()
    assert id(options1) != id(options2)
    assert id(options1.srcml_options) != id(options2.srcml_options)
    assert len(options2.srcml_options.functions_api_prefixes) == 0


def test_standard_replacements():
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = code_replacements.apply_code_replacements(s, litgen.opencv_replacements())
    assert r == "cv::Sizeounette Size s = (0, 0)"

    s = "a = 1.5f;"
    r = code_replacements.apply_code_replacements(s, litgen.standard_code_replacements())
    assert r == "a = 1.5;"

    s = "a = -1.5d;"
    r = code_replacements.apply_code_replacements(s, litgen.standard_code_replacements())
    assert r == "a = -1.5;"
