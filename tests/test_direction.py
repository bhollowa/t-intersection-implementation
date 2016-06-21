import unittest

from models.direction import Direction, UnProperDirectionException
LEFT = 1
RIGHT = -1


class TestDirection(unittest.TestCase):
    def setUp(self):
        self.direction = Direction()

    def tearDown(self):
        self.direction = Direction()

    def test_create_default_direction(self):
        self.assertEqual(self.direction.x, 1)
        self.assertEqual(self.direction.y, 0)

    def test_create_direction(self):
        direction = Direction(0, 1)
        self.assertEqual(direction.x, 0)
        self.assertEqual(direction.y, 1)

    def test_create_bad_direction(self):
        self.assertRaises(UnProperDirectionException, Direction, 1, 1)

    def test_turn_left(self):
        self.direction.turn(45, LEFT)
        self.assertAlmostEqual(self.direction.x, (2.0 ** (1.0 / 2) / 2))
        self.assertAlmostEqual(self.direction.y, (2.0 ** (1.0 / 2) / 2))
        self.direction.turn(45, LEFT)
        self.assertAlmostEqual(self.direction.x, 0)
        self.assertAlmostEqual(self.direction.y, 1)

    def test_turn_right(self):
        self.direction.turn(45, RIGHT)
        self.assertAlmostEqual(self.direction.x, (2.0 ** (1.0 / 2) / 2))
        self.assertAlmostEqual(self.direction.y, -(2.0 ** (1.0 / 2) / 2))
        self.direction.turn(45, RIGHT)
        self.assertAlmostEqual(self.direction.x, 0)
        self.assertAlmostEqual(self.direction.y, -1)

    def test_equal_directions(self):
        direction = Direction()
        self.assertEqual(direction, Direction())
