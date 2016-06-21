import unittest
from models.car import Car
from models.direction import Direction


class TestCar(unittest.TestCase):

    def setUp(self):
        self.car = Car()

    def test_create_default_car(self):
        self.assertEqual(self.car.pos_x, 0)
        self.assertEqual(self.car.pos_y, 0)
        self.assertEqual(self.car.absolute_speed, 0)
        self.assertEqual(self.car.direction, Direction())
        self.assertEqual(self.car.max_speed, 17)
        self.assertEqual(self.car.acceleration, 3)

if __name__ == '__main__':
    unittest.main()
