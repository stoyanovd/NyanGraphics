from helpers.Point import Point


class SK:
    FIELD_SIZE = 4
    FPS = 60.0

    CELL_SQ = 150
    CELL_HEIGHT = CELL_SQ
    CELL_WIDTH = CELL_SQ

    sq = 1200
    MINIMUM_WINDOW_SIZE = (sq, sq)

    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    DOWN = 'DOWN'
    UP = 'UP'
    TELEPORT = 'TELEPORT'

    STEPS = {
        LEFT: Point([-1, 0]),
        RIGHT: Point([1, 0]),
        DOWN: Point([0, 1]),
        UP: Point([0, -1]),
        TELEPORT: None
    }


