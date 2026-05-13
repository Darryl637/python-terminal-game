from colorama import Fore, Style, init, Back
from typing import List
from src.models import ROOMS, Action
import os
import textwrap
from src.models import (
    State,
    Character,
    Room,
    GoToRoomAction,
    Campaign,
    wear_locations,
    layer_locations,
    ItemBase,
    Armor,
    Weapon,
    HeldItem,
)
from src.constants import NEW_GAME, ROLLED_STATS
from src.utility import (
    generate_id,
    get_choice,
    get_index,
    get_number,
    set_state_with_line,
    set_state_with_number,
    validate_campaign_player_count,
    get_line,
)


class Game:
    state: State

    def __init__(self):
        self.load_state()

    def get_room_name(self, action: Action) -> str:

        rooms = self.state.rooms

        if isinstance(action, GoToRoomAction):
            room_id = action.room_id
            return rooms[room_id].name
        return ""

    # make rooms save to json upon making room
    def start(self):
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
        needsprompt = True
        while True:
            room_id = self.state.campaign.room_id
            room = self.state.rooms[room_id]
            actions = self.get_actions()
            if needsprompt:
                #            os.system("cls")
                print(
                    f"({room.name}) \n--------------------------------------------------------------------------------{Fore.RESET} "
                )
                print(
                    f"{room.desc} \n--------------------------------------------------------------------------------"
                )

                print("Obvious exits: \n" + "\n".join(actions))
                print(
                    "--------------------------------------------------------------------------------"
                )

                for item in room.items:
                    print(item)
            needsprompt = True

            action = get_line(">")

            match action:
                case "look":
                    needsprompt = True

                case s if s.startswith("makeroom "):
                    command, todirection, fromdirection, *room_name = s.split()
                    room_name = " ".join(room_name)
                    self.state.make_roomc(room_name, todirection, fromdirection)

                case s if s.startswith("make "):
                    command, type = s.lower().split()
                    match type:
                        case "armor":
                            item = Armor()

                        case "weapon":
                            item = Weapon()

                    item.fill()
                    item_id = generate_id()
                    self.state.items[item_id] = item

                case "eq" | "equipment":
                    print(self.state.show_equipment())

                    needsprompt = False
                case "i" | "inv" | "inventory":
                    print("Inventory:")
                    items = self.state.campaign.inventory
                    for item in items:
                        print(item)
                    needsprompt = False
                case g if g.startswith("get "):
                    command, *item_input = g.split()
                    item_input = " ".join(item_input).lower()
                    found = False
                    for index, item in enumerate(room.items):
                        if item_input == item:
                            self.state.campaign.inventory.append(item)
                            room.items.pop(index)
                            found = True
                            break
                    if not found:
                        print("That item isn't here")

                case d if d.startswith("drop "):
                    command, *item_input = d.split()
                    item_input = " ".join(item_input).lower()
                    found = False
                    for index, item in enumerate(self.state.campaign.inventory):
                        if item_input == item:
                            room.items.append(item)
                            self.state.campaign.inventory.pop(index)
                            found = True
                            needsprompt = False
                            break
                    if not found:
                        print("You don't have that item")

                case s if s.startswith("setroomname "):
                    command, *room_name = s.split()
                    room_name = " ".join(room_name)
                    self.state.set_room_name(room_name)
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
                        buffer.append(line.rstrip())

                    # Join exactly as typed
                    raw_text = "\n".join(buffer)

                    # Split into paragraphs (blank lines separate them)
                    paragraphs = [p.strip() for p in raw_text.split("\n\n")]

                    wrapped_paragraphs = [
                        textwrap.fill(
                            p,
                            width=80,
                            break_long_words=False,
                            break_on_hyphens=False,
                        )
                        for p in paragraphs
                        if p
                    ]

                    # Rejoin with a blank line between paragraphs
                    room.desc = "\n\n".join(wrapped_paragraphs)

                case d if d.startswith("deleteroom "):
                    command, room_id = d.split()
                    self.state.delete_room(room_id)
                case s if s.startswith("spawn "):
                    command, search = s.split()
                    items = [
                        (key, item)
                        for (key, item) in self.state.items.items()
                        if search.lower() in item.name.lower()
                    ]
                    item_names = [item.name for (key, item) in items]
                    print(list(item_names))
                    choice = get_choice(
                        "Which item do you want to spawn?",
                        [*item_names, "Nevermind"],
                        returns_index=True,
                    )
                    if choice < len(items):
                        (item_id, item) = items[choice]
                        held_item = HeldItem()
                        held_item.item_id = item_id
                        held_item.durability = item.durability
                        room.items.append(held_item)

                case s if s.startswith("score"):
                    print(self.state.get_score())

                    needsprompt = False
                case q if q.startswith("quit"):
                    break

                case _:
                    if not self.state.go_direction(action):
                        print("you can't go that way")

            self.save_state()

    def get_actions(self) -> List[str]:
        actions = []
        roomid = self.state.campaign.room_id
        room = self.state.rooms[roomid]
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
        for stat in ROLLED_STATS:
            already_allocated_stat = getattr(character, stat) or 0
            stat_pool = stat_pool - already_allocated_stat

        def validate_stat(stat: int):
            return 0 <= stat and stat <= stat_pool

        if stat_pool > 0:
            print(f"Pick stats for {character_name}")
            while stat_pool > 0:
                for stat in ROLLED_STATS:
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
        except FileNotFoundError:
            self.state = State()
