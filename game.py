import json
from typing import TypeVar, List, Callable, Any
from colorama import Fore, Style, init

T = TypeVar("T")

NEW_GAME = 0

STATS = ["Strength", "Dexterity", "Wisdom", "Intelligence", "Consitution"]


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


def set_state_with_line(
    map: dict[str, Any], path: str, prompt: str, skip_if_has_value=False
):
    if skip_if_has_value and path in map:
        return
    map[path] = get_line(prompt)


def set_state_with_number(
    map: dict[str, Any],
    path: str,
    prompt: str,
    validator: Callable[[int], bool],
    skip_if_has_value=False,
):
    if skip_if_has_value and path in map:
        return
    map[path] = get_number(prompt, validator)


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


GO_TO_ROOM = "gotoroom "


def get_room_name(action_name: str) -> str:
    if action_name.startswith(GO_TO_ROOM):
        return action_name[len(GO_TO_ROOM) :]
    return ""


def make_room(desc, actions):
    return {"actions": actions, "desc": desc}


def go_to_room(room_name):
    return f"{GO_TO_ROOM}{room_name}"


STARTING_ROOM = "Starting room"
KITCHEN = "Kitchen"
LIVING_ROOM = "Living room"

rooms = {
    STARTING_ROOM: make_room(
        Fore.GREEN + "You are in the starting room\n------------------------------",
        {"Go to the Kitchen": go_to_room(KITCHEN)},
    ),
    KITCHEN: make_room(
        "You are in the Kitchen",
        {
            "Go to Starting room": go_to_room(STARTING_ROOM),
            "Go to Living room": go_to_room(LIVING_ROOM),
        },
    ),
    LIVING_ROOM: make_room(
        "You are in the Living room", {"Go to the Kitchen": go_to_room(KITCHEN)}
    ),
}


class Game:
    def __init__(self):
        self.load_state()

    # make rooms save to json upon making room
    def start(self):
        self.rooms = self.state.get("rooms", rooms)
        self.campaign = self.choose_campaign()  # -> magic -> function
        self.campaign["room"] = self.campaign.get("room", STARTING_ROOM)
        print(self.campaign["name"])
        set_state_with_number(
            self.campaign,
            "character_count",
            "How many characters are in your campaign? (1-4)",
            validate_campaign_player_count,
            skip_if_has_value=True,
        )
        self.save_state()
        characters = self.campaign.get("characters", [])
        self.campaign["characters"] = characters
        for i in range(self.campaign["character_count"]):
            character = get_index(characters, i, {})
            if i >= len(characters):
                characters.append(character)
            self.pick_stats(character)

        while True:
            room = rooms[self.campaign["room"]]
            actions = self.get_actions()
            print(room["desc"])
            action = get_choice(
                "What would you like to do?",
                [*actions, "quit game"],
                allows_free_form=True,
                returns_index=True,
            )
            match action:
                case i if isinstance(i, int):
                    direction = list(room["actions"].keys())[action]
                    match room["actions"][direction]:
                        case s if s.startswith(GO_TO_ROOM):
                            command, *room_name = s.split()
                            room_name = " ".join(room_name)
                            self.campaign["room"] = room_name
                        case _:
                            pass
                case s if s.startswith("makeroom "):
                    command, direction, *room_name = s.split()
                    room_name = " ".join(room_name)
                    room["actions"][direction] = go_to_room(room_name)
                    self.rooms[room_name] = make_room(room_name, {})
                case "quit game":  # get quit funtioning
                    break

            self.save_state()

    def get_actions(self):
        actions = []
        room_name = self.campaign["room"]
        room = self.rooms[room_name]
        for key, value in room["actions"].items():
            room_name = get_room_name(value)
            actions.append(f"{key} - {room_name}")
        return actions

    def choose_campaign(self):
        campaigns = self.state.get("campaigns", [])
        options = ["New Game"]
        for campaign in campaigns:
            options.append(campaign["name"])
        option = get_choice("Choose your campaign: ", options, True)
        if option == NEW_GAME:
            campaign = {
                "name": "Campaign " + str(option + len(options)),
            }
            campaigns.append(campaign)
            self.state["campaigns"] = campaigns
            self.save_state()
            return campaign
        return campaigns[option - 1]

    def pick_stats(self, character: dict[str, Any]):
        # When using self here does it mean the names in characters is the instance
        set_state_with_line(character, "name", "What is your characters name?", True)
        self.save_state()
        character_name = character["name"]
        stat_pool = 75
        for stat in STATS:
            already_allocated_stat = character.get(stat, 0)
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
                    already_allocated_stat = character.get(stat, 0)
                    stat_pool = stat_pool - value
                    character[stat] = value + already_allocated_stat
                    self.save_state()

    def save_state(self):
        with open("state.json", "w") as f:
            contents = json.dumps(self.state, indent=2)
            f.write(contents)

    def load_state(self):
        try:
            with open("state.json", "r") as f:
                contents = f.read()
                self.state = json.loads(contents)
        except:
            self.state = {}
