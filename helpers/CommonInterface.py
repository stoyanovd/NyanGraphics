import json


class GAME_CONF:
    # steps of cat in one game run
    STEPS_NUMBER = 100

    # repeats of sending message through UDP
    #  p=0.05  # probability of one loss - in real it must be less
    #  k=100   #  STEPS_NUMBER
    #  r=4     # REPEATS_NUMBER
    #  (1-p^r)^k
    # 	~0.99937519331990344353 # probability of having zero lost packets in one game run

    ONE_STEP_TIME_LIMIT_SEC = 1
    REPEATS_NUMBER = 4

    FIELD_SIZE = 4
    assert 4 <= FIELD_SIZE <= 20


WHOIS = "whois"
CAT = "cat"
HUNTER = "hunter"

INIT = "init"
BOT_STEP = "bot_step"
REQUEST_FOR_STEP = "request_for_step"

GAME_MAP = "game_map"

RUN_NUMBER = "run_number"
CAT_BOT_NAME = "cat_bot_name"

STEPS_NUMBER = "steps_number"
FIELD_SIZE = 'field_size'

TELEPORTS = "teleports"

# no two teleports FROM one cell
FROM_X = "from_x"
FROM_Y = "from_y"
TO_X = "to_x"
TO_Y = "to_y"

TIME_FRAME = "time_frame"

DIRECTION = "direction"

LEFT = "LEFT"
RIGHT = "RIGHT"
DOWN = "DOWN"
UP = "UP"
TELEPORT = "TELEPORT"
HERE = "HERE"

CUR_X = "cur_x"
CUR_Y = "cur_y"


# Coordinates go from 0
# e.g from (0, 0) to (15, 15)
# Zero coordinates are in LEFT-UP corner

def cell_is_correct(p):
    return (0 <= p[0] < GAME_CONF.FIELD_SIZE) and (0 <= p[1] < GAME_CONF.FIELD_SIZE)


# LOOK HERE!                               local          UDP multicast           local
# We have such connections:   NyanCatBot <-------> Server --------------> Client <-------> HunterBot


# INIT message from Server to Client
# Server duplicates it to NyanCatBot
# Client duplicates it to HunterBot

def pack_init(run_number, game_map, cat):
    assert isinstance(run_number, int)
    assert isinstance(cat.bot_name, str)
    # and assert teleports coords are correct

    d = {
        INIT:
            {
                RUN_NUMBER: run_number,
                CAT_BOT_NAME: cat.bot_name,
                STEPS_NUMBER: GAME_CONF.STEPS_NUMBER,
                FIELD_SIZE: GAME_CONF.FIELD_SIZE,
                GAME_MAP:
                    {
                        TELEPORTS:
                            [
                                {
                                    FROM_X: t[0],
                                    FROM_Y: t[1],
                                    TO_X: t[2],
                                    TO_Y: t[3]
                                }
                                for t in game_map.teleports
                                ]
                    }
            }
    }
    s = json.dumps(d)
    return s


# common format for
#   NyanCat to Server message (forward it to Client, and than to HunterBot)
# and to
#   Hunter to Client message

def pack_bot_step(run_number, time_frame, whois, direction):
    assert isinstance(run_number, int)
    assert isinstance(time_frame, int)
    assert whois in [CAT, HUNTER]
    assert direction in [LEFT, RIGHT, DOWN, UP, TELEPORT, HERE]

    d = {
        BOT_STEP:
            {
                RUN_NUMBER: run_number,
                TIME_FRAME: time_frame,
                WHOIS: whois,
                DIRECTION: direction,
            }
    }

    s = json.dumps(d)
    return s


# Bot can send not correct direction - in this case, his step will not be made by client/server.
# and in next request Bot will learn it.

# Cat/Hunter start positions are set randomly by Server/Client and will be sent with first request.

# request for step
# common format for
#   Server to NyanCat message
# and to
#   Client to Hunter message

# direction is fictive for NyanCatBot

def pack_request_for_step(run_number, time_frame, direction_to_cat, position):
    assert isinstance(run_number, int)
    assert isinstance(time_frame, int)
    # and assert position is correct

    d = {
        REQUEST_FOR_STEP:
            {
                RUN_NUMBER: run_number,
                TIME_FRAME: time_frame,
                DIRECTION: direction_to_cat,
                CUR_X: position[0],
                CUR_Y: position[1]
            }
    }

    s = json.dumps(d)
    return s
