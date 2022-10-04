#include "mylib/api_marker.h"

#include <string>

namespace Root  // MY_API
{
    namespace Inner // MY_API
    {
        class MyVirtualClass // MY_API
        {
        public:
            virtual ~MyVirtualClass() = default;
        protected:
            MY_API virtual int foo_virtual(int x) const { return 42 + x; }
            // MY_API virtual int foo_virtual_pure() const = 0;
            MY_API virtual std::string foo_virtual_const_const(const std::string& name) const {
                return std::string("Hello ") + name;
            }
        };
    }
}
