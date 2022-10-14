#include "api_marker.h"

#include <string>
#include <memory>


namespace Animals
{
    struct Animal
    {
        MY_API Animal(const std::string &name) : name(name) { }
        std::string name;

        virtual ~Animal() = default;
    };

    struct Dog : Animal
    {
        MY_API Dog(const std::string &name) : Animal(name + "_dog") { }
        MY_API virtual std::string bark() const { return "BIG WOOF!"; }

        virtual ~Dog() = default;
    };

}

namespace Home
{
    struct Pet
    {
        MY_API bool is_pet() const { return true; }
    };

    struct PetDog: public Animals::Dog, public Pet
    {
        MY_API PetDog(const std::string &name): Animals::Dog(name), Pet() {}
        MY_API virtual std::string bark() const { return "woof"; }

        virtual ~PetDog() = default;
    };

}

// Test that downcasting works: the return type is Animal, but it should bark!
MY_API std::unique_ptr<Animals::Animal> make_dog()
{
    return std::make_unique<Animals::Dog>("Rolf");
}
