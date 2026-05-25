import pytest
import math
from bat import Bat
from world import World, WorldElement, ELEMENT_STALAGMITE
from events import RandomEvent, EVENT_INSECT_SWARM, EVENT_FALLING_ROCKS

# ──────────────────────────────────────────────────────────────── Bat Tests

def test_bat_initialization():
    bat = Bat("ACE", 0, 0, 45, 200)
    assert bat.name == "ACE"
    assert bat.x == 0.0
    assert bat.y == 0.0
    assert bat.angle == 45.0
    assert bat.echolocation == 200.0
    assert len(bat.path) == 1

def test_bat_movement_math():
    bat = Bat("ACE", 0, 0, 0, 200) # Facing East
    nx, ny = bat.compute_next_position(10)
    assert nx == 10.0
    assert ny == 0.0

    bat.turn(90) # Now North
    nx, ny = bat.compute_next_position(10)
    assert nx == 0.0
    assert ny == 10.0

def test_bat_apply_position():
    bat = Bat("ACE", 0, 0, 0, 200)
    bat.apply_position(10, 20)
    assert bat.x == 10.0
    assert bat.y == 20.0
    assert len(bat.path) == 2
    assert bat.path[-1] == (10.0, 20.0)

def test_echolocation_consumption():
    bat = Bat("ACE", 0, 0, 0, 200)
    used = bat.consume_echolocation(50)
    assert used == 50.0
    assert bat.echolocation == 150.0

    used = bat.consume_echolocation(200) # More than available
    assert used == 150.0
    assert bat.echolocation == 0.0

def test_echolocation_restoration():
    bat = Bat("ACE", 0, 0, 0, 200)
    bat.consume_echolocation(100)
    restored = bat.restore_echolocation(50)
    assert restored == 50.0
    assert bat.echolocation == 150.0

    restored = bat.restore_echolocation(100) # Over max
    assert restored == 50.0
    assert bat.echolocation == 200.0

# ────────────────────────────────────────────────────────────── World Tests

def test_world_bounds():
    world = World(limit=100, target_x=60, target_y=60)
    assert world.is_within_bounds(0, 0) is True
    assert world.is_within_bounds(100, 100) is True
    assert world.is_within_bounds(101, 0) is False
    assert world.is_within_bounds(0, -101) is False

def test_world_clamping():
    world = World(limit=100, target_x=60, target_y=60)
    assert world.clamp_to_bounds(120, 50) == (100.0, 50.0)
    assert world.clamp_to_bounds(-150, -200) == (-100.0, -100.0)

def test_target_reached():
    world = World(limit=100, target_x=60, target_y=60)
    assert world.target_reached(60, 60) is True
    assert world.target_reached(65, 65) is True # within tolerance
    assert world.target_reached(0, 0) is False

def test_element_detection():
    world = World(limit=100, target_x=60, target_y=60, num_elements=0)
    el = WorldElement(ELEMENT_STALAGMITE, 10, 10, radius=5)
    world.elements.append(el)

    assert world.get_element_at(10, 10) == el
    assert world.get_element_at(12, 12) == el
    assert world.get_element_at(20, 20) is None

# ───────────────────────────────────────────────────────────── Event Tests

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
