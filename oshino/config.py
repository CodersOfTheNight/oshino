import os
import yaml

from jinja2 import Template


class Config(object):

    """
    Config object
    """

    def __init__(self, cfg):
        self._data = cfg


def load(config_file):
    """
    Processes and loads config file.
    """
    with open(config_file, "r") as f:

        def env_get():
            return dict(os.environ)
        tmpl = Template(f.read())
        return Config(yaml.load(tmpl.render(**env_get())))
