import json
import random

NEW_GAME = 0

STATS = ["Strength", "Dexterity", "Wisdom", "Intelligence", "Consitution"]


#Using to check if index value is there, if not default value provided
def get_index(list, index, default):
    if index < len(list):
        return list[index]
    return default

def is_valid(*args):
    return True

def get_number(prompt, validator = is_valid):
    while True:
        print(prompt)
        try:
            number = int(input())
            if validator(number):
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
        set_state_with_number(self.campaign, "character_count", "How many characters are in your campaign? (1-4)", validate_campaign_player_count, True)
        self.save_state()
        characters = self.campaign.get("characters", [])
        self.campaign["characters"] = characters
        for i in range(self.campaign["character_count"]):
            character = get_index(characters, i, {})
            if i >= len(characters):
                characters.append(character)
            self.pick_stats(character)
      
        
        #Add while loop to stay in game?
        # while True:



        

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

    def pick_stats(self, character):
        set_state_with_line(character, "name", "What is your characters name?", True)
        self.save_state()
        character_name = character["name"]
        stat_pool = 75
        for stat in STATS:
            already_allocated_stat = character.get(stat, 0)
            stat_pool = stat_pool - already_allocated_stat
        

        def validate_stat(stat):
            return 0 <= stat and stat <= stat_pool
        if stat_pool > 0:
            print(f"Pick stats for {character_name}")
            while stat_pool > 0:
                for stat in STATS:
                    value = get_number(f"Pick your {stat} ({stat_pool} remaining points)", validate_stat)
                    already_allocated_stat = character.get(stat, 0)
                    stat_pool = stat_pool - value
                    character[stat] = value + already_allocated_stat
                    self.save_state()

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


