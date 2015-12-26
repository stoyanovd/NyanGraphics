import os

from helpers import CommonInterface


class SK:
    FPS = 60.0

    CELL_SQ = 150
    CELL_HEIGHT = CELL_SQ
    CELL_WIDTH = CELL_SQ

    # MINIMUM_WINDOW_SIZE = (1600, 1200)
    MINIMUM_WINDOW_SIZE = (600, 450)

    STEPS = {
        CommonInterface.LEFT: [-1, 0],
        CommonInterface.RIGHT: [1, 0],
        CommonInterface.DOWN: [0, 1],
        CommonInterface.UP: [0, -1],
        CommonInterface.HERE: [0, 0],
        CommonInterface.TELEPORT: None
    }

    ROOM_NUMBER = 1
    TO_CLIENT_VIS_FIFO = os.path.join('.', 'nyan_tc')
    TO_SERVER_VIS_FIFO = os.path.join('.', 'nyan_ts')


class Stater:
    def __init__(self):
        self.cat_p = None
        self.hunter_p = None
        self.cat_direction = None
