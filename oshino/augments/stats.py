from queue import Queue

from . import AugmentBase, consume


class MovingAverage(AugmentBase):

    def __init__(self, *args, **kwargs):
        super(MovingAverage, self).__init__(*args, **kwargs)
        self.q = Queue()

    @property
    def step(self):
        self._data.get("step", 5)

    def activate(self, client, g):
        step = self.step

        while True:
            for i in range(0, step):
                for event in g:
                    self.q.put(event)

            data = list(map(lambda x: x.metric_f, consume(self.q)))
            output = sum(data) / len(data)

            self.send_event(service=self.prefix,
                            metric_f=output,
                            state="ok")
