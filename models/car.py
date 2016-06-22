from models.direction import Direction


class Car:
    SECONDS = 1000.0
    max_absolute_speed = 17.0  # In meters/seconds
    acceleration = 3.0  # In meters/seconds*seconds

    def __init__(self, pos_x=0.0, pos_y=0.0, absolute_speed=0.0, direction=Direction()):
        self.pos_x = pos_x
        self.pos_y = pos_y
        if abs(absolute_speed) > self.max_absolute_speed:
            raise ExceedMaximumSpeedError
        self.absolute_speed = absolute_speed
        self.direction = direction

    def move(self, quantity, time_unit):
        self.pos_x += self.direction.x * self.absolute_speed * quantity * time_unit / self.SECONDS
        self.pos_y += self.direction.y * self.absolute_speed * quantity * time_unit / self.SECONDS

    def accelerate(self, quantity, time_unit):
        total_distance = self.acceleration * quantity ** 2 * time_unit / (self.SECONDS * 2) + \
                         self.absolute_speed * quantity * time_unit / self.SECONDS
        self.absolute_speed += self.acceleration * quantity * time_unit / self.SECONDS
        self.pos_x += total_distance * self.direction.x
        self.pos_y += total_distance * self.direction.y


class ExceedMaximumSpeedError(Exception):
    pass
