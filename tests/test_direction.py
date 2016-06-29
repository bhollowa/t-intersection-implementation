import unittest

from models.direction import Direction, UnProperDirectionException, NotEqualAngleException
LEFT = 1
RIGHT = -1


class TestDirection(unittest.TestCase):
    def setUp(self):
        self.direction = Direction()

    def tearDown(self):
        self.direction = Direction()

    def test_create_direction(self):
        self.assertEqual(self.direction.x, 1)
        self.assertEqual(self.direction.y, 0)

        direction = Direction(0, 1, 90)
        self.assertEqual(direction.x, 0)
        self.assertEqual(direction.y, 1)
        self.assertEqual(direction.angle, 90)

        degrees = 2.0 ** (1.0 / 2) / 2.0
        direction = Direction(degrees, -degrees, -45)
        self.assertEqual(direction.x, degrees)
        self.assertEqual(direction.y, -degrees)

    def test_create_bad_direction(self):
        self.assertRaises(UnProperDirectionException, Direction, 1, 1, 90)
        self.assertRaises(NotEqualAngleException, Direction, 1, 0, 90)

    def test_turn_left(self):
        self.direction.turn(45, LEFT)
        self.assertAlmostEqual(self.direction.x, (2.0 ** (1.0 / 2) / 2))
        self.assertAlmostEqual(self.direction.y, (2.0 ** (1.0 / 2) / 2))
        self.assertEqual(self.direction.angle, 45)
        self.direction.turn(45, LEFT)
        self.assertAlmostEqual(self.direction.x, 0)
        self.assertAlmostEqual(self.direction.y, 1)
        self.assertEqual(self.direction.angle, 90)

        direction = Direction()
        direction.turn(90, LEFT)
        self.assertAlmostEqual(direction.x, 0)
        self.assertAlmostEqual(direction.y, 1)
        self.assertEqual(direction.angle, 90)
        direction.turn(90, LEFT)
        self.assertAlmostEqual(direction.x, -1)
        self.assertAlmostEqual(direction.y, 0)
        self.assertEqual(direction.angle, 180)

    def test_turn_right(self):
        self.direction.turn(45, RIGHT)
        self.assertAlmostEqual(self.direction.x, (2.0 ** (1.0 / 2) / 2))
        self.assertAlmostEqual(self.direction.y, -(2.0 ** (1.0 / 2) / 2))
        self.assertEqual(self.direction.angle, -45 % 360)
        self.direction.turn(45, RIGHT)
        self.assertAlmostEqual(self.direction.x, 0)
        self.assertAlmostEqual(self.direction.y, -1)
        self.assertEqual(self.direction.angle, -90 % 360)

    def test_equal_directions(self):
        direction = Direction()
        self.assertEqual(direction, Direction())
