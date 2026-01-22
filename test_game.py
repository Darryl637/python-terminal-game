from game import (
    get_index,
    get_number,
    set_state_with_line,
    set_state_with_number,
    is_valid,
)
from unittest import mock
import pytest


def test__get_index__index_in_range():
    list = [10, 20, 30]
    index = 1
    default = 5
    output = get_index(list, index, default)
    assert output == 20, "Valid Index"


def test__get_index__negative_index():
    list = [10, 20, 30]
    index = -1
    default = 5
    with pytest.raises(IndexError):
        get_index(list, index, default)


def test__get_index__index_out_of_range():
    list = [10, 20, 30]
    index = 8
    default = 5
    output = get_index(list, index, default)
    assert output == 5, "Invalid Index"


def test__get_number__gets_a_number_first_try():
    with mock.patch("builtins.input", return_value="7"):
        prompt = "Is working"
        output = get_number(prompt)
        assert output == 7


def test__get_number__validates_number():
    with mock.patch("builtins.input", side_effect=["7", "NAN", "5"]):
        prompt = "Is working"

        def validator(number):
            return number <= 5

        output = get_number(prompt, validator)
        assert output == 5


def test__set_state_with_line__it_skips():
    path = "zaboomafom"
    map = {
        path: 4,
    }
    prompt = "testingwords"
    skip_if_has_value = True
    set_state_with_line(map, path, prompt, skip_if_has_value)


def test__set_state_with_line__stores_line():
    user_input = "stringtopass"
    path = "zaboomafom"
    map = {
        path: 4,
    }
    with mock.patch("builtins.input", side_effect=[user_input]):
        prompt = "testingwords"
        skip_if_has_value = False
        set_state_with_line(map, path, prompt, skip_if_has_value)
        assert map[path] == user_input


def test__set_state_with_number__it_skips():
    path = "zaboomafom"
    map = {
        path: 4,
    }
    prompt = "testingwords"
    skip_if_has_value = True
    set_state_with_number(map, path, prompt, is_valid, skip_if_has_value)


def test__set_state_with_number__stores_number():
    user_input = "3"
    path = "zaboomafom"
    map = {
        path: 4,
    }
    with mock.patch("builtins.input", side_effect=[user_input]):
        prompt = "testingwords"
        skip_if_has_value = False
        set_state_with_number(map, path, prompt, is_valid, skip_if_has_value)
        assert map[path] == int(user_input)
