import json
from typing import TypeVar, List, Callable, Any, Literal
from colorama import Fore, Style, init, Back
import uuid
import os
from pydantic import BaseModel

T = TypeVar("T")

NEW_GAME = 0

STATS = ["Strength", "Dexterity", "Wisdom", "Intelligence", "Constitution"]


class Character(BaseModel):
    name: str = ""
    Strength: int = 0
    Dexterity: int = 0
    Wisdom: int = 0
    Intelligence: int = 0
    Constitution: int = 0


class Campaign(BaseModel):
    characters: List[Character] = []
    name: str = ""
    room_id: str = ""
    character_count: int = 0


class State(BaseModel):
    campaigns: List[Campaign] = []
    rooms: dict[
        str, "Room"
    ] = {}  # "Room" the quotes are saying to wait until file is loaded


class Room(BaseModel):
    name: str = ""
    desc: str = ""
    actions: dict[str, "Action"] = {}


class GoToRoomAction(BaseModel):
    action: Literal["gotoroom"] = "gotoroom"
    room_id: str


Action = GoToRoomAction


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
        except KeyboardInterrupt:
            exit(0)
        except:
            pass
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


GO_TO_ROOM = "gotoroom"


CLONING_TUBE_ID = "vnum0"

ROOMS = {
    CLONING_TUBE_ID: Room(
        name="Cloning tube",
        desc="You are in a cloning tube\n",
        actions={},
    ),
}


class Game:
    def __init__(self):
        self.load_state()

    def get_room_name(self, action: dict) -> str:

        rooms = self.rooms

        if isinstance(action, GoToRoomAction):
            room_id = action.room_id
            return rooms[room_id].name
        return ""

    # make rooms save to json upon making room
    def start(self):
        self.rooms = self.state.rooms or ROOMS
        self.campaign = self.choose_campaign()  # -> magic -> function
        self.campaign.room_id = self.campaign.room_id or CLONING_TUBE_ID
        set_state_with_number(
            self.campaign,
            "character_count",
            "How many characters are in your campaign? (1-4)",
            validate_campaign_player_count,
            skip_if_has_value=True,
        )
        self.save_state()
        characters = self.campaign.characters or []
        self.campaign.characters = characters
        for i in range(self.campaign.character_count):
            character = get_index(characters, i, Character())
            if i >= len(characters):
                characters.append(character)
            self.pick_stats(character)

        while True:
            room_id = self.campaign.room_id
            room = self.rooms[room_id]
            actions = self.get_actions()
            print(
                f"({room.name}) \n--------------------------------------------------{Fore.RESET} "
            )
            print(f"{room.desc} \n-------------------------------------------------- ")

            action = get_choice(
                "Obvious exits:             ",
                [*actions],
                allows_free_form=True,
                returns_index=True,
            )
            os.system("cls")
            match action:
                case i if isinstance(i, int):
                    direction = list(room.actions.keys())[
                        action
                    ]  # direction stores string north west east ext
                    match room.actions[direction]:
                        case a if isinstance(a, GoToRoomAction):
                            room_id = a.room_id

                            self.campaign.room_id = room_id
                        case _:
                            pass
                case s if s.startswith("makeroom "):
                    command, direction, *room_name = s.split()
                    room_name = " ".join(room_name)
                    room_id = generate_id()
                    room.actions[direction] = GoToRoomAction(room_id=room_id)
                    self.rooms[room_id] = Room(name=room_name, desc="", actions={})
                    self.state.rooms = self.rooms
                case s if s.startswith("makeroomc "):
                    command, todirection, fromdirection, *room_name = s.split()
                    room_name = " ".join(room_name)
                    room_id = generate_id()
                    room.actions[todirection] = GoToRoomAction(room_id=room_id)

                    self.rooms[room_id] = Room(
                        name=room_name,
                        desc="",
                        actions={
                            fromdirection: GoToRoomAction(room_id=self.campaign.room_id)
                        },
                    )
                    self.state.rooms = self.rooms
                case s if s.startswith("setroomname "):
                    command, *room_name = s.split()
                    room_name = " ".join(room_name)
                    room.name = room_name
                case id if id.startswith("vin "):
                    print(room_id)
                case s if s.startswith("makeexit "):
                    command, direction, room_id = s.split()
                    room.actions[direction] = GoToRoomAction(room_id=room_id)
                case d if d.startswith("roomdesc "):
                    print("Enter new room description")
                    room.desc = input()  # changed .desc from ["desc"]
                case d if d.startswith("deleteroom "):
                    command, toremove = s.split()
                    del self.rooms[toremove]
                    for room in self.rooms.values():
                        for action_key, action_value in dict(room.actions).items():
                            if action_value.room_id == toremove:
                                del room.actions[action_key]
                case s if s.startswith("score"):
                    for character in characters:
                        print(f"-= Score for {character.name} =-")
                        output = []
                        for stat in STATS:
                            output.append(f"{stat[0:3]}: {getattr(character, stat)}")

                        print(", ".join(output))
                        print()
                case q if q.startswith("quit"):
                    break

            self.save_state()

    def get_actions(self):
        actions = []
        roomid = self.campaign.room_id
        room = self.rooms[roomid]
        for key, value in room.actions.items():
            room_name = self.get_room_name(value)
            actions.append(f"{key} - {room_name}")
        return actions

    def choose_campaign(self):
        campaigns = self.state.campaigns or []
        options = ["New Game"]
        for campaign in campaigns:
            options.append(campaign.name)
        option = get_choice("Choose your campaign: ", options, True)
        if option == NEW_GAME:
            campaign = Campaign(name="Campaign " + str(option + len(options)))
            campaigns.append(campaign)
            self.state.campaigns = campaigns
            self.save_state()
            return campaign
        return campaigns[option - 1]

    def pick_stats(self, character: Character):
        # When using self here does it mean the names in characters is the instance
        set_state_with_line(character, "name", "What is your characters name?", True)
        self.save_state()
        character_name = character.name
        stat_pool = 75
        for stat in STATS:
            already_allocated_stat = getattr(character, stat) or 0
            stat_pool = stat_pool - already_allocated_stat

        def validate_stat(stat: int):
            return 0 <= stat and stat <= stat_pool

        if stat_pool > 0:
            print(f"Pick stats for {character_name}")
            while stat_pool > 0:
                for stat in STATS:
                    value = get_number(
                        f"Pick your {stat} ({stat_pool} remaining points)",
                        validate_stat,
                    )
                    already_allocated_stat = getattr(character, stat) or 0
                    stat_pool = stat_pool - value
                    setattr(character, stat, value + already_allocated_stat)
                    self.save_state()

    def save_state(self):
        with open("state.json", "w") as f:
            contents = self.state.model_dump_json(indent=2)
            f.write(contents)

    def load_state(self):
        try:
            with open("state.json", "r") as f:
                contents = f.read()
                self.state = State.model_validate_json(contents)
        except:
            self.state = State()
