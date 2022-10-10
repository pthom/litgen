#pragma once

// Here, we test that functions placed under unknown preprocessor conditions are not exported by default
// You could choose to add them anyway with:
//    options.srcmlcpp_options.header_filter_acceptable_suffixes += "|OBSCURE_OPTION"

#ifdef OBSCURE_OPTION
MY_API int ObscureFunction() { return 42; }
#endif
