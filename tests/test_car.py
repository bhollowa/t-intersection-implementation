import unittest

from models.car import Car


class TestCar(unittest.TestCase):

    def setUp(self):
        self.car = Car()

    def tearDown(self):
        self.car.reset()

    def test_create_car(self):
        self.assertEqual(self.car.pos_x, 0)
        self.assertEqual(self.car.pos_y, 0)
        self.assertEqual(self.car.speed, 0)
        self.assertEqual(self.car.max_speed, 17)
        self.assertEqual(self.car.acceleration, 3)

    def test_accelerate_car_x_seconds(self):
        self.assertEqual(self.car.accelerate_x_seconds(2), 6)
        self.assertEqual(self.car.pos_x, 6)
        self.assertEqual(self.car.pos_y, 0)
        self.assertEqual(self.car.speed, 6)

    def test_accelerate_car_y_seconds(self):
        self.assertEqual(self.car.accelerate_y_seconds(2), 6)
        self.assertEqual(self.car.pos_y, 6)
        self.assertEqual(self.car.pos_x, 0)
        self.assertEqual(self.car.speed, 6)

    def test_accelerate_car_x_meters(self):
        self.assertEqual(self.car.accelerate_x_meters(6), 2)
        self.assertEqual(self.car.pos_x, 6)
        self.assertEqual(self.car.pos_y, 0)
        self.assertEqual(self.car.speed, 6)
        self.car.reset()
        self.assertAlmostEqual(self.car.accelerate_x_meters(100), 8.16, 2)
        self.assertEqual(self.car.pos_x, 100)
        self.assertEqual(self.car.pos_y, 0)
        self.assertAlmostEqual(self.car.speed, 24.49, 2)


if __name__ == '__main__':
    unittest.main()
