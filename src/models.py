from pydantic import BaseModel, Field
from typing import List, Literal, Union
from src.constants import NEW_GAME, STATS
from src.utility import (
    set_state_with_line,
    set_state_with_number,
    set_state_with_choice,
    is_non_negative,
    is_valid,
    is_positive,
    get_choice,
    generate_id,
    add_stats,
)


class HeldItem(BaseModel):
    item_id: str = ""
    durability: int = 500


class Layers(BaseModel):
    first: Union[HeldItem, None] = None
    second: Union[HeldItem, None] = None
    third: Union[HeldItem, None] = None
    forth: Union[HeldItem, None] = None
    fifth: Union[HeldItem, None] = None


class Character(BaseModel):
    name: str = ""
    Strength: int = 0
    Dexterity: int = 0
    Wisdom: int = 0
    Intelligence: int = 0
    Constitution: int = 0
    hitroll: int = 0
    damroll: int = 0
    armor: int = 0
    head: List[
        Layers
    ] = []  # This represents items being worn by each head 1+ head locations

    torso: List[Layers] = []
    waist: List[Layers] = []
    legs: List[Layers] = []
    hands: List[Layers] = []
    feet: List[Layers] = []
    arms: List[Layers] = []


class Campaign(BaseModel):
    characters: List[Character] = []
    name: str = ""
    room_id: str = ""
    character_count: int = 0
    inventory: List[HeldItem] = []


class ItemBase(BaseModel):
    name: str = ""
    value: int = 0

    def fill(self):
        set_state_with_line(self, "name", "what is the item name")
        set_state_with_number(self, "value", "how much is it worth", is_non_negative)


WearLocation = Literal["head", "torso", "waist", "legs", "hands", "feet", "arms"]
wear_locations = ["head", "torso", "waist", "legs", "hands", "feet", "arms"]


class Combatable(ItemBase):
    damageroll: int = 1
    hitroll: int = 1
    durability: int = 500

    def fill(self):
        super().fill()
        set_state_with_number(self, "damageroll", "What is the damageroll", is_valid)
        set_state_with_number(self, "hitroll", "What is the hitroll", is_valid)
        set_state_with_number(self, "durability", "What is the durability", is_positive)


class Wearable(Combatable):
    wear_location: WearLocation = "torso"

    def fill(self):
        super().fill()
        set_state_with_choice(self, "wear_location", "Where is it worn", wear_locations)


LayerLocation = Literal["first", "second", "third", "forth", "fifth"]
layer_locations = ["first", "second", "third", "forth", "fifth"]


class Armor(Wearable):
    type: Literal["Armor"] = "Armor"
    armor: int = 0
    layer_loc: LayerLocation = "first"

    def fill(self):
        super().fill()
        set_state_with_choice(
            self, "layer_loc", "what is the layer location", layer_locations
        )
        set_state_with_number(self, "armor", "what is armor stat", is_non_negative)


class Weapon(Combatable):
    type: Literal["Weapon"] = "Weapon"

    def fill(self):
        super().fill()


Item = Union[Armor, Weapon]


class GoToRoomAction(BaseModel):
    action: Literal["gotoroom"] = "gotoroom"
    room_id: str


Action = GoToRoomAction


class Room(BaseModel):
    name: str = ""
    desc: str = ""
    actions: dict[str, Action] = {}
    items: List[str] = []


CLONING_TUBE_ID = "vnum0"

ROOMS = {
    CLONING_TUBE_ID: Room(
        name="Cloning tube",
        desc="You are in a cloning tube\n",
        actions={},
    ),
}


class State(BaseModel):
    campaigns: List[Campaign] = []
    rooms: dict[str, Room] = (
        ROOMS  # "Room" the quotes are saying to wait until file is loaded
    )
    campaign_index: int = -1
    items: dict[str, Item] = {}

    @property
    def room(self):
        room = self.rooms[self.campaign.room_id]
        return room

    @property
    def campaign(self):
        return self.campaigns[self.campaign_index]

    @property
    def characters(self):
        return self.campaign.characters

    def calulate_score(self):
        characters = []
        for character in self.characters:
            stats = {}
            add_stats(stats, character)
            for wear_location in wear_locations:
                for layer in getattr(character, wear_location):
                    for layer_location in layer_locations:
                        held_item = getattr(layer, layer_location)
                        if held_item:
                            item = self.items[held_item.item_id]
                            if item:
                                print(held_item)
                                add_stats(stats, item)
            print(stats)
        raise Exception()

    def get_score(self):
        self.calulate_score()
        output = []
        for character in self.characters:
            output.append(f"-= Score for {character.name} =-")
            for stat in STATS:
                output.append(f"{stat[0:3]}: {getattr(character, stat)}")
            output.append("")

            output.append(
                f"hitroll: {character.hitroll}, damroll: {character.damroll}, armor: {character.armor}"
            )
        return "\n".join(output)

    def delete_room(self, room_id: str):
        del self.rooms[room_id]
        for room in self.rooms.values():
            for action_key, action_value in dict(room.actions).items():
                if action_value.room_id == room_id:
                    del room.actions[action_key]

    def set_room_name(self, room_name: str):
        self.room.name = room_name

    def make_roomc(self, room_name: str, todirection: str, fromdirection: str):
        _, room = self.make_room(todirection, room_name)
        room.actions[fromdirection] = GoToRoomAction(room_id=self.campaign.room_id)

    def make_room(self, direction: str, room_name: str):
        room_id = generate_id()
        self.room.actions[direction] = GoToRoomAction(room_id=room_id)
        room = Room(name=room_name, desc="", actions={})
        self.rooms[room_id] = room
        return room_id, room

    def go_direction(self, direction: str) -> bool:
        match self.room.actions.get(direction):
            case a if isinstance(a, GoToRoomAction):
                room_id = a.room_id

                self.campaign.room_id = room_id
                return True
        return False

    def choose_campaign(self):
        campaigns = self.campaigns or []
        options = ["New Game"]
        for campaign in campaigns:
            options.append(campaign.name)
        option = get_choice("Choose your campaign: ", options, True)
        if option == NEW_GAME:
            campaign = Campaign(name="Campaign " + str(option + len(options)))
            campaigns.append(campaign)
            self.campaigns = campaigns
            # self.save_state()
            self.campaign_index = len(campaigns) - 1
        else:
            self.campaign_index = option - 1
        self.campaign.room_id = self.campaign.room_id or CLONING_TUBE_ID

    def show_equipment(self):
        output = []
        for index, character in enumerate(self.characters):
            if index:
                output.append("")
            output.append(f"Name: {character.name.upper()}")
            output.append("")
            for location in wear_locations:
                layers = getattr(character, location)
                if layers:
                    for layer_index, layer in enumerate(layers):
                        if len(layers) > 1:
                            output.append(f"{location} {layer_index + 1}:")
                        else:
                            output.append(f"{location}:")
                        for layer_location in layer_locations:
                            held_item = getattr(layer, layer_location)
                            if held_item:
                                item = self.items[held_item.item_id]
                                if item:
                                    output.append(
                                        f"\t{layer_location}: {item.name} ({held_item.durability} / {item.durability})"
                                    )

        return "\n".join(output)
