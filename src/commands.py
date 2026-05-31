from src.models import State, MobConversation
from typing import Callable

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

    def __init__(self, call_back, description, args=[]):
        self.args = args
        self.description = description
        self.call_back = call_back

    def syntax(self, command_name: str):
        args = " ".join([arg for arg in self.args])
        args = f" {args}" if args else ""
        return f"Syntax: {command_name}{args} - {self.description}"


def setroomname(arguments: CommandArguments):
    room_name = " ".join(arguments.argv)
    arguments.state.set_room_name(room_name)


def help(arguments):
    for key, value in commands.items():
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


commands = dict(
    sorted(
        {
            "setroomname": Command(
                setroomname,
                description="sets the name of the room",
                args=["<room name>"],
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
        }.items()
    )
)


def run_command(state: State, line: str):
    command_name, *argv = line.split()
    arguments = CommandArguments(state, argv)
    if command_name in commands:
        command = commands[command_name]
        if len(argv) < len(command.args):
            print("Not enough arguments")
            print(command.syntax(command_name))
        else:
            return command.call_back(arguments)
    elif state.go_direction(command_name):
        return
    else:
        print("you can't go that way")
    return DO_NOT_PRINT
