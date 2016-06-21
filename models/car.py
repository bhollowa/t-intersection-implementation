from models.direction import Direction


class Car:
    max_speed = 17  # In meters/seconds
    acceleration = 3  # In meters/seconds*seconds

    def __init__(self, pos_x=0, pos_y=0, absolute_speed=0, direction=Direction()):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.absolute_speed = absolute_speed
        self.direction = direction
