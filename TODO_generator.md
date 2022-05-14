- OK ! Test overidde function
- OK! Test keyword inline
- Test array: Semi Ok. 
  - Type size inconsistency
  - Template functions?
  - Check authorized buffer_types in options (uint8_t ok, not char, etc) 
  - test avec const 
- Test leaked_ptr
- Test use class
- private / public
- ToString ?
- Online Interface with google colab


- test dans implot
- test dans immvision
- methods

- Later: folder in site-packages
- definir politique vis a vis DocString and multiline comments
- code_replacement sur comments deconne:
    // Doubles the input number
    // i.e return "2 * x"    <== le * est supprimé


Pour les buffer non template, il faudra aussi vérifier le type dans l'array

Solution / Templates:
            char array_type = array.dtype().char_();
            if (array_type == 'B')
                return mul_inside_array<uint8_t>((uint8_t *)array_buffer, array_count, factor);
            else if (array_type == 'b')
                return mul_inside_array<int8_t>((int8_t *)array_buffer, array_count, factor);
            else if (array_type == 'H')
                return mul_inside_array<uint16_t>((uint16_t *)array_buffer, array_count, factor);
            else if (array_type == 'h')
                return mul_inside_array<int16_t>((int16_t *)array_buffer, array_count, factor);
            else if (array_type == 'I')
                return mul_inside_array<uint32_t>((uint32_t *)array_buffer, array_count, factor);
            else if (array_type == 'i')
                return mul_inside_array<int32_t>((int32_t *)array_buffer, array_count, factor);
    else if (array_type == 'L')
        return mul_inside_array<__UINT64_TYPE__>((__UINT64_TYPE__ *)array_buffer, array_count, factor);
    else if (array_type == 'l')
        return mul_inside_array<__INT64_TYPE__>((__INT64_TYPE__ *)array_buffer, array_count, factor);
            else if (array_type == 'f')
                return mul_inside_array<float>((float *)array_buffer, array_count, factor);
            else if (array_type == 'd')
                return mul_inside_array<double>((double *)array_buffer, array_count, factor);
            else if (array_type == 'g')
                return mul_inside_array<long double>((long double *)array_buffer, array_count, factor);
            else
                throw std::runtime_error(std::string("mul_inside_array unexpected array type: ") + array_type);

