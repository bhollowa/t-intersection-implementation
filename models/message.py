from math import pi, cos, sin, sqrt, pow


class Message:
    """
    Message object that can be created from a car. If no car is given, the message will have an "invalid" car name
    (a negative one).
    The message can give the distance to the center of the car from it was created (based on the information given).
    """
    def __init__(self, car=None):
        """
        Constructor of a message. The car can be given to use its information.
        :param car: car to create the message from.
        """
        if car is not None:
            self.pos_x, self.pos_y = car.get_position()
            self.direction = car.get_direction()
            self.speed = car.get_speed()
            self.car_name = car.get_name()
        else:
            self.car_name = -1
            self.pos_x = 384
            self.pos_y = 384
            self.direction = 0
            self.speed = 10

    def distance_to_center(self):
        """
        Returns the distance of the car who created the message to the perpendicular line to the center of the screen
        depending of the direction of the car. Only works if the car is perpendicular to one of those lines.
        :return: distance to the perpendicular line to the direction of the car who created the message at the center of
         the screen.
        """
        x = 1 if self.pos_x % 384 == 0 else 0
        y = 1 if self.pos_y % 384 == 0 else 0
        sign = cos(self.direction * pi / 180)*(self.pos_y - 384)/abs(self.pos_y - 384 + y) + sin(self.direction * pi / 180)*(self.pos_x - 384)/abs(self.pos_x - 384 + x)
        return sign*sqrt(pow(self.pos_x - 384,2) + pow(self.pos_y - 384, 2))