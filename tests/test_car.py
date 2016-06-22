import unittest
from models.car import Car, ExceedCarMaximumSpeedError
from models.direction import Direction

SECONDS = 1000.0


class TestCar(unittest.TestCase):

    def setUp(self):
        self.car = Car()

    def test_create_car(self):

        self.assertEqual(self.car.pos_x, 0)
        self.assertEqual(self.car.pos_y, 0)
        self.assertEqual(self.car.absolute_speed, 0)
        self.assertEqual(self.car.direction, Direction())
        self.assertEqual(self.car.max_absolute_speed, 17)
        self.assertEqual(self.car.acceleration, 3)

        new_car = Car(50, 50, 17, Direction(0, -1))
        self.assertEqual(new_car.pos_x, 50)
        self.assertEqual(new_car.pos_y, 50)
        self.assertEqual(new_car.absolute_speed, 17)
        self.assertEqual(new_car.direction, Direction(0, -1))
        self.assertRaises(ExceedCarMaximumSpeedError, Car, 0, 0, 30)

    def test_move_car(self):

        self.car.move(5.0, SECONDS)
        self.assertEqual(self.car.pos_x, 0)
        self.assertEqual(self.car.pos_y, 0)

        new_car = Car(absolute_speed=17)
        new_car.move(5.0, SECONDS)
        self.assertEqual(new_car.pos_x, 85)
        self.assertEqual(new_car.pos_y, 0)

        new_car = Car(absolute_speed=10, direction=Direction(-1, 0))
        new_car.move(5.0, SECONDS)
        self.assertEqual(new_car.pos_x, -50)
        self.assertEqual(new_car.pos_y, 0)

        degrees = 2.0 ** (1.0 / 2) / 2.0
        new_car = Car(absolute_speed=10, direction=Direction(degrees, -degrees))
        new_car.move(5.0, SECONDS)
        new_pos = degrees * 5.0 * 10
        self.assertEqual(new_car.pos_x, new_pos)
        self.assertEqual(new_car.pos_y, -new_pos)

    def test_accelerate_car(self):

        self.car.accelerate(1.0, SECONDS)
        self.assertEqual(self.car.absolute_speed, 3)
        self.assertEqual(self.car.pos_x, 3.0 / 2.0)
        self.assertEqual(self.car.pos_y, 0)

        self.car.accelerate(1.0, SECONDS)
        self.assertEqual(self.car.absolute_speed, 6)
        self.assertEqual(self.car.pos_x, 6)
        self.assertEqual(self.car.pos_y, 0)

        degrees = 2.0 ** (1.0 / 2) / 2.0
        new_car = Car(direction=Direction(degrees, degrees))
        new_car.accelerate(5.0, SECONDS)
        self.assertEqual(new_car.absolute_speed, 15)
        self.assertEqual(new_car.pos_x, 75.0 / 2.0 * degrees)
        self.assertEqual(new_car.pos_y, 75.0 / 2.0 * degrees)

        new_car = Car(direction=Direction(-degrees, -degrees))
        new_car.accelerate(5.0, SECONDS)
        self.assertEqual(new_car.absolute_speed, 15)
        self.assertEqual(new_car.pos_x, - 75.0 / 2.0 * degrees)
        self.assertEqual(new_car.pos_y, - 75.0 / 2.0 * degrees)

        self.assertRaises(ExceedCarMaximumSpeedError, new_car.accelerate, 10, SECONDS)


if __name__ == '__main__':
    unittest.main()
