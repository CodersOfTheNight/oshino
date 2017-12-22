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
