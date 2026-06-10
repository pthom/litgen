#pragma once

// Here, we test that functions placed under unknown preprocessor conditions are not exported by default
// You could choose to add them anyway with:
//    options.srcmlcpp_options.header_filter_acceptable_suffixes += "|OBSCURE_OPTION"

#ifdef OBSCURE_OPTION
MY_API int ObscureFunction() { return 42; }
#endif

// The same filtering also applies to `#if` conditions (not only `#ifdef`/`#ifndef`):
// the macro name referenced in the condition is matched against
// options.srcmlcpp_options.header_filter_acceptable__regex, exactly like `#ifdef`.

// OBSCURE_OPTION is not acceptable => this function is not exported
#if OBSCURE_OPTION
MY_API int ObscureFunctionInIf() { return 43; }
#endif

// HEADER_FILTER_ACCEPTABLE_IF is added to header_filter_acceptable__regex
// (see autogenerate_mylib.py) => these functions are exported
#define HEADER_FILTER_ACCEPTABLE_IF 1

#if HEADER_FILTER_ACCEPTABLE_IF
MY_API int FilterAcceptableIfFunction() { return 44; }
#endif

#if defined(HEADER_FILTER_ACCEPTABLE_IF)
MY_API int FilterAcceptableDefinedFunction() { return 45; }
#endif

// The `#else` branch of an accepted region is inactive: only the primary branch is
// exported (the `#else` body is dropped). Since HEADER_FILTER_ACCEPTABLE_IF is defined,
// the primary branch is what the C++ compiler keeps too.
#if HEADER_FILTER_ACCEPTABLE_IF
MY_API int ElseBranchPrimary() { return 46; }
#else
MY_API int ElseBranchSecondary() { return 47; }
#endif
