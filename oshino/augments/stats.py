from collections import deque

from . import AugmentBase


class SimpleMovingAverage(AugmentBase):

    def __init__(self, *args, **kwargs):
        super(SimpleMovingAverage, self).__init__(*args, **kwargs)
        self.dq = deque(maxlen=self.step)

    @property
    def step(self):
        return self._data.get("step", 5)

    def activate(self, client, g):
        step = self.step

        stopped = False
        while not stopped:

            try:
                event = next(g)
                self.dq.append(event)
            except StopIteration:
                stopped = True
                break

            data = list(map(lambda x: x["metric_f"], list(self.dq)))
            if len(data) == step:
                output = sum(data) / len(data)

                self.send_event(client,
                                service=self.prefix + "value",
                                metric_f=output,
                                state="ok")
