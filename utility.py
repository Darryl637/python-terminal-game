import uuid
from typing import TypeVar, List, Callable, Any

T = TypeVar("T")


def generate_id():
    return str(uuid.uuid4())


# Using to check if index value is there, if not default value provided
def get_index(list: List[T], index: int, default: T) -> T:
    if index < 0:
        raise IndexError
    if index < len(list):
        return list[index]
    return default


def is_valid(*args):
    return True


def get_number(prompt: str, validator: Callable[[int], bool] = is_valid) -> int:
    while True:
        print(prompt)
        try:
            number = int(input())
            if validator(number):
                return number
        finally:
            print("Try again")


def set_state_with_line(instance: Any, path: str, prompt: str, skip_if_has_value=False):
    value = getattr(instance, path)
    if skip_if_has_value and value:
        return
    setattr(instance, path, get_line(prompt))


def set_state_with_number(
    instance: Any,
    path: str,
    prompt: str,
    validator: Callable[[int], bool],
    skip_if_has_value=False,
):
    value = getattr(instance, path)
    if skip_if_has_value and value:
        return
    setattr(instance, path, get_number(prompt, validator))


# possible not needed now
def set_state_with_choice(
    map: dict[str, Any],
    path: str,
    prompt: str,
    options: List[str],
    skip_if_has_value=False,
):
    if skip_if_has_value and path in map:
        return
    map[path] = get_choice(prompt, options)


def get_line(prompt: str):
    return input(prompt + "\n")


def get_choice(
    prompt: str, options: List[str], returns_index=False, allows_free_form=False
) -> str | int:
    while True:
        try:
            print(prompt)
            for index, option in enumerate(options):
                print(f"{index + 1}. {option}")
            value = input()
            number = int(value) - 1
            if 0 <= number and number < len(options):
                if returns_index:
                    return number
                return options[number]
        except KeyboardInterrupt:
            exit(0)
        except:
            if allows_free_form:
                return value
        print("Try again")


def validate_campaign_player_count(number: int) -> bool:
    return number > 0 and number < 5
