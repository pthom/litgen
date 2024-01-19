from __future__ import annotations
import enum


class WarningType(enum.Enum):
    Undefined = enum.auto()

    Unclassified = enum.auto()

    # A cpp element was stored as CppUnprocessed
    SrcmlcppIgnoreElement = enum.auto()

    # parse_parameter_list unhandled tag
    SrcmlcppUnhandledTagParameterList = enum.auto()

    # An element was ignored when parsing the block of a namespace, struct or unit
    LitgenIgnoreElement = enum.auto()

    # An exception was raised when creating an adapted element for python
    LitgenBlockElementException = enum.auto()

    # a C Style array was not added as a class or struct member was ignored
    # since it does not contain numbers and cannot be represented as a numpy array
    LitgenClassMemberNonNumericCStyleArray = enum.auto()

    # AdaptedClassMember: Detected a numeric C Style array, but will not export it.
    # Hint: modify `options.member_numeric_c_array_replace__regex`
    LitgenClassMemberNumericCStyleArray_Setting = enum.auto()

    # AdaptedClassMember: Detected a numeric C Style array, but its size is not parsable.
    # Hint: may be, add the value "{array_size_str}" to `options.c_array_numeric_member_size_dict`
    LitgenClassMemberNumericCStyleArray_UnparsableSize = enum.auto()

    # Public elements of type {child.tag()} are not supported in python conversion
    LitgenClassMemberUnsupported = enum.auto()

    # AdaptedClassMember: Skipped bitfield member
    LitgenClassMemberSkipBitfield = enum.auto()

    # AdaptedClassMember: Can't parse the size of this array.
    # Hint: use a vector, or extend `options.c_array_numeric_member_types`
    LitgenClassMemberUnparsableSize = enum.auto()

    # An exception was raised when creating an adapted class member for python
    LitgenClassMemberException = enum.auto()

    # Ignoring template class. You might need to set LitgenOptions.class_template_options
    LitgenTemplateClassIgnore = enum.auto()

    # Template classes with more than one parameter are not supported
    LitgenTemplateClassMultipleIgnore = enum.auto()

    # Ignoring template function. You might need to set LitgenOptions.fn_template_options
    LitgenTemplateFunctionIgnore = enum.auto()

    # Only one parameters template functions are supported
    LitgenTemplateFunctionMultipleIgnore = enum.auto()

    # Cannot parse the value of this enum element.
    # Hint: maybe add an entry to SrcmlcppOptions.named_number_macros
    LitgenEnumUnparsableValue = enum.auto()
