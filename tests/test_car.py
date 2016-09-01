import unittest
from models.car import Car
from models.direction import Direction


class TestCar(unittest.TestCase):

    def setUp(self):
        self.car = Car()
        self.degrees = 2.0 ** (1.0 / 2) / 2.0

    def test_create_car(self):

        self.assertEqual(self.car.pos_x, 0)
        self.assertEqual(self.car.pos_y, 0)
        self.assertEqual(self.car.absolute_speed, 0)
        self.assertEqual(self.car.direction, Direction())
        self.assertEqual(self.car.max_absolute_speed, 120.0)
        self.assertEqual(self.car.acceleration_rate, 3)

        new_car = Car(50, 50, 17, Direction(0, -1))
        self.assertEqual(new_car.pos_x, 50)
        self.assertEqual(new_car.pos_y, 50)
        self.assertEqual(new_car.absolute_speed, 17)
        self.assertEqual(new_car.direction, Direction(0, -1))
        self.assertRaises(Car.ExceedCarMaximumSpeedError, Car, 0, 0, 121)

    def test_move_car(self):

        self.car.move(5.0, self.car.SECONDS)
        self.assertEqual(self.car.pos_x, 0)
        self.assertEqual(self.car.pos_y, 0)

        new_car = Car(absolute_speed=17)
        new_car.move(5.0, new_car.SECONDS)
        self.assertEqual(new_car.pos_x, 85)
        self.assertEqual(new_car.pos_y, 0)

        new_car = Car(absolute_speed=10, direction=Direction(-1, 0))
        new_car.move(5.0, new_car.SECONDS)
        self.assertEqual(new_car.pos_x, -50)
        self.assertEqual(new_car.pos_y, 0)

        new_car = Car(absolute_speed=10, direction=Direction(self.degrees, -self.degrees, -45))
        new_car.move(5.0, new_car.SECONDS)
        new_pos = self.degrees * 5.0 * 10
        self.assertEqual(new_car.pos_x, new_pos)
        self.assertEqual(new_car.pos_y, -new_pos)

    def test_accelerate_car(self):

        self.car.accelerate(1.0, self.car.SECONDS)
        self.assertEqual(self.car.absolute_speed, 3)
        self.assertEqual(self.car.pos_x, 3.0 / 2.0)
        self.assertEqual(self.car.pos_y, 0)

        self.car.accelerate(1.0, self.car.SECONDS)
        self.assertEqual(self.car.absolute_speed, 6)
        self.assertEqual(self.car.pos_x, 6)
        self.assertEqual(self.car.pos_y, 0)

        new_car = Car(direction=Direction(self.degrees, self.degrees, 45))
        new_car.accelerate(5.0, new_car.SECONDS)
        self.assertEqual(new_car.absolute_speed, 15)
        self.assertEqual(new_car.pos_x, 75.0 / 2.0 * self.degrees)
        self.assertEqual(new_car.pos_y, 75.0 / 2.0 * self.degrees)

        new_car = Car(direction=Direction(-self.degrees, -self.degrees, 225))
        new_car.accelerate(5.0, new_car.SECONDS)
        self.assertEqual(new_car.absolute_speed, 15)
        self.assertEqual(new_car.pos_x, - 75.0 / 2.0 * self.degrees)
        self.assertEqual(new_car.pos_y, - 75.0 / 2.0 * self.degrees)

        self.assertRaises(Car.ExceedCarMaximumSpeedError, new_car.accelerate, 40, new_car.SECONDS)

    def test_decelerate_car(self):

        self.assertRaises(Car.StopSpeedReached, self.car.brake_decelerate, 1, self.car.SECONDS)

        new_car = Car(absolute_speed=30)
        new_car.brake_decelerate(1, new_car.SECONDS)
        self.assertEqual(new_car.absolute_speed, 26)
        self.assertEqual(new_car.pos_x, 28)
        self.assertEqual(new_car.pos_y, 0)

        new_car.brake_decelerate(5, new_car.SECONDS)
        self.assertEqual(new_car.absolute_speed, 6)
        self.assertEqual(new_car.pos_x, 108)
        self.assertEqual(new_car.pos_y, 0)

        new_car = Car(direction=Direction(-self.degrees, -self.degrees, 225), absolute_speed=30)
        new_car.brake_decelerate(7, new_car.SECONDS)
        self.assertEqual(new_car.absolute_speed, 2)
        self.assertEqual(new_car.pos_x, - 112.0 * self.degrees)
        self.assertEqual(new_car.pos_y, - 112.0 * self.degrees)

    def test_start_go_stop(self):

        self.car.accelerate(4, self.car.SECONDS)
        self.car.move(10, self.car.SECONDS)
        self.car.brake_decelerate(3, self.car.SECONDS)
        self.assertEqual(self.car.absolute_speed, 0)
        self.assertEqual(self.car.pos_x, 162)
        self.assertEqual(self.car.pos_y, 0)

    def test_turn_car(self):

        self.car.turn(1, self.car.SECONDS, 45)
        self.assertEqual(self.car.absolute_speed, 0)
        self.assertEqual(self.car.direction, Direction())
        self.assertEqual(self.car.pos_x, 0)
        self.assertEqual(self.car.pos_y, 0)

        self.car.accelerate(5, self.car.SECONDS)
        self.assertRaises(Car.ExceedWheelTurningException, self.car.turn, 5, self.car.SECONDS, 90)
        self.assertRaises(Car.ExceedTurningSpeedException, self.car.turn, 5, self.car.SECONDS, 45)

        new_car = Car(absolute_speed=10)
        new_car.turn(0.627, self.car.SECONDS, 45)
        self.assertAlmostEqual(new_car.pos_x, 4, 1)
        self.assertAlmostEqual(new_car.pos_y, 4, 1)
        self.assertAlmostEqual(new_car.direction.x, 0, 1)
        self.assertAlmostEqual(new_car.direction.y, 1, 1)

        new_car.turn(0.627, self.car.SECONDS, 45)
        self.assertAlmostEqual(new_car.pos_x, 0, 1)
        self.assertAlmostEqual(new_car.pos_y, 8, 1)
        self.assertAlmostEqual(new_car.direction.x, -1, 1)
        self.assertAlmostEqual(new_car.direction.y, 0, 1)

        new_car.turn(0.627, self.car.SECONDS, 45)
        self.assertAlmostEqual(new_car.pos_x, -4, 1)
        self.assertAlmostEqual(new_car.pos_y, 4, 1)
        self.assertAlmostEqual(new_car.direction.x, 0, 1)
        self.assertAlmostEqual(new_car.direction.y, -1, 1)

        new_car.turn(0.627, self.car.SECONDS, 45)
        self.assertAlmostEqual(new_car.pos_x, 0, 1)
        self.assertAlmostEqual(new_car.pos_y, 0, 1)
        self.assertAlmostEqual(new_car.direction.x, 1, 1)
        self.assertAlmostEqual(new_car.direction.y, 0, 1)

        new_car = Car(absolute_speed=10, direction=Direction(0, 1, 90))
        new_car.turn(0.627, self.car.SECONDS, 45)
        self.assertAlmostEqual(new_car.pos_x, -4, 1)
        self.assertAlmostEqual(new_car.pos_y, 4, 1)
        self.assertAlmostEqual(new_car.direction.x, -1, 1)
        self.assertAlmostEqual(new_car.direction.y, 0, 1)

        new_car.turn(0.627, self.car.SECONDS, 45)
        self.assertAlmostEqual(new_car.pos_x, -8, 1)
        self.assertAlmostEqual(new_car.pos_y, 0, 1)
        self.assertAlmostEqual(new_car.direction.x, 0, 1)
        self.assertAlmostEqual(new_car.direction.y, -1, 1)

        new_car.turn(0.627, self.car.SECONDS, 45)
        self.assertAlmostEqual(new_car.pos_x, -4, 1)
        self.assertAlmostEqual(new_car.pos_y, -4, 1)
        self.assertAlmostEqual(new_car.direction.x, 1, 1)
        self.assertAlmostEqual(new_car.direction.y, 0, 1)

        new_car.turn(0.627, self.car.SECONDS, 45)
        self.assertAlmostEqual(new_car.pos_x, 0, 1)
        self.assertAlmostEqual(new_car.pos_y, 0, 1)
        self.assertAlmostEqual(new_car.direction.x, 0, 1)
        self.assertAlmostEqual(new_car.direction.y, 1, 1)

if __name__ == '__main__':
    unittest.main()
