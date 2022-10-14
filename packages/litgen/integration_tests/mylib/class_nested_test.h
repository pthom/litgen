#include "api_marker.h"

#include <string>

class TextEditor
{
public:
    MY_API std::string GetText() const { return "abc"; }

private:
    std::string GetText(int a) const { return std::to_string(a); }
};
