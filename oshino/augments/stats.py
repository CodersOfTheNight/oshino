from . import AugmentBase


class MovingAverage(AugmentBase):

    @property
    def step(self):
        self._data.get("step", 5)

    def activate(self, client, g):
        pass
