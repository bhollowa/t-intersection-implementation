from math import cos, sin, degrees as d, radians, atan


class Direction:
    """
    Direction represented by the bases of a square triangle. It can turn describing a circular shape, like in polar
    coordinates with constant radius of length 1.
    """

    def __init__(self, x=1.0, y=0.0, angle=0.0):
        """
        Initializer for a direction of an object viewed from top. The sum of the squares values of x and y must be 1.
        :param x: Value of the x axis.
        :param y: Value of the x axis.
        :param angle: Value of the angle in which the object is pointing (counterclockwise from the x axis.
        """
        if int(x**2 + y**2) != int(1.0):
            raise UnProperDirectionException
        if x != 0:
            if d(atan(y / x)) != angle:
                raise NotEqualAngleException
        self.x = x
        self.y = y
        self.angle = angle

    def turn(self, angle, direction):
        """
        Turn the object in degrees. Left is counterclockwise and right is clockwise.
        :param angle: How many to turn in degrees.
        :param direction: Direction to turn. Must be 1 (left) or -1 (right).
        """
        self.angle = (self.angle + angle * direction) % 360
        new_angle = radians(self.angle)
        self.x = cos(new_angle)
        self.y = sin(new_angle)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return 'posx: ' + str(self.x) + ' posy: ' + str(self.y) + ' angle: ' + str(self.angle)


class UnProperDirectionException(Exception):
    pass


class NotEqualAngleException(Exception):
    pass
