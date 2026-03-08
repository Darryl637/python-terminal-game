from pydantic import BaseModel
from typing import Literal


class ItemBase(BaseModel):
    name: str
    item_id: str
    value: int


WearLocation = Literal["head", "torso", "waist", "legs", "hands", "feet", "arms"]


class Wearable(ItemBase):
    wear_location: WearLocation
    damageroll: int
    hitroll: int


LayerLocation = Literal["first", "second", "third", "forth", "fifth"]


class Armor(Wearable):
    armor: int
    layer_loc: LayerLocation


class Weapon(Wearable):
    pass


class Layer(BaseModel):
    item_id: str


class Layers(BaseModel):
    first: Layer | None = None
    second: Layer | None = None
    third: Layer | None = None
    forth: Layer | None = None
    fifth: Layer | None = None
