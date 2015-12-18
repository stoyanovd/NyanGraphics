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


CAT = "cat"
HUNTER = "hunter"

INIT = "init"
RUN_NUMBER = "run_number"

TIME_FRAME = "time_frame"
DIRECTION = "direction"

CAT_BOT_NAME = "cat_bot_name"
STEPS_NUMBER = "steps_number"

GAME_MAP = "game_map"
TELEPORTS = "teleports"

LEFT = 'LEFT'
RIGHT = 'RIGHT'
DOWN = 'DOWN'
UP = 'UP'
TELEPORT = 'TELEPORT'

FROM_X = "from_x"
FROM_Y = "from_y"
TO_X = "to_x"
TO_Y = "to_y"


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


# message about step
# common format for
#   NyanCat to Server message (forward it to Client, and than to HunterBot)
# and to
#   Hunter to Client message

def pack_step(run_number, time_frame, direction):
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
