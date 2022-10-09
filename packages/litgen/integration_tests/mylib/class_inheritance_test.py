import lg_mylib


def test_inherit():
    dog = lg_mylib.Animals.Dog("Lonely dog")
    assert dog.name == "Lonely dog_dog"
    assert dog.bark() == "BIG WOOF!"

    pet_dog = lg_mylib.Home.PetDog("Sammy")
    assert pet_dog.name == "Sammy_dog"
    assert pet_dog.bark() == "woof"
    assert pet_dog.is_pet()


def test_downcasting():
    dog = lg_mylib.make_dog()
    assert dog.bark() == "BIG WOOF!"
