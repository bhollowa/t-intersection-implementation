import unittest

from models.direction import Direction, UnProperDirectionException
LEFT = 1
RIGHT = -1


class TestDirection(unittest.TestCase):

    def test_create_default_direction(self):
        default_direction = Direction()
        self.assertEqual(default_direction.x, 1)
        self.assertEqual(default_direction.y, 0)

    def test_create_direction(self):
        direction = Direction(0, 1)
        self.assertEqual(direction.x, 0)
        self.assertEqual(direction.y, 1)

    def test_create_bad_direction(self):
        self.assertRaises(UnProperDirectionException, Direction, 1, 1)

    def test_turn_left(self):
        direction = Direction()
        direction.turn(45, LEFT)
        self.assertAlmostEqual(direction.x, (2.0 ** (1.0 / 2) / 2))
        self.assertAlmostEqual(direction.y, (2.0 ** (1.0 / 2) / 2))
        direction.turn(45, LEFT)
        self.assertAlmostEqual(direction.x, 0)
        self.assertAlmostEqual(direction.y, 1)
