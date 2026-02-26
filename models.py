from pydantic import BaseModel
from typing import List, Literal
from utility import generate_id
from constants import NEW_GAME
from utility import get_choice


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
    campaign_index: int = -1

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
