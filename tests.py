import unittest
import math
from bat import Bat
from world import World, WorldElement, ELEMENT_STALAGMITE
from events import RandomEvent, EVENT_INSECT_SWARM, EVENT_FALLING_ROCKS

class TestBatSimulator(unittest.TestCase):

    def test_bat_initialization(self):
        bat = Bat("ACE", 0, 0, 45, 200)
        self.assertEqual(bat.name, "ACE")
        self.assertEqual(bat.x, 0.0)
        self.assertEqual(bat.y, 0.0)
        self.assertEqual(bat.angle, 45.0)
        self.assertEqual(bat.echolocation, 200.0)
        self.assertEqual(len(bat.path), 1)

    def test_bat_movement_math(self):
        bat = Bat("ACE", 0, 0, 0, 200)
        nx, ny = bat.compute_next_position(10)
        self.assertEqual(nx, 10.0)
        self.assertEqual(ny, 0.0)

        bat.turn(90)
        nx, ny = bat.compute_next_position(10)
        self.assertEqual(nx, 0.0)
        self.assertEqual(ny, 10.0)

    def test_bat_apply_position(self):
        bat = Bat("ACE", 0, 0, 0, 200)
        bat.apply_position(10, 20)
        self.assertEqual(bat.x, 10.0)
        self.assertEqual(bat.y, 20.0)
        self.assertEqual(len(bat.path), 2)
        self.assertEqual(bat.path[-1], (10.0, 20.0))

    def test_echolocation_consumption(self):
        bat = Bat("ACE", 0, 0, 0, 200)
        used = bat.consume_echolocation(50)
        self.assertEqual(used, 50.0)
        self.assertEqual(bat.echolocation, 150.0)

        used = bat.consume_echolocation(200)
        self.assertEqual(used, 150.0)
        self.assertEqual(bat.echolocation, 0.0)

    def test_echolocation_restoration(self):
        bat = Bat("ACE", 0, 0, 0, 200)
        bat.consume_echolocation(100)
        restored = bat.restore_echolocation(50)
        self.assertEqual(restored, 50.0)
        self.assertEqual(bat.echolocation, 150.0)

        restored = bat.restore_echolocation(100)
        self.assertEqual(restored, 50.0)
        self.assertEqual(bat.echolocation, 200.0)

    def test_world_bounds(self):
        world = World(limit=100, target_x=60, target_y=60)
        self.assertTrue(world.is_within_bounds(0, 0))
        self.assertTrue(world.is_within_bounds(100, 100))
        self.assertFalse(world.is_within_bounds(101, 0))
        self.assertFalse(world.is_within_bounds(0, -101))

    def test_world_clamping(self):
        world = World(limit=100, target_x=60, target_y=60)
        self.assertEqual(world.clamp_to_bounds(120, 50), (100.0, 50.0))
        self.assertEqual(world.clamp_to_bounds(-150, -200), (-100.0, -100.0))

    def test_target_reached(self):
        world = World(limit=100, target_x=60, target_y=60)
        self.assertTrue(world.target_reached(60, 60))
        self.assertTrue(world.target_reached(65, 65))
        self.assertFalse(world.target_reached(0, 0))

    def test_element_detection(self):
        world = World(limit=100, target_x=60, target_y=60, num_elements=0)
        el = WorldElement(ELEMENT_STALAGMITE, 10, 10, radius=5)
        world.elements.append(el)

        self.assertEqual(world.get_element_at(10, 10), el)
        self.assertEqual(world.get_element_at(12, 12), el)
        self.assertIsNone(world.get_element_at(20, 20))


    def test_event_insect_swarm(self):
        bat = Bat("ACE", 0, 0, 0, 200)
        bat.echolocation = 100
        world = World(100, 60, 60)
        event = RandomEvent(EVENT_INSECT_SWARM)

        msgs = event.apply(bat, world)
        self.assertTrue(any("owad" in m.lower() or "insect" in m.lower() for m in msgs))
        self.assertGreater(bat.echolocation, 100)

    def test_event_falling_rocks(self):
        bat = Bat("ACE", 0, 0, 0, 200)
        world = World(100, 60, 60)
        event = RandomEvent(EVENT_FALLING_ROCKS)

        event.apply(bat, world)
        self.assertLess(bat.echolocation, 200)

    def test_no_event(self):
        bat = Bat("ACE", 0, 0, 0, 200)
        world = World(100, 60, 60)
        event = RandomEvent(None)

        msgs = event.apply(bat, world)
        self.assertEqual(msgs, [])
        self.assertEqual(bat.echolocation, 200)

if __name__ == '__main__':
    unittest.main()
