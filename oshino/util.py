import sys
import time

from datetime import datetime


def dynamic_import(path):
    module, builder = path.rsplit(".", 1)
    return getattr(__import__(module, fromlist=[builder]), builder)


def current_ts():
    """
    Just gives current timestamp.
    """
    utcnow = datetime.utcnow()
    return int(utcnow.timestamp() * 1000)


def timer():
    """
    Timer used for calculate time elapsed
    """
    if sys.platform == "win32":
        default_timer = time.clock
    else:
        default_timer = time.time

    return default_timer()
