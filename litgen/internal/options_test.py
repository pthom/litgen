import litgen


def test_multiple_options_instances():
    options1 = litgen.options.code_style_implot()
    options2 = litgen.CodeStyleOptions()
    assert id(options1) != id(options2)
    assert id(options1.srcml_options) != id(options2.srcml_options)
    assert len(options2.srcml_options.functions_api_prefixes) == 0
