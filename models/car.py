class Car:

    def __init__(self):
        self.pos_x = 0
        self.pos_y = 0
        self.speed = 0
        self.max_speed = 17
        self.acceleration = 3

    def reset(self):
        self.pos_x = 0
        self.pos_y = 0
        self.speed = 0

    def accelerate_x_seconds(self, seconds):
        total_distance = self.speed*seconds + self.acceleration * (seconds ** 2) / 2
        self.pos_x += total_distance
        self.speed += self.acceleration * seconds
        return total_distance

    def accelerate_y_seconds(self, seconds):
        total_distance = self.speed * seconds + self.acceleration * (seconds ** 2) / 2
        self.pos_y += total_distance
        self.speed += self.acceleration * seconds
        return total_distance

    def accelerate_x_meters(self, meters):
        total_time = (-self.speed + (self.speed**2 + 2*self.acceleration*meters)**(1.0/2))/self.acceleration
        self.pos_x += meters
        self.speed += self.acceleration * total_time
        return total_time
