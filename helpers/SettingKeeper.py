from helpers import CommonInterface
from helpers.Point import Point


class SK:
    FPS = 60.0

    CELL_SQ = 150
    CELL_HEIGHT = CELL_SQ
    CELL_WIDTH = CELL_SQ

    MINIMUM_WINDOW_SIZE = (1600, 1200)

    STEPS = {
        CommonInterface.LEFT: Point([-1, 0]),
        CommonInterface.RIGHT: Point([1, 0]),
        CommonInterface.DOWN: Point([0, 1]),
        CommonInterface.UP: Point([0, -1]),
        CommonInterface.TELEPORT: None
    }
