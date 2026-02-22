from dataclasses import dataclass


@dataclass
class Person:
    first_name: str = ""
    last_name: str = ""


person_class = Person()
person_class.first_name
print(person_class)


def make_person(first_name="", last_name=""):
    return {"first_name": first_name, "last_name": last_name}


person_map = make_person()
person_map["first_name"]
print(person_map)
