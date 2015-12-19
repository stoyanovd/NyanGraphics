from helpers.CommonInterface import GAME_CONF

class TimesConf:
    MULTIPLIER = 1

    TOTAL = 1.0
    BORDER_DELAY = 0.05

    BETWEEN_REPEATS_DT = (TOTAL - 2 * BORDER_DELAY) / (GAME_CONF.REPEATS_NUMBER - 1)
