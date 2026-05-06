from src.utility import (
    get_index,
    get_number,
    set_state_with_line,
    set_state_with_number,
    is_valid,
    generate_id,
    validate_campaign_player_count,
)
from src.models import (
    State,
    CLONING_TUBE_ID,
    Room,
    GoToRoomAction,
    Campaign,
    ItemBase,
    Character,
    Layers,
    HeldItem,
)
from unittest import mock
import pytest

TEST_DIRECTION = "north"
OTHER_ROOM_ID = "other room"


@pytest.fixture
def dummy_state():
    state = State()

    state.rooms[CLONING_TUBE_ID] = Room(
        name="Cloning tube",
        desc="You are in a cloning tube\n",
        actions={TEST_DIRECTION: GoToRoomAction(room_id=OTHER_ROOM_ID)},
    )
    state.rooms[OTHER_ROOM_ID] = Room(
        name="other room",
        desc="a description",
        actions={TEST_DIRECTION: GoToRoomAction(room_id=CLONING_TUBE_ID)},
    )

    state.campaigns.append(
        Campaign(
            room_id=CLONING_TUBE_ID,
            characters=[
                Character(
                    Strength=1,
                    Dexterity=2,
                    Wisdom=3,
                    Intelligence=4,
                    Constitution=5,
                    hitroll=6,
                    damroll=7,
                    armor=8,
                    name="testname",
                    torso=[],
                )
            ],
        )
    )
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


def test__itembase_fill__name():
    user_input = "namecheck"
    price = 5
    item = ItemBase()
    with mock.patch("builtins.input", side_effect=[user_input, price]):
        item.fill()
        assert item.name == user_input
        assert item.value == price


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
    assert (
        other_action.room_id == dummy_state.campaign.room_id
    )  # this checks to make sure new room connects to current room


def test__state__set_room_name(dummy_state):
    room_name = "hallway"
    dummy_state.set_room_name(room_name)
    assert dummy_state.room.name == room_name


def test__state__delete_room(dummy_state):
    assert OTHER_ROOM_ID in dummy_state.rooms
    assert len(dummy_state.rooms[CLONING_TUBE_ID].actions) == 1
    dummy_state.delete_room(OTHER_ROOM_ID)
    assert OTHER_ROOM_ID not in dummy_state.rooms
    assert len(dummy_state.rooms[CLONING_TUBE_ID].actions) == 0


def test__state__get_score(dummy_state):
    score = dummy_state.get_score()
    assert score == "\n".join(
        [
            "-= Score for testname =-",
            "Str: 1",
            "Dex: 2",
            "Wis: 3",
            "Int: 4",
            "Con: 5",
            "",
            "hitroll: 6     damroll: 7     armor: 8",
        ]
    )


def test__state__makeroom(dummy_state):
    direction = "down"
    name = "start room"
    room_id, _ = dummy_state.make_room(direction, name)
    assert room_id in dummy_state.rooms
    assert room_id == dummy_state.room.actions[direction].room_id


def test__state__show_equipment(dummy_state):
    equipment = dummy_state.show_equipment()
    print(equipment)
    assert equipment == ""
