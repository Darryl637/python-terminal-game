from pydantic import BaseModel, Field
from typing import List, Literal, Union
from src.utility import generate_id
from src.constants import NEW_GAME
from src.utility import get_choice
from src.items import Wearable, Armor, Weapon, Layers, ItemBase


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
    inventory: List[str] = []


Item = Union[Armor, Weapon]


class State(BaseModel):
    campaigns: List[Campaign] = []
    rooms: dict[
        str, "Room"
    ] = {}  # "Room" the quotes are saying to wait until file is loaded
    campaign_index: int = -1
    items: dict[str, Item] = {}

    @property
    def campaign(self):
        return self.campaigns[self.campaign_index]

    def make_room(self, direction: str, room_name: str):
        room = self.rooms[self.campaign.room_id]
        room_id = generate_id()
        room.actions[direction] = GoToRoomAction(room_id=room_id)
        self.rooms[room_id] = Room(name=room_name, desc="", actions={})

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
            self.save_state()
            self.campaign_index = len(campaigns) - 1
        else:
            self.campaign_index = option - 1
        self.campaign.room_id = self.campaign.room_id or CLONING_TUBE_ID


class Room(BaseModel):
    name: str = ""
    desc: str = ""
    actions: dict[str, "Action"] = {}
    items: List[str] = []


class GoToRoomAction(BaseModel):
    action: Literal["gotoroom"] = "gotoroom"
    room_id: str


Action = GoToRoomAction

CLONING_TUBE_ID = "vnum0"

ROOMS = {
    CLONING_TUBE_ID: Room(
        name="Cloning tube",
        desc="You are in a cloning tube\n",
        actions={},
    ),
}
