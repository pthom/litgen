#pragma once

// Here, we test that functions placed under unknown preprocessor defines are not exported by default
// You could choose to add them anyway with:
// ````
//    options.srcml_options.header_guard_suffixes.append("OBSCURE_OPTION")
// ````

#ifdef OBSCURE_OPTION
MY_API int ObscureFunction() { return 42; }
#endif
