import json

def get_line(prompt):
    return input(prompt + "\n")

def get_choice(prompt, options):
    while True:
        try:
            print(prompt)
            for index, option in enumerate(options):
                print(f"{index + 1}. {option}")
            value = input()
            number = int(value) -1
            if number < len(options):
                return options[number]
        except:
            pass
        print("Try again")

def save_state(state):
    with open("state.json", "w") as f:
        contents = json.dumps(state)
        f.write(contents)


def load_state():
    try:
        with open("state.json", "r") as f:
            contents = f.read()
            return json.loads(contents)
    except:
        return {}

def main():
    state = load_state()
    print(state)
    state["name"] = get_line("What is your name?")
    save_state(state)
    print(f"Hello {state['name']}")
    state["gender"] = get_choice("What is your gender?", ["Male", "Female"])
    save_state(state)
    print(state["gender"])

    

if __name__ == "__main__":
    main()