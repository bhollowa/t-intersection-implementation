from math import pi, cos, sin, sqrt, pow


class Message:
    def __init__(self, car=None):
        if car is not None:
            self.pos_x, self.pos_y = car.get_position()
            self.direction = car.get_direction()
            self.speed = car.get_speed()
            self.car_name = car.get_name()
        self.car_name = -1

    def distance_to_center(self):
        x = 1 if self.pos_x % 384 == 0 else 0
        y = 1 if self.pos_y % 384 == 0 else 0
        sign = cos(self.direction * pi / 180)*(self.pos_y - 384)/abs(self.pos_y - 384 + y) + sin(self.direction * pi / 180)*(self.pos_x - 384)/abs(self.pos_x - 384 + x)
        return sign*sqrt(pow(self.pos_x - 384,2) + pow(self.pos_y - 384, 2))