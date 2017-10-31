from pytest import mark, raises
from logbook import Logger

from oshino.core import processor
from oshino.augments import InvalidAugment
from oshino.config import AugmentConfig
from .fixtures import (mock_client,
                       broken_transport,
                       executor,
                       moving_avg)

logger = Logger(__name__)


class TestAugment(object):

    @mark.asyncio
    async def test_simple_augment(self, mock_client, executor, event_loop):
        events_received = 0
     
        def stub_augment(client, g):
            nonlocal events_received

            print("Waiting for events")
            for event in g:
                print("Got event: {0}".format(event))
                events_received += 1

        processor.register_augment(mock_client, "test", stub_augment, logger)
        mock_client.event(service="test", tags=["test"])
        mock_client.event(service="test", tags=["test"])
        mock_client.event(service="test", tags=["test"])

        mock_client.on_stop()

        assert events_received == 3

    @mark.asyncio
    async def test_window_n_3(self, mock_client, event_loop):
        def stub_augment(client, g):
            acc = 0

            while True:
                try:
                    for i in range(0, 3):
                        event = next(g)
                        print("Got event")
                        acc += event["metric"]
                    client.event(service="accumulated", metric=acc)
                    acc = 0
                except StopIteration:
                    break

        processor.register_augment(mock_client, "test", stub_augment, logger)

        for i in range(0, 10):
            mock_client.event(service="test", metric=i*10)


        mock_client.on_stop()

        print(mock_client.events)

        # 10 events pushed, every 3 extra event added (10/3 = 3)
        assert len(mock_client.events) == 13


        filtered = list(filter(lambda x: x["service"] == "accumulated",
                               mock_client.events))

        assert len(filtered) == 3
        # 30, 120, 210
        assert sum([event["metric"] for event in filtered]) == 360

    @mark.asyncio
    @mark.slow
    async def test_lagging_augment(self, mock_client, event_loop):
        from time import time, sleep
        
        def stub_augment(client, g):
            for event in g:
                print("Got event")
                ts = time()
                print("Doing Long sleep")
                sleep(10)
                te = time()
                print("Done sleeping: {0}".format(te - ts))

        processor.register_augment(mock_client, "test", stub_augment, logger)
        ts = time()
        mock_client.event(service="test")
        te = time()
        td = te - ts

        assert len(mock_client.events) == 1
        assert td < 0.5

    def test_invalid_augment(self):
        aug = InvalidAugment({})
        assert not aug.is_valid()

    def test_invalid_augment_from_config(self):
        cfg = AugmentConfig({"module": "oshino.augments.InvalidAugment"})
        assert not cfg.is_valid()

    def test_invalid_augment_raise_exception(self):
        cfg = AugmentConfig({"module": "oshino.augments.InvalidAugment"})
        with raises(RuntimeError):
            cfg.instance.activate(None, None)


class TestStatsAugments(object):

    @mark.asyncio
    async def test_moving_average(self, mock_client, moving_avg, event_loop):
        processor.register_augment(mock_client,
                                   moving_avg.key,
                                   moving_avg.activate,
                                   logger)

        print("Key: {0}".format(moving_avg.key))
        for i in range(9):
            mock_client.event(service=moving_avg.key, metric_f=i**2)

        mock_client.on_stop()
        assert len(mock_client.events) == 16

        print(mock_client.events)

        filtered = filter(lambda x: x["service"] == "test_moving_avg.value",
                          mock_client.events)

        assert len(list(filtered)) == 7
