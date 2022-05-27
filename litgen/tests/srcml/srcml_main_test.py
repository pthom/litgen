from litgen.internal.srcml import srcml_main


def test_srcml_main():
    code = """
#define MY_HEADER_H
#ifndef MY_HEADER_H

// Comment Line 1
// Comment Line 2
void Foo();

static int NCalls = 0; // Total number of calls

#endif     
"""