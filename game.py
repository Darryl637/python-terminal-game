import json
import random

NEW_GAME = 0

def game_enter_number(self, prompt):
    match_number = random.randint(1, 99)
    print(f"{prompt} {match_number}")
    
    number = int(input())
    while number != match_number:
        print(f"Try typing {match_number}")
        number = int(input())
    print("Match, Unlocking gameplay!")

def get_number(prompt, validator = None):
    while True:
        print(prompt)
        try:
            number = int(input())
            if not validator or validator(number):
                return number
        except:
            pass
        print("Try again") 

def set_state_with_line(map, path, prompt, skip_if_has_value = False):
    if skip_if_has_value and path in map:
        return
    map[path] = get_line(prompt)

def set_state_with_number(map, path, prompt, validator, skip_if_has_value = False):
    if skip_if_has_value and path in map:
        return
    map[path] = get_number(prompt, validator)

def set_state_with_choice(map, path, prompt, options, skip_if_has_value = False):
    if skip_if_has_value and  path in map:
        return
    map[path] = get_choice(prompt, options)

def get_line(prompt):
    return input(prompt + "\n")

def get_choice(prompt, options, returns_index = False):
    while True:
        try:
            print(prompt)
            for index, option in enumerate(options):
                print(f"{index + 1}. {option}")
            value = input()
            number = int(value) -1
            if 0 <= number and number < len(options):
                if returns_index:
                    return number
                return options[number]
        except:
            pass
        print("Try again")

def validate_campaign_player_count(number):
    return number > 0 and number < 5

class Game:

    def __init__(self):
        self.load_state()
    def start(self):
        self.campaign = self.choose_campaign()
        print(self.campaign["name"])
        set_state_with_number(self.campaign, "player_count", "How many players are in your campaign? (1-4)", validate_campaign_player_count, True)
        players = []
        for i in range(self.campaign["player_count"]):
            player = {}
            player["Strength"] = random.randint(10, 21)
            players.append(player)
        self.campaign["players"] = players
        self.save_state()

    def choose_campaign(self):
        campaigns = self.state.get("campaigns", [])
        options = ["New Game"]
        for campaign in campaigns:
            options.append(campaign["name"])
        option = get_choice("Choose your campaign: ", options, True)
        if option == NEW_GAME:
            campaign = {
                "name":"Campaign " + str(option + len(options)),
            }
            campaigns.append(campaign)
            self.state["campaigns"] = campaigns
            self.save_state()
            return campaign
        return campaigns[option - 1]


        
        


    @property    
    def gender(self):
        return self.state["gender"]



    # def set_state_for_race(self, path, prompt, options, skip_if_has_value = False):
    #     if skip_if_has_value and self.state[path]:
    #         return
    #     self.state[path] = self.


    def save_state(self):
        with open("state.json", "w") as f:
            contents = json.dumps(self.state, indent=2)
            f.write(contents)

    def load_state(self):
        try:
            with open("state.json", "r") as f:
                contents = f.read()
                self.state = json.loads(contents)
        except:
            self.state = {}


