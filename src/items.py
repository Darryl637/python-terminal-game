from pydantic import BaseModel
from typing import Literal


class ItemBase(BaseModel):
    name: str = ""
    value: int = 0


WearLocation = Literal["head", "torso", "waist", "legs", "hands", "feet", "arms"]
wear_location = ["head", "torso", "waist", "legs", "hands", "feet", "arms"]


class Wearable(ItemBase):
    wear_location: WearLocation = "torso"
    damageroll: int = 1
    hitroll: int = 1


LayerLocation = Literal["first", "second", "third", "forth", "fifth"]
layer_location = ["first", "second", "third", "forth", "fifth"]


class Armor(Wearable):
    armor: int = 0
    layer_loc: LayerLocation = "first"


class Weapon(Wearable):
    pass


class Layer(BaseModel):
    item_id: str
    # durability instance


class Layers(BaseModel):
    first: Layer | None = None
    second: Layer | None = None
    third: Layer | None = None
    forth: Layer | None = None
    fifth: Layer | None = None
