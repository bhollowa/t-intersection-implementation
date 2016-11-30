from math import pi, cos, sin, atan


class Message(object):
    """
    Message object that can be created from a car. If no car is given, the message will have an "invalid" car name
    (a negative one).
    The message can give the distance to the center of the car from it was created (based on the information given).
    """
    value_dict = {"SupervisorLeftIntersectionMessage": 3, "LeftIntersectionMessage": 2, "NewCarMessage": 1,
                  "InfoMessage": 0, "FollowingCarMessage": 0, "Message": 0}

    def __init__(self, car=None):
        """
        Constructor of a message. The car can be given to use its information.
        :param car: car to create the message from.
        """
        if car is not None:
            self.actual_coordinates = car.get_actual_coordinates()
            self.origin_coordinates = car.get_origin_coordinates()
            self.acceleration = car.get_acceleration()
            self.speed = car.get_speed()
            self.name = car.get_name()
            self.lane = car.get_lane()
            self.creation_time = car.get_creation_time()
            self.new = car.is_new()
            self.intention = car.get_intention()
            self.caravan_depth = car.get_caravan_depth()
        else:
            self.actual_coordinates = (384, 384, 0, 1)
            self.origin_coordinates = (384, 384, 0, 1)
            self.acceleration = 3
            self.name = -1
            self.speed = 10
            self.creation_time = -1
            self.new = True
            self.intention = "s"
            self.caravan_depth = 0
        self.receiver = None
        self.type = "info"
        self.follower = None
        self.car = None
        self.follow = False
        self.value = self.value_dict[self.__class__.__name__]

    def __str__(self):
        """
        Generates a string that describes this message.
        :return: <string>
        """
        return self.__class__.__name__ + " From " + str(self.get_name()) + " depth " + str(self.get_caravan_depth())

    def virtual_distance(self):
        """
        Gets the virtual position of the car.
        :return: <int> virtual position of the car
        """
        conflict_zone_radio = 384.0
        path_width = 172.0
        right_turn_radio = path_width / 4.0
        left_turn_radio = 3 * path_width / 4.0
        initial_straight_section = conflict_zone_radio - path_width / 2.0
        if self.get_intention() == "s":
            virtual_distance_value = self.get_virtual_x_position()
        elif self.get_intention() == "r":
            if self.get_virtual_x_position() <= initial_straight_section:  # Calculate real virtual distance
                virtual_distance_value = self.get_virtual_x_position()
            elif self.get_virtual_y_position() > -right_turn_radio:
                virtual_distance_value = initial_straight_section + atan(
                    (self.get_virtual_x_position() - initial_straight_section) / (
                        right_turn_radio + self.get_virtual_y_position())) * right_turn_radio
            else:
                virtual_distance_value = initial_straight_section + pi * right_turn_radio / 2.0 - \
                                         self.get_virtual_y_position() - right_turn_radio

            a = path_width / 2.0
            b = right_turn_radio + path_width / 4.0
            c = pi * right_turn_radio / 2.0
            if virtual_distance_value <= initial_straight_section + c:  # Scale virtual distance
                virtual_distance_value *= (initial_straight_section + a + b) / (initial_straight_section + c)
            else:
                virtual_distance_value += a + b - c

        else:
            if self.get_virtual_x_position() <= initial_straight_section:  # Calculate real virtual distance
                virtual_distance_value = self.get_virtual_x_position()
            elif self.get_virtual_y_position() < left_turn_radio:
                virtual_distance_value = initial_straight_section + atan(
                    (self.get_virtual_x_position() - initial_straight_section) / (
                        left_turn_radio - self.get_virtual_y_position())) * left_turn_radio
            else:
                virtual_distance_value = initial_straight_section + pi * left_turn_radio / 2 + \
                                         self.get_virtual_y_position() - left_turn_radio

            a = path_width / 2
            b = right_turn_radio + path_width / 4
            c = pi * left_turn_radio / 2
            if virtual_distance_value <= initial_straight_section + c:  # Scale virtual distance
                virtual_distance_value *= (initial_straight_section + a + b) / (initial_straight_section + c)
            else:
                virtual_distance_value += a + b - c

        return virtual_distance_value

    def is_new(self):
        """
        Check if the car that created this message is new at the intersection. a car is new at an intersection if it
        hasn't been analyzed by a supervisory level.
        :return: True if the car is new at the intersection. False otherwise.
        """
        return self.new

    def set_receiver(self, receiver):
        """
        Sets the receiver of the message.
        """
        self.receiver = receiver

    def get_receiver(self):
        """
        Gets the receiver of this message.
        :return: The receiver of the message.
        """
        return self.receiver

    def get_type(self):
        """
        Returns the type of the message
        :return: <string> Message type
        """
        return self.type

    def set_type(self, message_type):
        """
        Sets the type of the message
        :param message_type: <string> type of the mesage
        """
        self.type = message_type

    def get_name(self):
        """
        Gets the name which identifies the car.
        :return: Name of the car
        """
        return self.name

    def get_follower(self):
        """
        Return the follower
        :return: follower
        """
        return self.follower

    def set_follower(self, follower):
        """
        Sets the follower variable
        :param follower: follower name
        """
        self.follower = follower

    def set_car(self, car):
        """
        Sets the car so it can be used at the supervisory level.
        :param car: reference of the car.
        """
        self.car = car

    def get_car(self):
        """
        Returns the car variable.
        :return: car variable
        """
        return self.car

    def set_follow(self, follow):
        """
        Set the follow param.
        :param follow: <boolean>
        """
        self.follow = follow

    def get_follow(self):
        """
        Get the follow param value.
        :return: <boolean>
        """
        return self.follow

    def get_origin_x_position(self):
        """
        Get the origin x position of the car who created this message
        :return:  <int> x position.
        """
        return self.origin_coordinates[0]

    def get_origin_y_position(self):
        """
        Get the origin y position of the car who created this message
        :return:  <int> y position.
        """
        return self.origin_coordinates[1]

    def get_x_position(self):
        """
        Get the x position of the car who created this message
        :return:  <int> x position.
        """
        return self.actual_coordinates[0]

    def get_y_position(self):
        """
        Get the y position of the car who created this message
        :return:  <int> y position.
        """
        return self.actual_coordinates[1]

    def get_direction(self):
        """
        Get the direction position of the car who created this message
        :return:  <int> direction position.
        """
        return self.actual_coordinates[2]

    def get_acceleration(self):
        """
        Get the acceleration of the car that created this message
        :return: <int> Acceleration of the car
        """
        return self.acceleration

    def get_intention(self):
        """
        Get the intention of the car that created this message.
        :return: <string> intention
        """
        return self.intention

    def get_virtual_x_position(self):
        """
        Returns the x position of the virtual caravan environment.
        :return: <float> x position at the virtual environment
        """
        x_real = (self.get_x_position() - self.get_origin_x_position()) * sin(self.get_origin_direction() * pi / 180)
        y_real = (self.get_y_position() - self.get_origin_y_position()) * cos(self.get_origin_direction() * pi / 180)
        return abs(x_real + y_real)

    def get_virtual_y_position(self):
        """
        Returns the x position of the virtual caravan environment.
        :return: <float> x position at the virtual environment
        """
        x_real = - 1 * (self.get_x_position() - self.get_origin_x_position()) * cos(
            self.get_origin_direction() * pi / 180)
        y_real = (self.get_y_position() - self.get_origin_y_position()) * sin(self.get_origin_direction() * pi / 180)
        return x_real + y_real

    def get_origin_direction(self):
        """
        Return the direction of the origin coordinates of a car.
        :return: <int> origin direction.
        """
        return self.origin_coordinates[2]

    def get_caravan_depth(self):
        """
        Get the car depth at the caravan.
        :return: <int> depth of the car at the caravan.
        """
        return self.caravan_depth

    def set_depth(self, new_depth):
        """
        Sets the depth of the car at the caravan. Function created for the supervisory level.
        :param new_depth: new depth of the car at the caravan.
        """
        self.caravan_depth = new_depth

    def get_lane(self):
        """
        Returns the lane of the car that created this message.
        :return: <int> lane number.
        """
        return self.lane

    def cross_path(self, other_car_lane, other_car_intention):
        """
        Check if the path of one car crosses tih the path o f another. It is true if the other car is the same lane
        or if the other car is in one of the perpendicular lanes.
        :param other_car_intention: the intention of way of the other car
        :param other_car_lane: the lane at which the other car star its way.
        :return: True if the paths does not crosses, False otherwise.
        """
        self_lane = self.get_lane()
        self_intention = self.get_intention()
        lane_to_int_dict = {"l": 0, "s": 1, "r": 2}
        table0 = [[True, True, True], [True, True, True], [True, True, True]]
        table1 = [[True, True, False], [True, True, False], [False, True, False]]
        table2 = [[True, True, True], [True, False, False], [True, False, False]]
        table3 = [[True, True, False], [True, True, True], [False, False, False]]
        all_tables = [table0, table1, table2, table3]
        return all_tables[(self_lane - other_car_lane) % 4][lane_to_int_dict[self_intention]][
            lane_to_int_dict[other_car_intention]]

    def get_value(self):
        """
        Get the value of the message. Depends of the class of the message. Used for sorting purposes.
        :return: <int>
        """
        return self.value

    def get_creation_time(self):
        """
        Get the creation time of the car that created this message.
        :return:
        """
        return self.creation_time

    def process(self, car):
        """
        Process the message. Depends of the class. Kind of instance method.
        :param car: car that will process the message.
        """
        pass


