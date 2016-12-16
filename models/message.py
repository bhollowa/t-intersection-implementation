from math import pi, cos, sin, atan


class Message(object):
    """
    Message object that can be created from a car. If no car is given, the message will have an "invalid" car name
    (a negative one).
    The message can give the distance to the center of the car from it was created (based on the information given).
    """
    value_dict = {"SupervisorLeftIntersectionMessage": 5, "LeftIntersectionMessage": 2, "NewCarMessage": 1,
                  "InfoMessage": 0, "FollowingCarMessage": 0, "Message": 0, "SecondAtChargeMessage": 4,
                  "NewSupervisorMessage": 3}

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
            self.supervisor = car.is_supervisor
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
            self.supervisor = False
        self.receiver = None
        self.follower = None
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

    def transmit(self, car_dict, transmitter_to_receiver_dict):
        """
        Transmit the message to all the cars that should receive this message
        :param car_dict: list of cars as a dictionary with the name of the car as the key and the car as the value.
        :param transmitter_to_receiver_dict: dictionary with the name of the transmitter as key and a list with the
        names of the receivers as value.
        :return: None
        """
        for car_name in transmitter_to_receiver_dict[self.get_name()]:
            self.process(car_dict[car_name])


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
        if car.is_second_at_charge and self.supervisor:
            car.reset_supervisor_counter()
        if car.is_supervisor:
            if self.get_name() in car.update_cars_at_intersection_counter:
                car.update_cars_at_intersection_counter[self.get_name()] = 4


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

    def process(self, car):
        """
        Process the message. Creates a new car with the information present at this message and add it to the list of
        cars present at the intersection.
        :param car: car to add a new car to the list of cars present at the intersection.
        """
        super(self.__class__, self).process(car)
        car.add_new_car(self)

    def transmit(self, car_dict, transmitter_to_receiver_dict):
        """
        Overrides transmit of generic message. For this message class, all cars must receive the message.
        :param car_dict: list of cars as a dictionary with the name of the car as the key and the car as the value.
        :param transmitter_to_receiver_dict: dictionary with the name of the transmitter as key and a list with the
        names of the receivers as value.
        :return: None
        """
        for car in car_dict.values():
            self.process(car)


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
        super(LeftIntersectionMessage, self).process(car)
        car.delete_car_at_intersection(self)

    def transmit(self, car_dict, transmitter_to_receiver_dict):
        """
        Overrides transmit of generic message. For this message class, all cars must receive the message.
        :param car_dict: list of cars as a dictionary with the name of the car as the key and the car as the value.
        :param transmitter_to_receiver_dict: dictionary with the name of the transmitter as key and a list with the
        names of the receivers as value.
        :return: None
        """
        for car in car_dict.values():
            self.process(car)


class SupervisorLeftIntersectionMessage(LeftIntersectionMessage):
    """
    Message created by a car that was supervisor and has left the intersection.
    """

    def process(self, car):
        """
        Process the message. Makes the car the new supervisor and gives it all the information needs to work correctly.
        :param car: new supervisor.
        """
        super(SupervisorLeftIntersectionMessage, self).process(car)
        if car.is_second_at_charge:
            car.set_supervisor_left_intersection(True)

    def transmit(self, car_dict, transmitter_to_receiver_dict):
        """
        Overrides transmit of generic message. For this message class, all cars must receive the message.
        :param car_dict: list of cars as a dictionary with the name of the car as the key and the car as the value.
        :param transmitter_to_receiver_dict: dictionary with the name of the transmitter as key and a list with the
        names of the receivers as value.
        :return: None
        """
        for car in car_dict.values():
            self.process(car)


class FollowingCarMessage(Message):
    """
    Message used to inform a specific car which car it must follow.
    """
    def __init__(self, car, following_car_name):
        """
        Initializer for this message. The only new information needed is the cars at the intersection.
        :param car: supervisor leaving the intersection.
        :param following_car_name: name of the car that must follow the car that created the message.
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

    def transmit(self, car_dict, transmitter_to_receiver_dict):
        """
        Overrides transmit of generic message. For this message class, all cars must receive the message.
        :param car_dict: list of cars as a dictionary with the name of the car as the key and the car as the value.
        :param transmitter_to_receiver_dict: dictionary with the name of the transmitter as key and a list with the
        names of the receivers as value.
        :return: None
        """
        for car in car_dict.values():
            self.process(car)


class SecondAtChargeMessage(Message):
    def __init__(self, car, second_at_charge_name):
        """
        Initializer for SecondAtChargeMessage. The info needes for the second at charge is the list of car present
        at the intersection of the supervisor car.
        :param car: supervisor leaving the intersection.
        :param second_at_charge_name: name of the car that will be the second at charge.
        """
        super(self.__class__, self).__init__(car)
        self.second_at_charge_name = second_at_charge_name
        self.cars_at_intersection = car.get_cars_at_intersection()
        self.transmitter_receiver_dict = car.get_transmitter_receiver_dict()

    def process(self, car):
        """
        Process the message for a car. If the name of the car is the same as the second at charge name stored in the
        message, that car will be made the second at charge.
        :param car: car to process the message
        :return: None
        """
        super(SecondAtChargeMessage, self).process(car)
        if car.is_second_at_charge:
            car.make_car()
        if car.get_name() == self.get_second_at_charge_name():
            car.make_second_at_charge(self)

    def get_second_at_charge_name(self):
        """
        Returns the name of the car that should be the second at charge.
        :return: <int> Second at charge name
        """
        return self.second_at_charge_name

    def get_cars_at_intersection(self):
        """
        Returns the list of cars present at the intersection
        :return: list of cars
        """
        return self.cars_at_intersection

    def get_transmitter_receiver_dict(self):
        """
        Return the transmitter_receiver_dict
        :return: <dict>
        """
        return self.transmitter_receiver_dict

    def transmit(self, car_dict, transmitter_to_receiver_dict):
        """
        Overrides transmit of generic message. For this message class, all cars must receive the message.
        :param car_dict: list of cars as a dictionary with the name of the car as the key and the car as the value.
        :param transmitter_to_receiver_dict: dictionary with the name of the transmitter as key and a list with the
        names of the receivers as value.
        :return: None
        """
        self.process(car_dict[self.get_second_at_charge_name()])


class NewSupervisorMessage(Message):
    """
    Message class to inform a car that it's the new supervisor.
    """
    def __init__(self, car):
        """
        Gets the information to send this message to the new supervisor car.
        :param car: car which created the message.
        """
        super(self.__class__, self).__init__(car)
        self.cars_at_intersection = car.get_cars_at_intersection()
        self.new_supervisor_name = car.get_new_supervisor_name()
        self.transmitter_receiver_dict = car.get_transmitter_receiver_dict()

    def process(self, car):
        """
        Process the message for a car. If the name of the car is the same as the second at charge name stored in the
        message, that car will be made the second at charge.
        :param car: car to process the message
        :return: None
        """
        super(NewSupervisorMessage, self).process(car)
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

    def get_transmitter_receiver_dict(self):
        """
        Return the transmitter_receiver_dict
        :return: <dict>
        """
        return self.transmitter_receiver_dict

    def transmit(self, car_dict, transmitter_to_receiver_dict):
        """
        Overrides transmit of generic message. For this message class, all cars must receive the message.
        :param car_dict: list of cars as a dictionary with the name of the car as the key and the car as the value.
        :param transmitter_to_receiver_dict: dictionary with the name of the transmitter as key and a list with the
        names of the receivers as value.
        :return: None
        """
        self.process(car_dict[self.get_new_supervisor_name()])
        self.process(car_dict[self.get_name()])
