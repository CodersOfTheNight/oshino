from pytest import mark, fixture
from logbook import Logger

from oshino.core import processor
from .fixtures import (mock_transport, mock_client, broken_transport, executor)

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
        mock_client.event(service="test")
        mock_client.event(service="test")
        mock_client.event(service="test")

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

        mock_client.on_stop()
        assert len(mock_client.events) == 1
        assert td < 0.5


    @mark.asyncio
    async def test_no_premature_exec(self, mock_client, event_loop):
        events_received = 0
        def stub_augment(client, g):
            nonlocal events_received

            for event in g:
                events_received += 1

        processor.register_augment(mock_client, "test", stub_augment, logger)
        mock_client.event(service="test", metric=1.0)

        mock_client.on_stop()

        assert events_received == 0
