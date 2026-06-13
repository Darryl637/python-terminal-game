from colorama import Fore
from typing import List
from src.models import (
    Action,
    State,
    Character,
    GoToRoomAction,
    Armor,
    Weapon,
    HeldItem,
)


from src.constants import ROLLED_STATS
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
from src.commands import run_command, DO_NOT_PRINT, QUIT

import hmr

run_command = hmr.reload(run_command)


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
                for mob in self.state.mobs:
                    for location in mob.locations:
                        if location.room_id == room_id:
                            print(f"{mob.name} is in the room")
                            break

                for item in room.items:
                    print(item)
            needsprompt = True

            line = get_line(">")

            match line:
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

                case _:
                    result = run_command(state=self.state, line=line)
                    if result == DO_NOT_PRINT:
                        needsprompt = False
                    if result == QUIT:
                        break

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
        contents = self.state.model_dump_json(indent=2)
        with open("state.json", "w") as f:
            f.write(contents)

    def load_state(self):
        try:
            with open("state.json", "r") as f:
                contents = f.read()
                self.state = State.model_validate_json(contents)
        except FileNotFoundError:
            self.state = State()
