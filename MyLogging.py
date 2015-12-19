import logging

logging.basicConfig(level=logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger = logging.getLogger("__GAME__")
logger.addHandler(ch)
