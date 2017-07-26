import os

from logbook import Logger


def run(host, port, qin, qout):
    logger = Logger("Admin")
    logger.info("Starting admin panel on: {0}:{1}, PID: {2}"
                .format(host,
                        port,
                        os.getpid()))
