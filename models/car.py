from math import pi, cos, sin, sqrt, pow
from pygame import image, transform
from models.message import Message
import os
from car_controllers.deafult_controller import default_controller
from time import time

images_directory = os.path.dirname(os.path.abspath(__file__)) + "/../images/"


class Car:
    """
    Car representation. It has x and y position (as in a cartesian plane), an absolute speed and a direction. In case
    of movement, the total movement will be escalated into x and y with the direction.
    Also, the car has a fixed acceleration and maximum speed.
    """
    SECONDS = 1000.0  # TODO: should this be here?
    max_forward_speed = 20.0  # meters/10*seconds.
    acceleration_rate = 3.0  # meters/seconds*seconds.
    message = Message()

    def __init__(self, name, pos_x=0.0, pos_y=0.0, absolute_speed=0.0, direction=0, lane=1,
                 controller=default_controller, creation_time=None, left_intersection_time=None):
        """

        :param name: id to identify the car. Integer
        :param pos_x: x value of the car position.
        :param pos_y: y value of the car position.
        :param car_image: object that represents the rectangle of the car. Also image used to display in graphic
        environment.
        :param absolute_speed: absolute speed of the car.
        :param direction: direction of the car. Represented in degrees.
        :param lane: lane in which the car is travelling.
        :param direction: direction at which the front of the car is looking.
        :param controller: object which controls the speed of the car.
        """
        self.initial_speed = absolute_speed  # initial speed of the car when it appeared in the simulation.
        if creation_time is None:
            self.creation_time = time()
        else:
            self.creation_time = creation_time
        self.left_intersection_time = left_intersection_time
        self.controller = controller
        self.lane = lane
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.direction = direction
        self.absolute_speed = absolute_speed
        self.image = None
        self.rotated_image = None
        # self.rotated_image = transform.scale(self.rotated_image, (  # reduction of the size of the image
        #     int(self.rotated_image.get_rect().w * 0.1), int(self.rotated_image.get_rect().h * 0.1)))
        self.screen_car = None
        # self.screen_car.center = self.get_position()  # add the position to the rectangle
        self.follower_cars = []  # all the followers of the car will be here, so this car can send it information
        # to the others
        self.follow = False  # True if the car is following some other car

    def __str__(self):
        """
        String representation of the car. Adapted to output actual state of the car to a log file.
        Example: "Car: 48 Speed: 19.975 Following: 47" if car is following other car,
        Example: "Car: 48 Speed: 19.975" else.
        :return: String representation of the car.
        """
        if self.get_message() is not None:
            return '{"car_name":' + str(self.name) + ',"following":' + str(self.get_message().car_name) + ',"lane":' + \
                   str(self.lane) + ',"speed":' + str(self.initial_speed) + ',"creation_time":' + \
                   str(self.creation_time) + ',"left_intersection_time":' + str(self.left_intersection_time) + '}'
        return '{"car_name":' + str(self.name) + ',"lane":' + str(self.lane) + ',"speed":' + str(self.initial_speed) + \
               ',"creation_time":' + str(self.creation_time) + ',"left_intersection_time":' + \
               str(self.left_intersection_time) + '}'

    def move(self, quantity, time_unit):
        """
        Function to move a car. If its speed its 0, it'll not move. Time unit is necessary to work in milliseconds.
        Seconds = 1000.
        :param quantity: how many unit of times the car must move.
        :param time_unit: unit of time in which the car will move (seconds = 1000).
        :return: None
        """
        rad = self.direction * pi / 180
        self.pos_x += -sin(rad) * self.absolute_speed * quantity * time_unit / self.SECONDS
        self.pos_y += -cos(rad) * self.absolute_speed * quantity * time_unit / self.SECONDS

    def accelerate(self, quantity, time_unit):
        """
        Function to accelerate a car. Exception raised if maximum speed is reached or surpassed. Time unit is necessary
         to work in milliseconds. Seconds = 1000.
        :param quantity: how many unit of times the car must accelerate.
        :param time_unit: unit of ti- 5me in which the car will accelerate (seconds = 1000).
        :return: None
        """
        new_speed = self.absolute_speed + self.acceleration_rate * quantity * time_unit / self.SECONDS
        if new_speed > self.max_forward_speed:
            self.absolute_speed = self.max_forward_speed
        elif new_speed < 0:
            self.absolute_speed = 0
        else:
            self.absolute_speed = new_speed

    def get_position(self):
        """
        Returns the actual position of the car.
        :return: Position of the car
        """
        return self.pos_x, self.pos_y

    def set_position(self, position):
        """
        Set the position of the car.
        :param position: tuple with the position of the car. tuple must have the form (x, y)
        """
        self.pos_x = position[0]
        self.pos_y = position[1]

    def get_rect(self):
        """
        Returns the rectangle which represents the car.
        :return: rectangle of the car
        """
        return self.screen_car

    def get_speed(self):
        """
        returns the speed of the car.
        :return: absolute speed of the car.
        """
        return self.absolute_speed

    def get_direction(self):
        """
        Returns the direction of the car. It is in radians.
        :return: direction value of the car in radians.
        """
        return self.direction

    def set_speed(self, new_speed):
        """
        Sets the speed of the car. No restrictions exists.
        :param new_speed: new speed of the car.
        """
        self.absolute_speed = new_speed

    def set_controller(self, controller):
        """
        Set the controller of the car.
        :param controller: new controller of the car.
        :return:
        """
        self.controller = controller

    def draw_car(self):
        """
        Prepares the image of the car to be drawn. The image is rotated, re-escalated and moved.
        """
        self.rotated_image = transform.rotate(self.image, self.direction)
        self.rotated_image = transform.scale(self.rotated_image, (
            int(self.rotated_image.get_rect().w * 0.1), int(self.rotated_image.get_rect().h * 0.1)))
        self.screen_car = self.rotated_image.get_rect()
        self.screen_car.center = self.get_position()

    def update(self, speed_change, direction_change):
        """
        Updates the speed, position and images of the car. Receives inputs as if a user were playing with the car
        with the keyboards arrows.
        :param speed_change: amount to change the speed og the car
        :param direction_change: amount to change the direction
        """
        self.accelerate(1000.0/120.0*speed_change, 1)
        self.direction += direction_change
        self.move(1000.0/120.0, 50)
        self.send_message()
        self.draw_car()

    def cross_path(self, other_car):
        """
        Check if the path of one car crosses tih the path o f another. It is true if the other car is the same lane
        or if the other car is in one of the perpendicular lanes.
        :param other_car: other car information.
        :return: True if the paths does not crosses, False otherwise.
        """
        if self.lane == 1 and other_car.lane == 3 or self.lane == 3 and other_car.lane == 1:
            return False
        elif self.lane == 2 and other_car.lane == 4 or self.lane == 4 and other_car.lane == 2:
            return False
        else:
            return True

    def distance_to_center(self):
        """
        Returns the distance of the car to the perpendicular line to the center of the screen depending of the direction
         of the car. Only works if the car is perpendicular to one of those lines.
        :return: distance to the perpendicular line to the direction of the car at the center of the screen.
        """
        x = 1 if self.pos_x % 384 == 0 else 0
        y = 1 if self.pos_y % 384 == 0 else 0
        sign = cos(self.direction * pi / 180) * (self.pos_y - 384) / abs(self.pos_y - 384 + y) + sin(
            self.direction * pi / 180) * (self.pos_x - 384) / abs(self.pos_x - 384 + x)
        return sign*sqrt(pow(self.pos_x - 384,2) + pow(self.pos_y - 384, 2))

    def send_message(self):
        """
        Creates and send a message of the actual state of the car.
        """
        message = Message(self)
        for car in self.follower_cars:
            car.receive(message)

    def add_follower(self, car):
        """
        Adds a follower to the list of followers of the car.
        :param car: new follower car.
        """
        self.follower_cars.append(car)

    def receive(self, message):
        """
        Gets a new message and stores it in the message param. "Proxy" for set_message, actually.
        :param message: new message of following car.
        """
        self.set_message(message)

    def set_message(self, message):
        """
        Sets the message of the car.
        :param message: new message.
        """
        self.message = message

    def get_message(self):
        """
        Returns the actual stored message of the following car.
        :return: Stored message of following car.
        """
        return self.message

    def get_followers(self):
        """
        Returns all the car that are following this car.
        :return: followers of this car.
        """
        return self.follower_cars

    def stop_following(self):
        """
        Set the variable follow to False to indicate that this car isn't following other.
        """
        self.follow = False

    def start_following(self):
        """
        Sets the variable follow to True to indicate that this car has started following another car.
        """
        self.follow = True

    def get_name(self):
        """
        Returns the name which identifies the car.
        :return: name of the car.
        """
        return self.name

    def get_lane(self):
        """
        Return the lane in which the cart started
        :return: int of lane
        """
        return self.lane

    def to_json(self):
        """
        Returns a string representing a car in json format, for log use.
        :return: sting of json representation of a car.
        """
        return_string = '{'
        return_string += '"name":' + str(self.get_name()) + ','
        return_string += '"following":' + str(self.get_message().car_name) + ','
        return_string += '"lane":' + str(self.lane) + ','
        return_string += '"speed":' + str(self.get_speed()) + ','
        return_string += '"creation_time":' + str(self.creation_time) + ','
        return_string += '"left_intersection_time":' + str(self.left_intersection_time) \
            if self.left_intersection_time is not None else '"left_intersection_time":' + str(-1)
        return_string += '}'
        return return_string

    def set_left_intersection_time(self):
        """
        Set the left_intersection_time to this time. Time stored in seconds.
        """
        self.left_intersection_time = time()

    def set_creation_time(self, creation_time=None):
        """
        Sets the creation time of a car. Used for simulations with car list.
        :param creation_time: time of "creation" of the car. If none passed, time at which the function was called.
        """
        if creation_time is None:
            self.creation_time = time()
        else:
            self.creation_time = creation_time

    def new_image(self):
        """
        Creates the image representation of a car, with his rotated image and his screen representation (with the rect).
        """
        self.image = image.load(images_directory + "car.png")
        self.rotated_image = transform.rotate(self.image, self.direction)  # image of the car rotated
        self.rotated_image = transform.scale(self.rotated_image, (  # reduction of the size of the image
            int(self.rotated_image.get_rect().w * 0.1), int(self.rotated_image.get_rect().h * 0.1)))
        self.screen_car = self.rotated_image.get_rect()  # rectangle representation of the car
        self.screen_car.center = self.get_position()  # add the position to the rectangle

    def collide(self, list_of_cars):
        """
        Check if a car collides with any car of the list of cars.
        :param list_of_cars: cars to check if this car is colliding with.
        :return: True if a collision is detected, False otherwise,
        """
        for car in list_of_cars:
            if self.get_rect().colliderect(car.get_rect()):
                return True
        return False

    class ExceedCarMaximumSpeedError(Exception):
        pass

    class StopSpeedReached(Exception):
        pass

    class ExceedWheelTurningException(Exception):
        pass

    class ExceedTurningSpeedException(Exception):
        pass

    class CollideWithCarException(Exception):
        pass
