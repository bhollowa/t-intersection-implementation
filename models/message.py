from math import pi, cos, sin, sqrt, pow

class Message:
    def __init__(self, car):
        self.pos_x, self.pos_y = car.get_position()
        self.direction = car.get_direction()
        self.speed = car.get_speed()

    def distance_to_center(self):
        sign = cos(self.direction * pi / 180)*(self.pos_y - 384)/abs(self.pos_y - 384) + sin(self.direction * pi / 180)*(self.pos_x - 384)/abs(self.pos_x - 384)
        return sign*sqrt(pow(self.pos_x - 384,2) + pow(self.pos_y - 384, 2))