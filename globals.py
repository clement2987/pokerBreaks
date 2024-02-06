import json

def load_settings():
    """
    opens settings.json and returns a dict object of the users chosen settings
    """
    with open("settings.json", "r") as file:
        return json.load(file)
    
def save_settings(settings):
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=4)

import copy

settings = load_settings()

# the number of seconds for times
BREAK_TIME = int(settings['times']['break'])

MAX_PLAY_TIME = int(settings['times']['btwn_break'])

TOTAL_TIME = BREAK_TIME + MAX_PLAY_TIME

DAY = 86400

HOUR = 3600

MINUTE = 60

# daylight savings variables
TIME_TO_THREE_AM = 75600

TIME_TO_TWO_AM = 72000

LOCATION = "melbourne"

TABLES = copy.deepcopy(settings['tables'])
GAMES = copy.deepcopy(settings['game_type'])

TODAY = None

DOMAIN = settings["domain"]
KEY = "test_123"


if __name__=="__main__":
    print(TOTAL_TIME)