class InfoMessage(Message):
    """
    Message used to update the info of the car that is being followed by another car.
    """
    def process(self, car):
        """
        Process the message. Sets the old message to be this new one, so the information of the car is updated.
        :param car: car whose following car information will be updated.
        """

        if car.get_following_car_message().get_name() == self.get_name():
            car.set_following_car_message(self)


class NewCarMessage(Message):
    """
    Message used to inform all the other cars that a new car has arrived at the intersection.
    """
    def __init__(self, car):
        """
        Initializer for this message. The only new information needed is the cars at the intersection.
        :param car: new car at the intersection..
        """
        super(self.__class__, self).__init__(car)
        self.following_car_message = car.get_following_car_message()

    def process(self, car):
        """
        Process the message. Creates a new car with the information present at this message and add it to the list of
        cars present at the intersection.
        :param car: car to add a new car to the list of cars present at the intersection.
        """
        super(self.__class__, self).process(car)
        car.add_new_car(self)

    # def get_following_car_message(self):
    #     """
    #     Gets the message generated
    #     :return:
    #     """
    #     return self.following_car_message


class LeftIntersectionMessage(Message):
    """
    Message used to inform all the other cars that a car has left the intersection.
    """
    def process(self, car):
        """
        Process the message. Deletes the car that created this message from the list of cars present at the
        intersection.
        :param car: car to update information
        """
        super(self.__class__, self).process(car)
        car.delete_car(self)


