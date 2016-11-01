import asyncio

from logbook import Logger

from ..config import Config
from ..version import get_version


def start_loop(cfg: Config):
    logger = Logger("Heart")
    loop = asyncio.get_loop()

    logger.info("Initializing Oshino v{0}".format(get_version()))
