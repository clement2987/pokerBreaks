from helpers import load_settings

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


if __name__=="__main__":
    print(TOTAL_TIME)