def dynamic_import(path):
    module, builder = path.rsplit(".", 1)
    return getattr(__import__(module, fromlist=[builder]), builder)
