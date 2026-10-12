#include "api_marker.h"

//
// "Text end" params: with options.fn_params_text_end_names__regex = r"_end$", a `const char *` param that follows
// another `const char *` param, and whose name ends with "_end", points inside the text: it leaves the python signature.
//
// The following functions will be exported with the following python signatures:
// -->    def text_end_length(text: str) -> int:            # text_end receives the end of the text
// -->    def text_end_length_optional(text: str) -> int:   # text_end receives its default value
//
MY_API inline int text_end_length(const char* text, const char* text_end)
{
    return (int)(text_end - text);
}

MY_API inline int text_end_length_optional(const char* text, const char* text_end = nullptr)
{
    if (text_end == nullptr)
        return -1;
    return (int)(text_end - text);
}