class SupervisorLeftIntersectionMessage(Message):
    """
    Message created by a car that was supervisor and has left the intersection.
    """
    def __init__(self, car):
        """
        Initializer for this message. The only new information needed is the cars at the intersection.
        :param car: supervisor leaving the intersection.
        """
        super(self.__class__, self).__init__(car)
        cars_at_intersection = car.get_cars_at_intersection()
        for car_at_intersection in cars_at_intersection:
            if car_at_intersection.get_name() == car.get_name():
                cars_at_intersection.remove(car_at_intersection)
        self.cars_at_intersection = cars_at_intersection
        self.new_supervisor_name = car.get_new_supervisor_name()

    def process(self, car):
        """
        Process the message. Makes the car the new supervisor and gives it all the information needs to work correctly.
        :param car: new supervisor.
        """
        super(self.__class__, self).process(car)
        if car.get_name() == self.get_new_supervisor_name():
            car.make_supervisor(self)

    def get_cars_at_intersection(self):
        """
        Returns the list of cars present at the intersection
        :return: list of cars
        """
        return self.cars_at_intersection

    def get_new_supervisor_name(self):
        """
        Gets the name of the car that must be the new supervisor.
        :return: <int> car name
        """
        return self.new_supervisor_name


class FollowingCarMessage(Message):
    """
    Message used to inform a specific car which car it must follow.
    """
    def __init__(self, car, following_car_name):
        """
        Initializer for this message. The only new information needed is the cars at the intersection.
        :param car: supervisor leaving the intersection.
        """
        super(self.__class__, self).__init__(car)
        self.following_car_name = following_car_name

    def process(self, car):
        """
        Process the message. Makes the car that this message is for
        :param car: car to update information
        """
        super(self.__class__, self).process(car)
        car.start_following(self)

    def get_following_car_name(self):
        """
        Get the name of the car that the car receptor of this message must follow.
        :return: <int> car name
        """
        return self.following_car_name
