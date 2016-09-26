from math import pi, cos, sin, sqrt, pow
from pygame import image, transform
from models.message import Message
import os

images_directory = os.getcwd() + "/images/"


class Car:
    """
    Car representation. It has x and y position (as in a cartesian plane), an absolute speed and a direction. In case
    of movement, the total movement will be escalated into x and y with the direction.
    Also, the car has a fixed acceleration and maximum speed.
    """
    SECONDS = 1000.0  # TODO: should this be here?
    max_forward_speed = 20.0  # meters/10*seconds.
    max_backward_speed = -20.0  # meters/10*seconds.
    acceleration_rate = 3.0  # meters/seconds*seconds.
    brake_deceleration_rate = 4  # meters/seconds*seconds.
    max_turning_speed = 14.0  # meters/seconds.
    maximum_turning_degrees = 45  # degrees.
    length = 4  # meters
    message = None

    def __init__(self, name, pos_x=0.0, pos_y=0.0, car_image=image.load(images_directory + "car.png"),
                 absolute_speed=0.0, direction=0, lane=1):
        """
        Initializer of a car. It can be placed anywhere looking in any direction with any speed under the car maximum
        speed.
        :param pos_x: x value of the car position.
        :param pos_y: y value of the car position.
        :param absolute_speed: absolute speed of the car.
        :param direction: direction at which the front of the car is looking.
        """
        self.initial_speed = absolute_speed
        self.controller = None
        self.lane = lane
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = car_image
        self.direction = direction
        self.rotated_image = transform.rotate(car_image, self.direction)
        self.rotated_image = transform.scale(self.rotated_image, (
            int(self.rotated_image.get_rect().w * 0.1), int(self.rotated_image.get_rect().h * 0.1)))
        self.screen_car = self.rotated_image.get_rect()
        self.screen_car.center = self.get_position()
        self.absolute_speed = absolute_speed
        self.follower_cars = []
        self.follow = False

    def __str__(self):
        if self.get_message() is not None:
            return "Auto " + self.name + " a " + str(
                self.absolute_speed) + " velocidad siguiendo a " + self.get_message().car_name
        return "Auto " + self.name + " a " + str(self.absolute_speed) + " velocidad"

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
        self.pos_x = position[0]
        self.pos_y = position[1]

    def get_rect(self):
        return self.screen_car

    def get_speed(self):
        return self.absolute_speed

    def get_direction(self):
        return self.direction

    def set_speed(self, new_speed):
        self.absolute_speed = new_speed

    def set_controller(self, controller):
        self.controller = controller

    def draw_car(self):
        self.rotated_image = transform.rotate(self.image, self.direction)
        self.rotated_image = transform.scale(self.rotated_image, (
            int(self.rotated_image.get_rect().w * 0.1), int(self.rotated_image.get_rect().h * 0.1)))
        self.screen_car = self.rotated_image.get_rect()
        self.screen_car.center = self.get_position()

    def update(self, right, left, up, down):
        self.accelerate(1000.0/120.0*(up+down), 1)
        self.direction += (right + left)
        self.move(1000.0/120.0, 50)
        self.send_message()
        self.draw_car()

    def cross_path(self, other_car):
        if self.lane == 1 and other_car.lane == 3 or self.lane == 3 and other_car.lane == 1:
            return False
        elif self.lane == 2 and other_car.lane == 4 or self.lane == 4 and other_car.lane == 2:
            return False
        else:
            return True

    def distance_to_center(self):
        x = 1 if self.pos_x % 384 == 0 else 0
        y = 1 if self.pos_y % 384 == 0 else 0
        sign = cos(self.direction * pi / 180) * (self.pos_y - 384) / abs(self.pos_y - 384 + y) + sin(
            self.direction * pi / 180) * (self.pos_x - 384) / abs(self.pos_x - 384 + x)
        return sign*sqrt(pow(self.pos_x - 384,2) + pow(self.pos_y - 384, 2))

    def send_message(self):
        message = Message(self)
        for car in self.follower_cars:
            car.receive(message)

    def add_follower(self, car):
        self.follower_cars.append(car)

    def receive(self, message):
        self.set_message(message)

    def set_message(self, message):
        self.message = message

    def get_message(self):
        return self.message

    def get_followers(self):
        return self.follower_cars

    def stop_following(self):
        self.follow = False

    def start_following(self):
        self.follow = True

    def get_name(self):
        return self.name

    def initial_conditions(self):
        return "Car: " + self.name + " Following: " + self.get_message().car_name + " Lane: " + str(
            self.lane) + " Speed: " + str(self.initial_speed)

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
