import pytest
from world import World, WorldElement, ELEMENT_STALAGMITE

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
