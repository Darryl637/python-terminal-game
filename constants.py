from models import Room

NEW_GAME = 0

STATS = ["Strength", "Dexterity", "Wisdom", "Intelligence", "Constitution"]

CLONING_TUBE_ID = "vnum0"

ROOMS = {
    CLONING_TUBE_ID: Room(
        name="Cloning tube",
        desc="You are in a cloning tube\n",
        actions={},
    ),
}
