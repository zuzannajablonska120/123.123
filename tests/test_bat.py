import pytest
import math
from bat import Bat

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
