import logging


def make_logger():
    level = logging.INFO

    logging.basicConfig(level=level)
    # ch = logging.StreamHandler()
    # ch.setLevel(level)

    logger = logging.getLogger("__GAME__")
    # logger.addHandler(ch)

    return logger
