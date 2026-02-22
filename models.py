from pydantic import BaseModel
from typing import List, Literal


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
