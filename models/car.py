import os
from math import pi, cos, sin, atan
from pygame import image, transform
from time import time
import random
from car_controllers import default_controller, follower_controller
from models.message import Message, InfoMessage, FollowingCarMessage, LeftIntersectionMessage, \
    SupervisorLeftIntersectionMessage, SecondAtChargeMessage, NewSupervisorMessage, NewCarMessage

images_directory = os.path.dirname(os.path.abspath(__file__)) + "/../images/"


class Car(object):
    """
    Car representation. It has x and y position (as in a cartesian plane), an absolute speed and a direction. In case
    of movement, the total movement will be escalated into x and y with the direction.
    Also, the car has a fixed acceleration and maximum speed.
    """
    TIME_STEP = 0.1
    SPEED_FACTOR = 2
    max_forward_speed = 20.0  # meters/seconds.
    acceleration_rate = 3.0  # meters/seconds*seconds.
    following_car_message = Message()
    image_scale_rate = 0.05
    maximum_acceleration = 4.2
    minimum_acceleration = -5.0

    def __init__(self, name, pos_x=0.0, pos_y=0.0, absolute_speed=0.0, direction=0, lane=1,
                 controller=default_controller.default_controller, creation_time=None, left_intersection_time=None,
                 intention="s"):
        """
        :param name: id to identify the car. Integer
        :param pos_x: x value of the car position.
        :param pos_y: y value of the car position.
        :param absolute_speed: absolute speed of the car.
        :param direction: direction of the car. Represented in degrees.
        :param lane: lane in which the car is travelling.
        :param direction: direction at which the front of the car is looking.
        :param controller: object which controls the speed of the car.
        """
        self.initial_speed = absolute_speed  # initial speed of the car when it appeared in the simulation.
        self.creation_time = creation_time
        self.left_intersection_time = left_intersection_time
        self.controller = controller
        self.name = name
        self.initial_coordinates = (pos_x, pos_y, direction, lane)
        self.actual_coordinates = (pos_x, pos_y, direction, lane)
        self.absolute_speed = absolute_speed
        self.lane = lane
        self.intention = intention
        self.image = None
        self.rotated_image = None
        self.screen_car = None
        self.following = False  # True if the car is following some other car
        self.new_car = True
        self.has_second_at_charge = False
        self.supervisor_left_intersection = False
        self.attack_supervisor = False
        self.has_alternate_second_at_charge = False
        self.supervisor_lies = False
        self.control_law_value = 0
        self.last_virtual_distance = 0
        self.new_supervisor_name = -1
        self.registered_caravan_depth = 0
        self.supervisor_counter = 4  # A car is coordinated in 2 ticks. If a car isn't
        # coordinated in 4 ticks, the second at charge car will assume the supervisor isn't coordinating anymore.
        self.following_car_counter = 4  # same as up
        self.transmitter_receiver_dict = {}
        self.coordination_messages = {}
        self.cars_at_intersection = {}
        self.update_cars_at_intersection_counter = {}
        self.new_messages = []
        self.log_messages = []
        self.new_cars_at_intersection_counter = []

    def __eq__(self, other):
        """
        compares two cars. For simplicity, two cars are the same if they share the same name
        :param other: other car
        :return: <boolean>
        """
        if isinstance(other, type(self)):
            if other.get_name() == self.get_name():
                return True
        return False

    def __str__(self):
        """
        String representation of the car. Adapted to output actual state of the car to a log file.
        Example: "Car: 48 Speed: 19.975 Following: 47" if car is following other car,
        Example: "Car: 48 Speed: 19.975" else.
        :return: String representation of the car.
        """
        return "Car " + str(self.get_name()) + " lane " + str(self.get_lane()) + " intention " + self.get_intention() \
               + " depth " + str(self.get_caravan_depth()) + " following " \
               + str(self.get_following_car_message().get_name()) + " creation time " + str(self.get_creation_time())

    def to_json(self):
        """
        Returns a string representing a car in json format, for log use.
        :return: sting of json representation of a car.
        """
        return_string = '{'
        return_string += '"name":' + str(self.get_name())
        return_string += ',"following":' + str(self.get_following_car_message().get_name())
        return_string += ',"lane":' + str(self.get_lane())
        return_string += ',"speed":' + str(self.get_speed())
        return_string += ',"creation_time":' + str(self.get_creation_time())
        return_string += ',"left_intersection_time":' + str(self.get_left_intersection_time())
        return_string += ',"intention":"' + self.get_intention() + '"'
        return_string += ',"actual_coordinates":{ '
        return_string += '"x_coordinate":' + str(self.get_x_position())
        return_string += ',"y_coordinate":' + str(self.get_y_position())
        return_string += ',"direction":' + str(self.get_direction())
        return_string += '}'
        return_string += ',"initial_coordinates":{ '
        return_string += '"x_coordinate":' + str(self.get_origin_x_position())
        return_string += ',"y_coordinate":' + str(self.get_origin_y_position())
        return_string += ',"direction":' + str(self.get_origin_direction())
        return_string += '}'
        return_string += ',"actual_caravan_depth":' + str(self.get_caravan_depth())
        return_string += '}'
        return return_string

    def move(self):
        """
        Function to move a car. If its speed its 0, it'll not move. Time unit is necessary to work in milliseconds.
        Seconds = 1000.
        """
        rad = self.get_direction() * pi / 180
        pos_x = self.get_x_position()
        pos_y = self.get_y_position()
        pos_x_diff = -sin(rad) * self.get_speed() * self.TIME_STEP * self.SPEED_FACTOR
        pos_y_diff = -cos(rad) * self.get_speed() * self.TIME_STEP * self.SPEED_FACTOR
        self.set_x_position(pos_x + pos_x_diff)
        self.set_y_position(pos_y + pos_y_diff)

    def turn(self):
        """
        Turns the car to the direction it intends to turn.
        """
        path_width = 172.0
        conflict_zone_radio = 384.0
        initial_straight_section = conflict_zone_radio - path_width / 2.0
        if self.get_virtual_x_position() > initial_straight_section and \
                self.get_controller() is not default_controller.default_controller:
            self.set_controller(default_controller.default_controller)
        if self.get_intention() == "r":
            right_turn_radio = path_width / 4.0
            if self.get_virtual_y_position() > -right_turn_radio and \
                    self.get_virtual_x_position() > initial_straight_section:
                direction_change = 90.0 * (self.get_speed() * self.TIME_STEP * self.SPEED_FACTOR) / (
                    pi / 2 * right_turn_radio)
                self.set_direction(self.get_direction() - direction_change)
        elif self.get_intention() == "l":
            left_turn_radio = 3 * path_width / 4.0
            if self.get_virtual_y_position() < left_turn_radio and \
                    self.get_virtual_x_position() > initial_straight_section:
                direction_change = 90.0 * (self.get_speed() * self.TIME_STEP * self.SPEED_FACTOR) / (
                    pi / 2 * left_turn_radio)
                self.set_direction(self.get_direction() + direction_change)

    def accelerate(self):
        """
        Function to accelerate a car. Exception raised if maximum speed is reached or surpassed. Time unit is necessary
         to work in milliseconds. Seconds = 1000.
        :return: None
        """
        speed_diff = self.acceleration_rate * self.TIME_STEP
        new_speed = self.absolute_speed + speed_diff

        if new_speed > self.max_forward_speed:
            self.absolute_speed = self.max_forward_speed
        elif new_speed < 0:
            self.absolute_speed = 0
        else:
            self.absolute_speed = new_speed

    def draw_car(self):
        """
        Prepares the image of the car to be drawn. The image is rotated, re-escalated and moved.
        """
        self.rotated_image = transform.rotate(self.image, self.get_direction())
        self.rotated_image = transform.scale(self.rotated_image, (
            int(self.rotated_image.get_rect().w * self.get_image_scale_rate()),
            int(self.rotated_image.get_rect().h * self.get_image_scale_rate())))
        self.screen_car = self.rotated_image.get_rect()
        self.screen_car.center = self.get_position()

    def update(self):
        """
        Updates the speed, position and images of the car. Receives inputs as if a user were playing with the car
        with the keyboards arrows.
        """
        if self.following_car_counter == 0:
            self.set_controller(default_controller.default_controller)
        self.following_car_counter -= 1
        self.accelerate()
        self.get_controller()(self)
        self.turn()
        self.move()
        self.draw_car()
        self.get_new_messages().append(InfoMessage(self))

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
            b = left_turn_radio - path_width / 4
            c = pi * left_turn_radio / 2
            if virtual_distance_value <= initial_straight_section + c:  # Scale virtual distance
                virtual_distance_value *= (initial_straight_section + a + b) / (initial_straight_section + c)
            else:
                virtual_distance_value += a + b - c

        return virtual_distance_value

    def start_following(self, message):
        """
        Sets the variable follow to True to indicate that this car has started following another car. Also updates
        the information of the cars at the intersection.
        :param message: message with the following info.
        """
        if self.get_name() == message.get_following_car_name():
            if message.get_name() != -1:
                self.set_following_car_message(message)
                self.set_controller(follower_controller.follower_controller)
                self.set_following(True)
        if message.get_following_car_name() in self.get_cars_at_intersection():
            car = self.get_cars_at_intersection()[message.get_following_car_name()]
            car.set_following_car_message(message)
            car.set_controller(follower_controller.follower_controller)
            car.set_following(True)

    def new_image(self, scale_rate=image_scale_rate):
        """
        Creates the image representation of a car, with his rotated image and his screen representation (with the rect).
        """
        self.image = image.load(images_directory + "car.png")
        self.rotated_image = transform.rotate(self.image, self.get_direction())  # image of the car rotated
        self.rotated_image = transform.scale(self.rotated_image, (  # reduction of the size of the image
            int(self.rotated_image.get_rect().w * scale_rate),
            int(self.rotated_image.get_rect().h * scale_rate)))
        self.screen_car = self.rotated_image.get_rect()  # rectangle representation of the car
        self.screen_car.center = self.get_position()  # add the position to the rectangle

    def collide(self, list_of_cars):
        """
        Check if a car collides with any car of the list of cars.
        :param list_of_cars: cars to check if this car is colliding with.
        :return: True if a collision is detected, False otherwise,
        """
        for car in list_of_cars:
            if self.get_rect().colliderect(car.get_rect()):
                return True
        return False

    def reset(self):
        """
        Sets all the attributes of the car as if it just arrived at the intersection.
        """
        initial_positions = [(435, 760, 0, 0), (760, 345, 90, 1), (345, 10, 180, 2), (10, 435, 270, 3)]
        self.set_x_position(initial_positions[self.get_lane()][0])
        self.set_y_position(initial_positions[self.get_lane()][1])
        self.set_direction(initial_positions[self.get_lane()][2])
        self.set_origin_coordinates(self.lane)

    def add_new_car(self, new_car_message):
        """
        Adds a car to the list of cars present at the intersection.
        :param new_car_message: message with the information of the new car.
        """
        new_car = Car(new_car_message.get_name(), lane=new_car_message.get_lane(),
                      intention=new_car_message.get_intention(), creation_time=new_car_message.get_creation_time())
        self.transmitter_receiver_dict[new_car.get_name()] = []
        self.get_cars_at_intersection()[new_car.get_name()] = new_car

    def delete_car_at_intersection(self, left_intersection_message):
        """
        Deletes a car from the list of cars at the intersection
        :param left_intersection_message: message of the car that left the intersection
        """
        cars_at_intersection = self.get_cars_at_intersection().values()
        cars_at_intersection.sort(key=lambda car_at_intersection: car_at_intersection.get_name())
        # update car information
        for car in cars_at_intersection:
            if left_intersection_message.get_name() == car.get_following_car_message().get_name():
                car.set_controller(default_controller.default_controller)
                car.set_following(False)
        if left_intersection_message.get_name() in cars_at_intersection:
            del cars_at_intersection[left_intersection_message.get_name()]

        # update following car information
        for car in cars_at_intersection:
            following_car_name = car.get_following_car_message().get_name()
            if following_car_name in self.get_cars_at_intersection():
                car.set_following_car_message(InfoMessage(self.get_cars_at_intersection()[following_car_name]))

        if left_intersection_message.get_name() == self.get_following_car_message().get_name():
            self.set_controller(default_controller.default_controller)
            self.set_following(False)
        if left_intersection_message.get_name() in self.transmitter_receiver_dict:
            del self.transmitter_receiver_dict[left_intersection_message.get_name()]

    def make_supervisor(self, new_supervisor_message):
        """
        Makes this car the supervisor of the intersection.
        :param new_supervisor_message:
        """
        self.__class__ = SupervisorCar
        for car_name in new_supervisor_message.get_cars_at_intersection():
            self.get_cars_at_intersection()[car_name] = new_supervisor_message.get_cars_at_intersection()[car_name]
            self.update_cars_at_intersection_counter[car_name] = 4
        self.set_transmitter_receiver_dict(new_supervisor_message.get_transmitter_receiver_dict())

    def make_second_at_charge(self, second_at_charge_message):
        """
        Makes this the second at charge of the supervisor car.
        :param second_at_charge_message: message with the information needed for the second at charge.
        """
        self.__class__ = SecondAtChargeCar
        self.set_cars_at_intersection(second_at_charge_message.get_cars_at_intersection())
        self.set_transmitter_receiver_dict(second_at_charge_message.get_transmitter_receiver_dict())

    def make_car(self):
        """
        Change the class of this car to Car
        """
        self.__class__ = Car

    def is_new(self):
        """
        Function to check if this car is new in the intersection.
        :return: <boolean> True if the car is new (and haven't been assigned a following car). False otherwise.
        """
        return self.new_car

    @property
    def is_supervisor(self):
        """
        Returns False. A Car isn't a supervisor.
        :return: <boolean> False
        """
        return False

    @property
    def is_second_at_charge(self):
        """
        Returns False. A Car isn't the second at charge.
        :return: <boolean> False
        """
        return False

    def set_following(self, following):
        """
        Sets the following parameter.
        :param following: <boolean>
        """
        self.following = following

    def get_acceleration(self):
        """
        Gets the actual acceleration of the car
        :return:  <int> acceleration of the car
        """
        return self.acceleration_rate

    def set_acceleration(self, acceleration):
        """
        Sets the acceleration at a new value.
        :param acceleration: new value of the acceleration
        """
        new_acceleration = self.acceleration_rate + acceleration
        if new_acceleration > self.get_maximum_acceleration():
            self.acceleration_rate = self.get_maximum_acceleration()
        elif new_acceleration < self.get_minimum_acceleration():
            self.acceleration_rate = self.get_minimum_acceleration()
        else:
            self.acceleration_rate = new_acceleration

    def get_image_scale_rate(self):
        """
        Get the rate at which the image is being scales
        :return: <int> image scale rate
        """
        return self.image_scale_rate

    def get_origin_x_position(self):
        """
        Return the x position of the origin coordinates of a car.
        :return: <int> origin x.
        """
        return self.initial_coordinates[0]

    def get_origin_y_position(self):
        """
        Return the y position of the origin coordinates of a car.
        :return: <int> origin y.
        """
        return self.initial_coordinates[1]

    def get_origin_direction(self):
        """
        Return the direction of the origin coordinates of a car.
        :return: <int> origin direction.
        """
        return self.initial_coordinates[2]

    def get_origin_lane(self):
        """
        Return the lane of the origin coordinates of a car.
        :return: <int> origin lane.
        """
        return self.initial_coordinates[3]

    def get_x_position(self):
        return self.actual_coordinates[0]

    def get_y_position(self):
        return self.actual_coordinates[1]

    def set_x_position(self, new_x):
        self.actual_coordinates = (
            new_x, self.get_y_position(), self.get_direction(), self.get_lane())

    def set_y_position(self, new_y):
        self.actual_coordinates = (
            self.get_x_position(), new_y, self.get_direction(), self.get_lane())

    def get_position(self):
        """
        Returns the actual position of the car.
        :return: Position of the car
        """
        return self.get_x_position(), self.get_y_position()

    def set_position(self, position):
        """
        Set the position of the car.
        :param position: tuple with the position of the car. tuple must have the form (x, y)
        """
        self.actual_coordinates = (position[0], position[1], self.get_direction(), self.get_lane())

    def get_rect(self):
        """
        Returns the rectangle which represents the car.
        :return: rectangle of the car
        """
        return self.screen_car

    def get_speed(self):
        """
        returns the speed of the car.
        :return: absolute speed of the car.
        """
        return self.absolute_speed

    def get_direction(self):
        """
        Returns the direction of the car. It is in radians.
        :return: direction value of the car in radians.
        """
        return self.actual_coordinates[2]

    def set_direction(self, new_direction):
        """
        Sets the new direction of a car.
        :param new_direction: new direction of a car.
        """
        self.actual_coordinates = (
            self.get_x_position(), self.get_y_position(), new_direction, self.get_lane())

    def set_speed(self, new_speed):
        """
        Sets the speed of the car. No restrictions exists.
        :param new_speed: new speed of the car.
        """
        self.absolute_speed = new_speed

    def set_controller(self, controller):
        """
        Set the controller of the car.
        :param controller: new controller of the car.
        """
        self.controller = controller

    def get_controller(self):
        """
        Get the controller of the car.
        :return: controller of the car
        """
        return self.controller

    def set_following_car_message(self, message):
        """
        Sets the message of the car.
        :param message: new message.
        """
        self.following_car_counter = 4
        self.following_car_message = message

    def get_following_car_message(self):
        """
        Returns the actual stored message of the following car.
        :return: Stored message of following car.
        """
        return self.following_car_message

    def get_name(self):
        """
        Returns the name which identifies the car.
        :return: name of the car.
        """
        return self.name

    def get_lane(self):
        """
        Return the lane in which the cart started
        :return: int of lane
        """
        return self.actual_coordinates[3]

    def set_lane(self, new_lane):
        """
        Sets the lane of a car.
        :param new_lane: new lane of a car.
        """
        self.actual_coordinates = (
            self.actual_coordinates[0], self.actual_coordinates[1], self.actual_coordinates[2], new_lane)

    def set_left_intersection_time(self, left_intersection_time):
        """
        Set the left_intersection_time to this time. Time stored in seconds.
        :param left_intersection_time: <int> number of the counter.
        """
        self.left_intersection_time = left_intersection_time

    def set_creation_time(self, creation_time=None):
        """
        Sets the creation time of a car. Used for simulations with car list.
        :param creation_time: time of "creation" of the car. If none passed, time at which the function was called.
        """
        if creation_time is None:
            self.creation_time = time()
        else:
            self.creation_time = creation_time

    def set_old(self):
        """
        Sets the new_car variable to False
        """
        self.new_car = False

    def get_info_message(self):
        """
        Creates a message object with the information of this car and returns it
        :return: a Message object.
        """
        return Message(self)

    def get_creation_time(self):
        """
        Getter for creation time.
        :return: Creation time of the car.
        """
        return self.creation_time

    def get_left_intersection_time(self):
        """
        Getter for the time at which the car left the intersection. -1 if it hasn't left yet.
        :return: Time at which the car left the intersection.
        """
        return self.left_intersection_time if self.left_intersection_time is not None else -1

    def get_following_car_name(self):
        """
        Returns the name of the car that this car is following. If the name is -1, this car is not following another.
        :return: <int> name of the car that this one is following
        """
        return self.get_following_car_message().get_name()

    def get_following(self):
        """
        Returns the follow variable.
        :return: True if the car is following other. False otherwise.
        """
        return self.following

    def get_car_length(self):
        """
        Get the length of the car based on it's screen representation.
        :return: <int> length of a car.
        """
        return abs((self.get_rect().right - self.get_rect().left) * sin(self.get_direction() * pi / 180) +
                   (self.get_rect().top - self.get_rect().bottom) * cos(self.get_direction() * pi / 180))

    def get_actual_coordinates(self):
        """
        Return the tuple containing the actual coordinates fo a car.
        :return: (<int>, <int>, <int>, <int>) actual coordinates of a car.
        """
        return self.actual_coordinates

    def get_origin_coordinates(self):
        """
        Return the tuple containing the origin coordinates fo a car.
        :return: (<int>, <int>, <int>, <int>) origin coordinates of a car.
        """
        return self.initial_coordinates

    def get_control_law_value(self):
        """
        Returns the last value of the control law value.
        :return: <int> control law value
        """
        return self.control_law_value

    def set_control_law_value(self, new_control_law):
        """
        Sets the value of the control law value
        :param new_control_law: <int> new value of control law value
        """
        self.control_law_value = new_control_law

    def get_last_virtual_distance(self):
        """
        Gets the value of the last virtual distance recorded
        :return: <float> last virtual distance
        """
        return self.last_virtual_distance

    def set_last_virtual_distance(self, new_virtual_distance):
        """
        Sets the last virtual distance
        :param new_virtual_distance: <float> new value of the last virtual distance
        """
        self.last_virtual_distance = new_virtual_distance

    def get_maximum_acceleration(self):
        """
        Return the maximum acceleration of a car
        :return: <float> maximum acceleration
        """
        return self.maximum_acceleration

    def get_minimum_acceleration(self):
        """
        Return the maximum acceleration of a car
        :return: <float> maximum acceleration
        """
        return self.minimum_acceleration

    def get_intention(self):
        """
        Return the intention of path of the car. "s" for straightforward, "r" for a right turn, "l" for a left turn.
        :return: <string> intention of the car
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

    def set_intention(self, intention):
        """
        Set the intention of the car. Function created for test issues
        :param intention: new intention of the car
        """
        self.intention = intention

    def get_caravan_depth(self):
        """
        Get the depth of the car in the virtual caravan. Base case the car is at the top and it's depth is 0. The other
        cases it's the following car depth plus 1.
        :return: <int> depth of the car at the caravan.
        """
        if self.get_following():
            return self.get_following_car_message().get_caravan_depth() + 1
        return 0

    def set_caravan_depth(self, new_depth):
        """
        Sets the depth of the caravan of this car. Function created for the supervisory level.
        :param new_depth: new depth of the car at the caravan.
        """
        self.get_following_car_message().set_depth(new_depth)

    def get_initial_speed(self):
        """
        Returns the initial speed of the car (his speed at the creation time).
        :return: <int> initial speed
        """
        return self.initial_speed

    def set_origin_coordinates(self, lane):
        """
        Sets the original coordinates of a car by it's lane.
        :param lane: lane at which the car was created
        """
        initial_positions = [(435, 760, 0, 0), (760, 345, 90, 1), (345, 10, 180, 2), (10, 435, 270, 3)]
        self.set_origin_x_position(initial_positions[lane][0])
        self.set_origin_y_position(initial_positions[lane][1])
        self.set_origin_direction(initial_positions[lane][2])

    def set_origin_x_position(self, new_x):
        """
        Sets the initial x position of a car
        :param new_x: new x initial position
        """
        self.initial_coordinates = (
            new_x, self.get_origin_y_position(), self.get_origin_direction(), self.get_lane())

    def set_origin_y_position(self, new_y):
        """
        Sets the initial y position of a car
        :param new_y: new y initial position
        """
        self.initial_coordinates = (
            self.get_origin_x_position(), new_y, self.get_origin_direction(), self.get_lane())

    def set_origin_direction(self, new_direction):
        """
        Sets the initial x position of a car
        :param new_direction: new initial direction
        """
        self.initial_coordinates = (
            self.get_origin_x_position(), self.get_origin_y_position(), new_direction, self.get_lane())

    def get_cars_at_intersection(self):
        """
        Returns the list of cars present at the intersection
        :return: list of cars
        """
        return self.cars_at_intersection

    def set_cars_at_intersection(self, cars_at_intersection):
        """
        Sets the list of cars at intersection to be the new list.
        :param cars_at_intersection: new list of cars at the intersection
        """
        for car_name in cars_at_intersection:
            self.cars_at_intersection[car_name] = cars_at_intersection[car_name]

    def get_new_messages(self):
        """
        Gets the new messages generated by this car.
        :return: <list of Messages>
        """
        return self.new_messages

    def set_new_messages(self, new_messages_list):
        """
        Sets the new messages.
        :param new_messages_list: <list of Messages>
        """
        self.new_messages = new_messages_list

    def get_new_supervisor_name(self):
        """
        Returns the name of the car that is the objective to be the new supervisor.
        :return: <int> name of the car that will be the new supervisor.
        """
        return self.new_supervisor_name

    def get_log_messages(self):
        """
        Getter for log messages.
        :return: <message list> list of Messages.
        """
        return self.log_messages

    def set_log_messages(self, log_messages):
        """
        Sets the log messages.
        :param log_messages:  <list of Messages> messages to set.
        """
        self.log_messages = log_messages

    def set_registered_caravan_depth(self, depth):
        """
        Set registered caravan depth
        :param depth: new depth of the car at the virtual caravan.
        """
        self.registered_caravan_depth = depth

    def get_registered_caravan_depth(self):
        """
        Gets the registered depth of this car at the virtual caravan.
        :return: <int>
        """
        return self.registered_caravan_depth

    def get_left_intersection_messages(self):
        """
        Generates and return a LeftIntersectionMessage.
        :return: <list of Messages>
        """
        return LeftIntersectionMessage(self)

    def get_transmitter_receiver_dict(self):
        """
        Returns the dict with the information of transmitter and receivers
        :return: <dict>
        """
        return self.transmitter_receiver_dict

    def set_transmitter_receiver_dict(self, transmitter_receiver_dict):
        """
        Set the transmitter to receiver dict.
        :param transmitter_receiver_dict: dict to set
        :return: None
        """
        self.transmitter_receiver_dict = transmitter_receiver_dict

    def get_new_cars_at_intersection(self):
        return self.new_cars_at_intersection_counter


class SupervisorCar(Car):
    """
    SupervisorCar class with the methods of the supervisor.
    """

    def update(self):
        super(SupervisorCar, self).update()
        deleted_cars = []
        for key in self.update_cars_at_intersection_counter:
            self.update_cars_at_intersection_counter[key] -= 1
            if self.update_cars_at_intersection_counter[key] == 0:
                deleted_cars.append(key)
                del self.cars_at_intersection[key]
        for car_name in deleted_cars:
            del self.update_cars_at_intersection_counter[car_name]

    def supervisor_level(self, new_car, attack=False):
        """
        Function that emulates the functioning of the supervisor level of the T-intersection coordination algorithm in a
        distributed way.
        As the original supervisor level, check if a new car needs to follow and "old" car at the intersection, but it
        works with messages (received and sent info).
        :param attack: if true, all cars will be set default controller, driving at maximum speed.
        :param new_car: information of the new car at the intersection
        """
        log_string = {"coordinated_car": new_car}
        if not attack:
            old_cars = self.get_cars_at_intersection().values()
            old_cars.sort(key=lambda car: car.get_name(), reverse=True)
            old_cars.sort(key=lambda car: car.get_caravan_depth(), reverse=True)
            log_string["old_cars"] = old_cars
            following_car_message = None
            for old_car in old_cars:
                if new_car.cross_path(old_car.get_lane(), old_car.get_intention()) and \
                        new_car.get_name() != old_car.get_name():
                    log_string["selected_car"] = old_car
                    self.get_log_messages().append(log_string)
                    if self.supervisor_lies:
                        bad_follower = old_cars[random.randint(0, len(old_cars)-1)]
                        following_car_message = FollowingCarMessage(bad_follower, new_car.get_name())
                    else:
                        following_car_message = FollowingCarMessage(old_car, new_car.get_name())
                    new_car.start_following(following_car_message)
                    self.get_new_messages().append(following_car_message)
                    break
            if not new_car.get_following():
                following_car_message = FollowingCarMessage(None, new_car.get_name())
                self.get_new_messages().append(following_car_message)
            return following_car_message

    def add_new_car(self, new_car_message):
        """
        Overwrites add_new_car of Car class to execute supervisor level
        :param new_car_message:
        :return:
        """
        # recreate car
        new_car = Car(new_car_message.get_name(), lane=new_car_message.get_lane(),
                      intention=new_car_message.get_intention(), creation_time=new_car_message.get_creation_time())
        # execute supervisor coordination
        self.supervisor_level(new_car, self.attack_supervisor)
        # store car
        self.get_cars_at_intersection()[new_car.get_name()] = new_car
        self.transmitter_receiver_dict[new_car.get_name()] = []
        self.update_cars_at_intersection_counter[new_car.get_name()] = 4
        if new_car.get_following_car_name() in self.transmitter_receiver_dict:
            self.transmitter_receiver_dict[new_car.get_following_car_name()].append(new_car.get_name())
        # select second at charge (or its alternate meanwhile a better second at charge appears)
        if not self.has_second_at_charge and new_car.get_name() != self.get_name():
            if self.get_caravan_depth() < new_car.get_caravan_depth():
                self.has_second_at_charge = True
                self.has_alternate_second_at_charge = True
                self.get_new_messages().append(SecondAtChargeMessage(self, new_car.get_name()))
            if not self.has_alternate_second_at_charge:
                self.has_alternate_second_at_charge = True
                self.get_new_messages().append(SecondAtChargeMessage(self, new_car.get_name()))

    def get_left_intersection_messages(self):
        """
        Besides of the LeftIntersectionMessage, a Supervisor also generates a SupervisorLeftIntersection message
        :return: <list of messages>
        """
        if not self.attack_supervisor:
            return SupervisorLeftIntersectionMessage(self)

    @property
    def is_supervisor(self):
        """
        Returns True a SupervisorCar is a supervisor
        :return: <boolean> True
        """
        return not self.attack_supervisor


class InfrastructureCar(SupervisorCar):
    """
    InfrastructureCar that do the same as the supervisor, but doesn't moves or generates updates info.
    """

    def update(self):
        """
        An infrastructure car doesn't move, so pass
        """
        pass


class SecondAtChargeCar(SupervisorCar):
    """
    SecondAtChargeCar in charge of supplying SupervisorCar chores while assigning a new one.
    """

    def supervisor_level(self, new_car, attack=False):
        """
        Function that emulates the functioning of the supervisor level of the T-intersection coordination algorithm in a
        distributed way.
        As the original supervisor level, check if a new car needs to follow and "old" car at the intersection, but it
        works with messages (received and sent info).
        For the SecondAtChargeCar class, this will be executed only if a car arrives the intersection after a
        SupervisorCar left the intersection and before the SecondAtChargeCar assigns a new Supervisor
        :param attack: if true, all cars will be set default controller, driving at maximum speed.
        :param new_car: information of the new car at the intersection
        """
        self.new_supervisor_name = new_car.get_name()
        # if self.get_supervisor_left_intersection():
        following_car_message = super(SecondAtChargeCar, self).supervisor_level(new_car, attack)
        self.get_new_messages().remove(following_car_message)
        self.coordination_messages[following_car_message.get_following_car_name()] = following_car_message

    def update(self):
        """
        Update the car.Besides of moving it and generate the InformationMessage, the SecondAtCharge will check if the
        supervisor is still active and, if it isn't, will create a NewSupervisorMessage for the new supervisor.
        """
        super(SecondAtChargeCar, self).update()
        new_cars_at_intersection = self.get_new_cars_at_intersection()
        if self.get_supervisor_left_intersection():
            for car_name in new_cars_at_intersection:
                self.supervisor_level(self.get_cars_at_intersection()[car_name])
            if self.new_supervisor_name != -1:
                self.get_new_messages().append(NewSupervisorMessage(self))
                self.set_supervisor_left_intersection(False)
                self.new_supervisor_name = -1
        if self.supervisor_counter == 0:
            self.set_supervisor_left_intersection(True)
        self.supervisor_counter -= 1

    def start_following(self, message):
        super(SecondAtChargeCar, self).start_following(message)
        if message.get_following_car_name() in self.get_new_cars_at_intersection():
            self.get_new_cars_at_intersection().remove(message.get_following_car_name())
        if message.get_following_car_name() in self.coordination_messages:
            if message.get_name() != self.coordination_messages[message.get_following_car_name()].get_name():
                print "Coordinador miente"
            else:
                print "coordinador no miente"
            del self.coordination_messages[message.get_following_car_name()]

    def add_new_car(self, new_car_message):
        """
        Overwrites add_new_car of Car class to execute supervisor level
        :param new_car_message:
        :return:
        """
        new_car = Car(new_car_message.get_name(), lane=new_car_message.get_lane(),
                      intention=new_car_message.get_intention(), creation_time=new_car_message.get_creation_time())
        self.supervisor_level(new_car)
        self.get_cars_at_intersection()[new_car.get_name()] = new_car
        self.get_new_cars_at_intersection().append(new_car.get_name())

    def reset_supervisor_counter(self):
        self.supervisor_counter = 4

    def get_supervisor_left_intersection(self):
        """
        Gets the variable to know if the supervisor left the intersection.
        :return: <boolean>
        """
        return self.supervisor_left_intersection

    def set_supervisor_left_intersection(self, left_intersection):
        """
        Sets the supervisor_left_intersection_variable.
        :param left_intersection: <boolean>
        """
        self.supervisor_left_intersection = left_intersection

    @property
    def is_supervisor(self):
        """
        Returns True a SupervisorCar is a supervisor
        :return: <boolean> True
        """
        return False

    @property
    def is_second_at_charge(self):
        """
        Returns True. SecondAtChargeCar is the second at charge.
        :return: <boolean> True
        """
        return True
