from src.utility import (
    get_index,
    get_number,
    set_state_with_line,
    set_state_with_number,
    is_valid,
    generate_id,
    validate_campaign_player_count,
)
from src.models import State, CLONING_TUBE_ID, Room, GoToRoomAction, Campaign
from unittest import mock
import pytest

TEST_DIRECTION = "north"


@pytest.fixture
def dummy_state():
    state = State()

    state.rooms[CLONING_TUBE_ID] = Room(
        name="Cloning tube",
        desc="You are in a cloning tube\n",
        actions={TEST_DIRECTION: GoToRoomAction(room_id="string")},
    )
    state.campaigns.append(Campaign(room_id=CLONING_TUBE_ID))
    return state


def test_generate_id():
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2


@pytest.mark.parametrize(
    "number_of_players, is_valid",
    [(-1, False), (0, False), (1, True), (2, True), (3, True), (4, True), (5, False)],
)
def test_validate_campaign_player_count(number_of_players, is_valid):
    output = validate_campaign_player_count(number_of_players)
    assert output == is_valid


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


@mock.patch("builtins.input", side_effect=KeyboardInterrupt())
@mock.patch("builtins.exit")
def test__get_number__exits_program(mock_exit, mock_input):
    get_number("exit prompt")
    mock_exit.assert_called_once_with(0)


class Dummy:
    def __init__(self):
        self.zaboomafom = 4


def test__set_state_with_line__has_value_skip():
    d = Dummy()
    set_state_with_line(d, "zaboomafom", "testwords", skip_if_has_value=True)
    assert d.zaboomafom == 4


def test__set_state_with_line__stores_line():
    user_input = "stringtopass"
    path = "zaboomafom"
    d = Dummy()
    with mock.patch("builtins.input", side_effect=[user_input]):
        prompt = "testingwords"
        skip_if_has_value = False
        set_state_with_line(d, path, prompt, skip_if_has_value)
        assert d.zaboomafom == user_input


def test__set_state_with_number__it_skips():
    d = Dummy()
    path = "zaboomafom"
    prompt = "testingwords"
    skip_if_has_value = True
    with mock.patch("src.utility.get_number") as mock_get_number:
        set_state_with_number(d, path, prompt, is_valid, skip_if_has_value)
        mock_get_number.assert_not_called()
    assert d.zaboomafom == 4


def test__set_state_with_number__stores_number():
    user_input = "3"
    path = "zaboomafom"
    d = Dummy()
    path = "zaboomafom"

    with mock.patch("builtins.input", side_effect=[user_input]):
        prompt = "testingwords"
        skip_if_has_value = False
        set_state_with_number(d, path, prompt, is_valid, skip_if_has_value)
        assert d.zaboomafom == int(user_input)


def test__go_direction__has_room__it_can_go(dummy_state):

    assert dummy_state.go_direction(TEST_DIRECTION)


def test__go_direction__does_not_have_room__it_cant_go(dummy_state):
    assert not dummy_state.go_direction("south")


def test__make_roomc__add_a_room__it_works(dummy_state):
    room_name = "testroom"
    to_direction = "up"
    from_direction = "down"
    dummy_state.make_roomc(room_name, to_direction, from_direction)
    action = dummy_state.room.actions[to_direction]
    assert isinstance(action, GoToRoomAction)
    other_room = dummy_state.rooms[action.room_id]
    other_action = other_room.actions[from_direction]
    assert isinstance(other_action, GoToRoomAction)
    assert other_action.room_id == dummy_state.campaign.room_id
