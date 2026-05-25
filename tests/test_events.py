import pytest
from bat import Bat
from world import World
from events import RandomEvent, EVENT_INSECT_SWARM, EVENT_FALLING_ROCKS

def test_event_insect_swarm():
    bat = Bat("ACE", 0, 0, 0, 200)
    bat.echolocation = 100
    world = World(100, 60, 60)
    event = RandomEvent(EVENT_INSECT_SWARM)

    msgs = event.apply(bat, world)
    assert any("owad" in m.lower() or "insect" in m.lower() for m in msgs)
    assert bat.echolocation > 100

def test_event_falling_rocks():
    bat = Bat("ACE", 0, 0, 0, 200)
    world = World(100, 60, 60)
    event = RandomEvent(EVENT_FALLING_ROCKS)

    event.apply(bat, world)
    assert bat.echolocation < 200

def test_no_event():
    bat = Bat("ACE", 0, 0, 0, 200)
    world = World(100, 60, 60)
    event = RandomEvent(None)

    msgs = event.apply(bat, world)
    assert msgs == []
    assert bat.echolocation == 200
