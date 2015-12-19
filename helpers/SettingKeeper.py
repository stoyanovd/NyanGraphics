from helpers import CommonInterface


class SK:
    FPS = 60.0

    CELL_SQ = 150
    CELL_HEIGHT = CELL_SQ
    CELL_WIDTH = CELL_SQ

    MINIMUM_WINDOW_SIZE = (1600, 1200)

    STEPS = {
        CommonInterface.LEFT: [-1, 0],
        CommonInterface.RIGHT: [1, 0],
        CommonInterface.DOWN: [0, 1],
        CommonInterface.UP: [0, -1],
        CommonInterface.HERE: [0, 0],
        CommonInterface.TELEPORT: None
    }

    TO_CLIENT_VIS_FIFO = 'tc'
    TO_SERVER_VIS_FIFO = 'ts'


class Stater:
    cat_p = None
    hunter_p = None
    cat_direction = None