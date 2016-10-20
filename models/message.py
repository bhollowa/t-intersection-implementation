from math import pi, cos, sin, sqrt, pow
from time import time


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
            self.actual_coordinates = car.get_actual_coordinates()
            self.origin_coordinates = car.get_origin_coordinates()
            self.acceleration = car.get_acceleration()
            self.speed = car.get_speed()
            self.car_name = car.get_name()
            self.lane = car.get_lane()
            self.creation_time = car.get_creation_time()
            self.new = car.is_new()
        else:
            self.actual_coordinates = (384, 384, 0, 1)
            self.origin_coordinates = (384, 384, 0, 1)
            self.acceleration = 3
            self.car_name = -1
            self.speed = 10
            self.creation_time = time()
            self.new = True
        self.receiver = None
        self.type = "info"
        self.follower = None
        self.car = None
        self.follow = False

    def virtual_distance(self):
        """
        Gets the virtual position of the car.
        :return: <int> virtual position of the car
        """
        x_distance = (self.get_origin_x_position() - self.get_x_position()) * sin(self.get_direction() * pi / 180)
        y_distance = (self.get_origin_y_position() - self.get_y_position()) * cos(self.get_direction() * pi / 180)
        return x_distance + y_distance

    def distance_to_center(self):
        """
        Returns the distance of the car who created the message to the perpendicular line to the center of the screen
        depending of the direction of the car. Only works if the car is perpendicular to one of those lines.
        :return: distance to the perpendicular line to the direction of the car who created the message at the center of
         the screen.
        """
        x = 1 if self.get_x_position() % 384 == 0 else 0
        y = 1 if self.get_y_position() % 384 == 0 else 0
        sign = cos(self.get_direction() * pi / 180) * (self.get_y_position() - 384) / abs(
            self.get_y_position() - 384 + y) + sin(self.get_direction() * pi / 180) * (
        self.get_x_position() - 384) / abs(self.get_x_position() - 384 + x)
        return sign*sqrt(pow(self.get_x_position() - 384,2) + pow(self.get_y_position() - 384, 2))

    def is_new(self):
        """
        Check if the car that created this message is new at the intersection. a car is new at an intersection if it
        hasn't been analyzed by a supervisory level.
        :return: True if the car is new at the intersection. False otherwise.
        """
        return self.new

    def cross_path(self, other_car_message):
        """
        Check if the path of one car crosses tih the path o f another. It is true if the other car is the same lane
        or if the other car is in one of the perpendicular lanes.
        :param other_car_message: information of the other car in a message.
        :return: True if the paths does not crosses, False otherwise.
        """
        if self.lane == 1 and other_car_message.lane == 3 or self.lane == 3 and other_car_message.lane == 1:
            return False
        elif self.lane == 2 and other_car_message.lane == 4 or self.lane == 4 and other_car_message.lane == 2:
            return False
        else:
            return True

    def set_receiver(self, receiver):
        """
        Sets the receiver of the message.
        """
        self.receiver = receiver

    def get_receiver(self):
        """
        Gets the receiver of this message.
        :return: The receiver of the message.
        """
        return self.receiver

    def get_type(self):
        """
        Returns the type of the message
        :return: <string> Message type
        """
        return self.type

    def set_type(self, message_type):
        """
        Sets the type of the message
        :param message_type: <string> type of the mesage
        """
        self.type = message_type

    def get_car_name(self):
        """
        Gets the name which identifies the car.
        :return: Name of the car
        """
        return self.car_name

    def get_follower(self):
        """
        Return the follower
        :return: follower
        """
        return self.follower

    def set_follower(self, follower):
        """
        Sets the follower variable
        :param follower: follower name
        """
        self.follower = follower

    def set_car(self, car):
        """
        Sets the car so it can be used at the supervisory level.
        :param car: reference of the car.
        """
        self.car = car

    def get_car(self):
        """
        Returns the car variable.
        :return: car variable
        """
        return self.car

    def set_follow(self, follow):
        self.follow = follow

    def get_follow(self):
        return self.follow

    def get_origin_x_position(self):
        """
        Get the origin x position of the car who created this message
        :return:  <int> x position.
        """
        return self.origin_coordinates[0]

    def get_origin_y_position(self):
        """
        Get the origin y position of the car who created this message
        :return:  <int> y position.
        """
        return self.origin_coordinates[1]

    def get_x_position(self):
        """
        Get the x position of the car who created this message
        :return:  <int> x position.
        """
        return self.actual_coordinates[0]

    def get_y_position(self):
        """
        Get the y position of the car who created this message
        :return:  <int> y position.
        """
        return self.actual_coordinates[1]

    def get_direction(self):
        """
        Get the direction position of the car who created this message
        :return:  <int> direction position.
        """
        return self.actual_coordinates[2]

    def get_acceleration(self):
        """
        Get the acceleration of the car that created this message
        :return: <int> Acceleration of the car
        """
        return self.acceleration
