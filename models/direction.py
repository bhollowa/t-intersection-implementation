from math import acos, cos, sin, radians


class Direction:

    def __init__(self, x=1, y=0):
        """
        Initializer for a direction of an object viewed from top. The sum of the squares values of x and y must be 1.
        :param x: Value of the x axis.
        :param y: Value of the x axis.
        """
        if x**2+y**2 != 1:
            raise UnProperDirectionException
        self.x = x
        self.y = y

    def turn(self, degrees, direction):
        """
        Turn the object counterclockwise in degrees
        :param degrees: How many to turn in degrees.
        :param direction: Direction to turn. Must be 1 (left) or -1 (right).
        """
        angle = acos(self.x) + radians(degrees * direction)
        self.x = cos(angle)
        self.y = sin(angle)


class UnProperDirectionException(Exception):
    pass
