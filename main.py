import asyncio

from src.game import Game
from tkinter import *
from src.user_io import ConsoleUserIO, UserIO, TkUserIO


async def main(user_io: UserIO):
    game = Game(user_io)
    await asyncio.gather(game.start(), game.background_task())


# from rich.console import Console
# from rich.layout import Layout
# from rich.panel import Panel

copy = """
Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.

Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.

Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.

Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.

Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
"""

if __name__ == "__main__":
    asyncio.run(main(ConsoleUserIO()))
if False:
    console = Console()
    layout = Layout()
    layout.split_column(
        Layout(name="top"),
        Layout(name="bottom"),
    )
    layout["top"].update(Panel("terminal screen"))
    layout["bottom"].update(Panel("input screen"))
    console.print(layout)
    console.print(layout)

    def key_handler_function(event):
        print("You clicked ENTER key in your keyboard")
        print(entry.get())
        entry.delete(0, END)

    root = Tk()
    width, height = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (width - 200, height - 200))
    root.bind("<Return>", key_handler_function)
    root.title("Game Window")
    # root.state("zoomed")

    main_frame = Frame(root)
    main_frame.pack(expand=True, fill="both")

    label_frame = Frame(main_frame)
    label_frame.pack(expand=True, fill="y")

    def update_wraplength(event):
        new_width = event.width
        label.config(wraplength=new_width)

    label = Label(label_frame, text=copy, justify="left", bg="#ff0000")
    label.pack(
        expand=True,
        fill="both",
    )
    label.bind("<Configure>", update_wraplength)

    entry_frame = Frame(main_frame)
    entry_frame.pack(expand=False, fill="x")

    entry = Entry(entry_frame)
    entry.pack(expand=True, fill="x")

    root.mainloop()
