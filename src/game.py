from colorama import Fore, Style, init, Back
from src.models import ROOMS
import os
import textwrap
from src.models import State, Character, Room, GoToRoomAction, Campaign
from src.constants import NEW_GAME, STATS
from src.utility import (
    generate_id,
    get_choice,
    get_index,
    get_number,
    set_state_with_line,
    set_state_with_number,
    validate_campaign_player_count,
)


class Game:
    state: State

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
        self.state.choose_campaign()  # -> magic -> function
        self.save_state()
        set_state_with_number(
            self.state.campaign,
            "character_count",
            "How many characters are in your campaign? (1-4)",
            validate_campaign_player_count,
            skip_if_has_value=True,
        )
        self.save_state()
        characters = self.state.campaign.characters or []
        self.state.campaign.characters = characters
        for i in range(self.state.campaign.character_count):
            character = get_index(characters, i, Character())
            if i >= len(characters):
                characters.append(character)
            self.pick_stats(character)

        while True:
            room_id = self.state.campaign.room_id
            room = self.rooms[room_id]
            actions = self.get_actions()
            print(
                f"({room.name}) \n--------------------------------------------------------------------------------{Fore.RESET} "
            )
            print(
                f"{room.desc} \n--------------------------------------------------------------------------------"
            )

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

                            self.state.campaign.room_id = room_id
                        case _:
                            pass
                case s if s.startswith("makeroom "):
                    command, direction, *room_name = s.split()
                    room_name = " ".join(room_name)
                    self.state.make_room(direction=direction, room_name=room_name)

                case s if s.startswith("makeroomc "):
                    command, todirection, fromdirection, *room_name = s.split()
                    room_name = " ".join(room_name)
                    room_id = generate_id()
                    room.actions[todirection] = GoToRoomAction(room_id=room_id)

                    self.rooms[room_id] = Room(
                        name=room_name,
                        desc="",
                        actions={
                            fromdirection: GoToRoomAction(
                                room_id=self.state.campaign.room_id
                            )
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
                    print("Type CLOSE on new line to finalize description")
                    buffer = []
                    while True:
                        line = input()
                        if line.strip().upper() == "CLOSE":
                            break
                        buffer.append(line)
                        buffer_needs_format = "\n".join(line.strip() for line in buffer)
                        room.desc = textwrap.fill(
                            buffer_needs_format,
                            replace_whitespace=False,
                            width=80,
                            break_long_words=False,
                            break_on_hyphens=False,
                        )
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
        roomid = self.state.campaign.room_id
        room = self.rooms[roomid]
        for key, value in room.actions.items():
            room_name = self.get_room_name(value)
            actions.append(f"{key} - {room_name}")
        return actions

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
