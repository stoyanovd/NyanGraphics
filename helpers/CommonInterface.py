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

    REPEATS_NUMBER = 4

    FIELD_SIZE = 16
    assert 4 <= FIELD_SIZE <= 20


CAT = "cat"  # not in use at the moment
HUNTER = "hunter"  # not in use at the moment

INIT = "init"
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

LEFT = 'LEFT'
RIGHT = 'RIGHT'
DOWN = 'DOWN'
UP = 'UP'
TELEPORT = 'TELEPORT'

CUR_X = 'cur_x'
CUR_Y = 'cur_y'


# Coordinates go from 0
# e.g from (0, 0) to (15, 15)
# Zero coordinates are in LEFT-UP corner

# LOOK HERE!                               local          UDP multicast           local
# We have such connections:   NyanCatBot <-------> Server --------------> Client <-------> HunterBot


# INIT message from Server to Client
# Server duplicates it to NyanCatBot
# Client duplicates it to HunterBot

def pack_init(run_number, game_map, cat):
    assert isinstance(run_number, int)
    assert isinstance(cat.bot_name, str)
    # and assert teleports coords are correct

    s = b""
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
                            {
                                [
                                    {
                                        FROM_X: t.from_p.x,
                                        FROM_Y: t.from_p.y,
                                        TO_X: t.to_p.x,
                                        TO_Y: t.to_p.y
                                    }
                                    for t in game_map.teleports]
                            }
                    }
            }
    }
    json.dump(d, s)
    return s


# common format for
#   NyanCat to Server message (forward it to Client, and than to HunterBot)
# and to
#   Hunter to Client message

def pack_bot_step(run_number, time_frame, direction):
    assert isinstance(run_number, int)
    assert isinstance(time_frame, int)
    assert direction in [LEFT, RIGHT, DOWN, UP, TELEPORT]

    s = b""
    d = {
        RUN_NUMBER: run_number,
        TIME_FRAME: time_frame,
        DIRECTION: direction,
    }

    json.dump(d, s)
    return s


# Bot can send not correct direction - in this case, his step will not be made by client/server.
# and in next request Bot will learn it.

# request for step
# common format for
#   Server to NyanCat message
# and to
#   Client to Hunter message

# direction is fictive for NyanCatBot

def pack_request_for_step(run_number, time_frame, direction, position):
    assert isinstance(run_number, int)
    assert isinstance(time_frame, int)
    # and assert position is correct

    s = b""
    d = {
        RUN_NUMBER: run_number,
        TIME_FRAME: time_frame,
        DIRECTION: direction,
        CUR_X: position.x,
        CUR_Y: position.y
    }

    json.dump(d, s)
    return s
