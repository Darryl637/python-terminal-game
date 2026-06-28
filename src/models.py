from pydantic import BaseModel, Field
from typing import List, Literal, Union, Callable
from src.constants import NEW_GAME, STATS, ROLLED_STATS
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
    set_state_with_list,
    set_state_with_dict,
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


class Statistics(BaseModel):
    Strength: int = 0
    Dexterity: int = 0
    Wisdom: int = 0
    Intelligence: int = 0
    Constitution: int = 0
    hitroll: int = 0
    damageroll: int = 0
    armor: int = 0


class Character(Statistics):
    name: str = ""
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
    flags: dict[str, bool] = {}
    inventory: List[HeldItem] = []


class ItemBase(BaseModel):
    name: str = ""
    value: int = 0

    def fill(self):
        set_state_with_line(self, "name", "what is the item name")
        set_state_with_number(self, "value", "how much is it worth", is_non_negative)


WearLocation = Literal["head", "torso", "waist", "legs", "hands", "feet", "arms"]
wear_locations = ["head", "torso", "waist", "legs", "hands", "feet", "arms"]


class Combatable(ItemBase, Statistics):
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
    items: List[HeldItem] = []


CLONING_TUBE_ID = "vnum0"

ROOMS = {
    CLONING_TUBE_ID: Room(
        name="Cloning tube",
        desc="You are in a cloning tube\n",
        actions={},
    ),
}


class MobLocation(BaseModel):
    # is_visible: Callable[[Campaign], bool]
    room_id: str


def is_visible(state: Campaign):
    return True


class MobConversation(BaseModel):
    text: str = ""
    item_ids: list[str] = []
    set_flags: dict[str, bool] = {}
    visible_flags: dict[str, bool] = {}

    def fill(self):
        set_state_with_line(self, "text", "what do you want them to say")
        set_state_with_list(self, "item_ids", "what items ids should they have")
        set_state_with_dict(
            self, "set_flags", "what flag should update after conversation"
        )
        set_state_with_dict(
            self, "visible_flags", "what flag are needed to have conversation"
        )


class BasicMob(BaseModel):
    name: str
    locations: List[MobLocation] = []
    conversations: List[MobConversation] = []


def mob_location_room(room_id: str):
    def inner(campaign: Campaign):
        return campaign.room_id == room_id

    return inner


class State(BaseModel):
    campaigns: List[Campaign] = []
    rooms: dict[str, Room] = (
        ROOMS  # "Room" the quotes are saying to wait until file is loaded
    )
    campaign_index: int = -1
    items: dict[str, Item] = {"stuff": Weapon()}
    # makemob <name>
    # makemob addlocation <mobname> <room_id>
    # makemob <name> add_conversation
    mobs: List[BasicMob] = [
        BasicMob(
            name="droid",
            locations=[MobLocation(room_id="vnum0")],
            conversations=[
                MobConversation(
                    text="have you seen these jedi",
                    item_ids=["stuff"],
                    visible_flags={"got_item": False},
                    set_flags={"got_item": True},
                ),
                MobConversation(
                    text="Move along I'm busy",
                ),
            ],
        )
    ]

    @property
    def room(self) -> Room:
        room = self.rooms[self.campaign.room_id]
        return room

    @property
    def campaign(self):
        return self.campaigns[self.campaign_index]

    @property
    def characters(self):
        return self.campaign.characters

    def get_item_by_id(self, id: str):
        return self.items[id]

    def get(self, item_input: str):
        for index, held_item in enumerate(self.room.items):
            item = self.get_item_by_id(held_item.item_id)
            if item_input in item.name:
                self.campaign.inventory.append(held_item)
                self.room.items.pop(index)
                return True
        return False

    def drop(self, item_input):
        for index, held_item in enumerate(self.campaign.inventory):
            item = self.get_item_by_id(held_item.item_id)
            if item_input == item.name.lower():
                self.room.items.append(held_item)
                self.campaign.inventory.pop(index)

                return True
        return False

    def make(self, type, do_fill=True):
        match type:
            case "armor":
                item = Armor()

            case "weapon":
                item = Weapon()

            case _:
                return (None, None)
        if do_fill:
            item.fill()
        item_id = generate_id()
        self.items[item_id] = item
        return (
            item_id,
            item,
        )  # update test for make to work with key and value being returned. check that the item is at that key in dict not just within dict

    def make_mob(self, name):
        self.mobs.append(BasicMob(name=name))

    def make_mob_location(self, name, room_id):
        for mob in self.mobs:
            if mob.name == name:
                mob.locations.append(MobLocation(room_id=room_id))

    def make_mob_conversation(self, name, mob_conversation):
        for mob in self.mobs:
            if mob.name == name:
                mob.conversations.append(mob_conversation)

    def say(self, target: str):
        for mob in self.mobs:
            if mob.name == target:
                for location in mob.locations:
                    if location.room_id == self.campaign.room_id:
                        for conversation in mob.conversations:
                            if self._can_have_conversation(conversation):
                                return self._have_convsation(conversation)
                return "They have nothing to say"

    def _can_have_conversation(self, conversation):
        # detect if flag is set to override conversation
        for key, value in conversation.visible_flags.items():
            if self.campaign.flags.get(key, False) != value:
                return False
        return True

    def _have_convsation(self, conversation):
        # the [key] is the key value updating the value of the key
        for key, value in conversation.set_flags.items():
            self.campaign.flags[key] = value
        for item_id in conversation.item_ids:
            self.campaign.inventory.append(HeldItem(item_id=item_id))
        return conversation.text

    def calculate_score(self, character: Character):
        stats = {}
        add_stats(stats, character)
        for wear_location in wear_locations:
            for layer in getattr(character, wear_location):
                for layer_location in layer_locations:
                    held_item = getattr(layer, layer_location)
                    if held_item:
                        item = self.items[held_item.item_id]
                        if item:
                            add_stats(stats, item)
        return stats

    def get_score(self):

        output = []
        for index, character in enumerate(self.characters):
            if index:
                output.append("")
            output.append(f"-= Score for {character.name} =-")
            calculated_score = self.calculate_score(character)
            for stat in STATS:
                original_score = getattr(character, stat)
                output.append(f"{stat[0:3]}: {original_score}|{calculated_score[stat]}")

        return "\n".join(output)

    def search_rooms(self, search):
        filtered = [
            (room_id, room)
            for (room_id, room) in self.rooms.items()
            if search in room.name
        ]
        return "\n".join([f"{room.name}: {room_id}" for room_id, room in filtered])

    def make_exit(self, direction, room_id):
        self.room.actions[direction] = GoToRoomAction(room_id=room_id)

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

    def spawn(self, item_id, item):
        held_item = HeldItem()
        held_item.item_id = item_id
        held_item.durability = item.durability
        self.room.items.append(held_item)

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
