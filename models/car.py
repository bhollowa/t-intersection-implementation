from models.direction import Direction


class Car:
    """
    Car representation. It has x and y position (as in a cartesian plane), an absolute speed and a direction. In case
    of movement, the total movement will be escalated into x and y with the direction.
    Also, the car has a fixed acceleration and maximum speed.
    """
    SECONDS = 1000.0
    max_absolute_speed = 120.0  # In meters/seconds.
    acceleration = 3.0  # In meters/seconds*seconds.

    def __init__(self, pos_x=0.0, pos_y=0.0, absolute_speed=0.0, direction=Direction()):
        """
        Initializer of a car. It can be placed anywhere looking in any direction with any speed under the car maximum
        speed.
        :param pos_x: x value of the car position.
        :param pos_y: y value of the car position.
        :param absolute_speed: absolute speed of the car.
        :param direction: direction at which the front of the car is looking.
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
        if abs(absolute_speed) > self.max_absolute_speed:
            raise ExceedCarMaximumSpeedError
        self.absolute_speed = absolute_speed
        self.direction = direction

    def move(self, quantity, time_unit):
        """
        Function to move a car. If its speed its 0, it'll not move. Time unit is necessary to work in milliseconds.
        Seconds = 1000.
        :param quantity: how many unit of times the car must move.
        :param time_unit: unit of time in which the car will move (seconds = 1000)
        :return: None
        """
        self.pos_x += self.direction.x * self.absolute_speed * quantity * time_unit / self.SECONDS
        self.pos_y += self.direction.y * self.absolute_speed * quantity * time_unit / self.SECONDS

    def accelerate(self, quantity, time_unit):
        """
        Function to accelerate a car. Exception raised if maximum speed is reached or surprassed. Time unit is necessary
         to work in milliseconds. Seconds = 1000.
        :param quantity: how many unit of times the car must accelerate.
        :param time_unit: unit of time in which the car will accelerate (seconds = 1000)
        :return: None
        """
        total_distance = self.acceleration * quantity ** 2 * time_unit / (self.SECONDS * 2) + \
            self.absolute_speed * quantity * time_unit / self.SECONDS
        new_speed = self.absolute_speed + self.acceleration * quantity * time_unit / self.SECONDS
        if new_speed > self.max_absolute_speed:
            raise ExceedCarMaximumSpeedError
        self.absolute_speed += self.acceleration * quantity * time_unit / self.SECONDS
        self.pos_x += total_distance * self.direction.x
        self.pos_y += total_distance * self.direction.y


class ExceedCarMaximumSpeedError(Exception):
    pass
