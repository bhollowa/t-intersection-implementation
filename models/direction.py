from math import cos, sin, degrees as d, radians, atan


class Direction:
    """
    Direction represented by the bases of a square triangle. It can turn describing a circular shape, like in polar
    coordinates with constant radius of length 1.
    """

    def __init__(self, x=1.0, y=0.0):
        """
        Initializer for a direction of an object viewed from top. The sum of the squares values of x and y must be 1.
        :param x: Value of the x axis.
        :param y: Value of the x axis.
        """
        if int(x**2 + y**2) != int(1.0):
            raise UnProperDirectionException
        self.x = x
        self.y = y

    def turn(self, degrees, direction):
        """
        Turn the object in degrees. Left is counterclockwise and right is clockwise.
        :param degrees: How many to turn in degrees.
        :param direction: Direction to turn. Must be 1 (left) or -1 (right).
        """
        angle = radians((d(atan(self.y/self.x)) + degrees * direction) % 360)
        self.x = cos(angle)
        self.y = sin(angle)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class UnProperDirectionException(Exception):
    pass
