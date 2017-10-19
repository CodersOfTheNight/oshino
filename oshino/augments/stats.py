from queue import Queue

from . import AugmentBase, consume


class MovingAverage(AugmentBase):

    def __init__(self, *args, **kwargs):
        super(MovingAverage, self).__init__(*args, **kwargs)
        self.q = Queue()

    @property
    def step(self):
        return self._data.get("step", 5)

    def activate(self, client, g):
        step = self.step

        stopped = False
        while not stopped:
            for i in range(0, step):
                try:
                    event = next(g)
                    self.q.put(event)
                except StopIteration:
                    stopped = True
                    break

            data = list(map(lambda x: x["metric_f"], consume(self.q)))
            if len(data) > 0:
                output = sum(data) / len(data)

                self.send_event(client,
                                service=self.prefix,
                                metric_f=output,
                                state="ok")
