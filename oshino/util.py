from time import time


def dynamic_import(path):
    module, builder = path.rsplit(".", 1)
    return getattr(__import__(module, fromlist=[builder]), builder)


def current_ts():
    """
    Just gives current timestamp.
    """
    return int(time() * 1000)
