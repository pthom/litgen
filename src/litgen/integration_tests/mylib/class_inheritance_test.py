from __future__ import annotations
import lg_mylib


def test_inherit():
    dog = lg_mylib.animals.Dog("Lonely dog")
    assert dog.name == "Lonely dog_dog"
    assert dog.bark() == "BIG WOOF!"

    if lg_mylib.binding_multiple_inheritance():
        pet_dog = lg_mylib.home.PetDog("Sammy")
        assert pet_dog.name == "Sammy_dog"
        assert pet_dog.bark() == "woof"
        assert pet_dog.is_pet()


def test_downcasting():
    dog = lg_mylib.make_dog()
    assert dog.bark() == "BIG WOOF!"
