from game import Game


def main():
    game = Game()
    game.start()
    # game.set_state_with_line("name", "What is your name?", True)
    # print(f"Greetings, {game.state['name']}")
    # game.set_state_with_choice("gender", "What is your gender?", ["Male", "Female"], True)
    # print(game.gender)

    # game.set_state_for_race("race", "Choose a race" ["Wookiee", "Human", "Ewok", "Verpine", "Hutt"], True)

    # game.game_enter_number("Enter number on screen:")


if __name__ == "__main__":
    main()
