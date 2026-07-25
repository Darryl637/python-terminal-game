from src.game import Game
import asyncio


async def background_task():
    while True:
        print("Background task running...")
        await asyncio.sleep(2)


async def run():
    await asyncio.gather(getuserinput(), background_task())


async def getuserinput():
    # Run background task and input task concurrently
    while True:
        user_text = await async_input("Enter something: ")
        print(f"You typed: {user_text}")
        if user_text.lower() == "quit":
            print("Exiting...")
            break


async def main():
    game = Game()
    await game.start()
    # game.set_state_with_line("name", "What is your name?", True)
    # print(f"Greetings, {game.state['name']}")
    # game.set_state_with_choice("gender", "What is your gender?", ["Male", "Female"], True)
    # print(game.gender)

    # game.set_state_for_race("race", "Choose a race" ["Wookiee", "Human", "Ewok", "Verpine", "Hutt"], True)

    # game.game_enter_number("Enter number on screen:")


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(run())
    # main()
