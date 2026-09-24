from sparks.core.events.bus import EventBus


def test_event_is_published():
    bus = EventBus()

    received = []

    def handler(data):
        received.append(data)

    bus.subscribe("test.event", handler)
    bus.publish("test.event", {"message": "hello"})

    assert received == [{"message": "hello"}]


def test_unsubscribe():
    bus = EventBus()

    received = []

    def handler(data):
        received.append(data)

    bus.subscribe("test.event", handler)
    bus.unsubscribe("test.event", handler)

    bus.publish("test.event", "hello")

    assert received == []