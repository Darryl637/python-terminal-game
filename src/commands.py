from src.models import State, MobConversation, HeldItem, Armor, Weapon
from typing import Callable
import textwrap
from src.utility import get_choice, generate_id


DO_NOT_PRINT = 1
QUIT = 2


class CommandArguments:
    state: State
    argv: list[str]

    def __init__(self, state, argv):
        self.state = state
        self.argv = argv


class Command:
    call_back: Callable[[CommandArguments], int]
    args: list[str]
    description: str
    short_hand: list[str]
    is_short_hand: bool = False

    def __init__(self, call_back, description, args=[], short_hand=[]):
        self.args = args
        self.description = description
        self.call_back = call_back
        self.short_hand = short_hand

    def make_short_hand(self):
        short_hand = Command(self.call_back, self.description, self.args, [])
        short_hand.is_short_hand = True
        return short_hand

    def syntax(self, command_name: str):
        args = " ".join([arg for arg in self.args])
        args = f" {args}" if args else ""
        short_hand = ", ".join([short_hand for short_hand in self.short_hand])
        short_hand = f" [{short_hand}]" if short_hand else ""

        return f"Syntax: {command_name}{args} - {self.description}{short_hand}"


def setroomname(arguments: CommandArguments):
    room_name = " ".join(arguments.argv)
    arguments.state.set_room_name(room_name)


def setroomdesc(arguments: CommandArguments):
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
    arguments.state.room.desc = "\n\n".join(wrapped_paragraphs)


def help(arguments):
    for key, value in commands.items():
        if not value.is_short_hand:
            print(value.syntax(key))
    return DO_NOT_PRINT


def score(arguments: CommandArguments):
    print(arguments.state.get_score())
    return DO_NOT_PRINT


def quit(arguments: CommandArguments):
    return QUIT


def make_mob(arguments: CommandArguments):
    name = arguments.argv[0]
    if len(arguments.argv) == 1:
        arguments.state.make_mob(name)
    else:
        subcommand = arguments.argv[1]
        if subcommand == "add_location":
            room_id = arguments.argv[2]
            arguments.state.make_mob_location(name, room_id)
        if subcommand == "add_conversation":
            mob_conversation = MobConversation()
            mob_conversation.fill()
            arguments.state.make_mob_conversation(name, mob_conversation)

    return DO_NOT_PRINT


def delete_room(arguments: CommandArguments):
    room_id = arguments.argv[0]
    arguments.state.delete_room(room_id)


def make_exit(arguments: CommandArguments):
    direction = arguments.argv[0]
    room_id = arguments.argv[1]
    arguments.state.make_exit(direction, room_id)


def search_room(arguments: CommandArguments):
    print(arguments.state.search_rooms(" ".join(arguments.argv)))
    return DO_NOT_PRINT


# makeroom function from game.py
def makeroom(arguments: CommandArguments):
    todirection, fromdirection, *room_name_list = arguments.argv
    room_name = " ".join(room_name_list)
    arguments.state.make_roomc(room_name, todirection, fromdirection)


def say(arguments: CommandArguments):
    target = arguments.argv[0]
    conversation = arguments.state.say(target)
    if conversation:
        print(conversation)
    else:
        print("Who are you trying to talk to?")
    return DO_NOT_PRINT


def look(_: CommandArguments):
    pass


def vin(arguments: CommandArguments):
    print(arguments.state.campaign.room_id)
    return DO_NOT_PRINT


def equipment(arguments: CommandArguments):
    print(arguments.state.show_equipment())
    return DO_NOT_PRINT


def inventory(arguments: CommandArguments):
    print("Inventory:")
    items = arguments.state.campaign.inventory
    for held_item in items:
        item = arguments.state.get_item_by_id(held_item.item_id)
        print(item.name)
    return DO_NOT_PRINT


def make(arguments: CommandArguments):
    type = arguments.argv[0].lower()
    if not arguments.state.make(type):
        print(f"{type} not allowed")
    return DO_NOT_PRINT


def spawn(arguments: CommandArguments):
    search = arguments.argv[0]
    items = [
        (key, item)
        for (key, item) in arguments.state.items.items()
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
        arguments.state.spawn(item_id, item)


def destroy(arguments: CommandArguments):
    item_input = " ".join(arguments.argv)
    for held_item in arguments.state.room.items:
        item = arguments.state.get_item_by_id(held_item.item_id)
        if item_input == item.name:
            arguments.state.room.items.remove(item)


def drop(arguments: CommandArguments):
    item_input = " ".join(arguments.argv).lower()
    if not arguments.state.drop(item_input):
        print("You don't have that item")
        return DO_NOT_PRINT


def get(arguments: CommandArguments):
    item_input = " ".join(arguments.argv)
    if not arguments.state.get(item_input):
        print("That item is not here")
        return DO_NOT_PRINT


commands = dict(
    sorted(
        {
            "setroomname": Command(
                setroomname,
                description="sets the name of the room",
                args=["<room name>"],
            ),
            "setroomdesc": Command(
                setroomdesc,
                description="sets the description of the room",
                args=[],
            ),
            "help": Command(
                help, description="prints help information for all commands"
            ),
            "score": Command(score, description="prints characters score sheet"),
            "quit": Command(quit, description="exits the game"),
            "deleteroom": Command(
                delete_room,
                description="deletes room and connecting exits",
                args=["<room id>"],
            ),
            "searchrooms": Command(search_room, description="", args=[]),
            # makeroom help
            "makeroom": Command(
                makeroom,
                description="todo",
                args=["<todirection>", "<fromdirection>", "<room_name>"],
            ),
            "say": Command(
                say, description="What do you want to say", args=["<target>"]
            ),
            "makemob": Command(make_mob, description="", args=["<name>"]),
            "look": Command(look, description="reprints character view of room"),
            "vin": Command(
                vin, description="shows the vin of the current room you are in"
            ),
            "equipment": Command(
                equipment,
                description="list characters equipment",
                short_hand=["eq"],
            ),
            "inventory": Command(
                inventory,
                description="campaign items",
                short_hand=["i", "inv"],
            ),
            "spawn": Command(
                spawn,
                description="spawn item into room",
            ),
            "make": Command(make, description="make things", args=["<type>"]),
            "get": Command(get, description="picks up item", args=["<item>"]),
            "drop": Command(drop, description="drops item", args=["<item>"]),
        }.items()
    )
)


for command in list(commands.values()):
    for short_hand in command.short_hand:
        if short_hand in commands:
            print(f"{short_hand} already exists")
        commands[short_hand] = command.make_short_hand()


def invoke(command_name, command, arguments):
    if len(arguments.argv) < len(command.args):
        print("Not enough arguments")
        print(command.syntax(command_name))
        return DO_NOT_PRINT
    else:
        return command.call_back(arguments)


def run_command(state: State, line: str):
    command_line = line.split()
    if len(command_line) < 1:
        return DO_NOT_PRINT
    command_name, *argv = command_line
    arguments = CommandArguments(state, argv)
    if command_name in commands:
        command = commands[command_name]
        return invoke(command_name, command, arguments)
    if state.go_direction(command_name):
        return
    print("you can't go that way")
    return DO_NOT_PRINT
