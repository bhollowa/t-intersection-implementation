import os
from math import pi, cos, sin, atan
from pygame import image, transform
from time import time
from car_controllers import default_controller, follower_controller
from models.message import Message, InfoMessage, FollowingCarMessage

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
        if creation_time is None:
            self.creation_time = time()
        else:
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
        self.follower_cars = []  # all the followers of the car will be here, so this car can send it information
        # to the others
        self.cars_at_intersection = []
        self.new_messages = []
        self.following = False  # True if the car is following some other car
        self.active_supervisory = False
        self.new_car = True
        self.control_law_value = 0
        self.last_virtual_distance = 0
        self.new_supervisor_name = -1

    def __str__(self):
        """
        String representation of the car. Adapted to output actual state of the car to a log file.
        Example: "Car: 48 Speed: 19.975 Following: 47" if car is following other car,
        Example: "Car: 48 Speed: 19.975" else.
        :return: String representation of the car.
        """
        return "Car " + str(self.get_name()) + " lane " + str(self.get_lane()) + " intention " + self.get_intention() \
               + " depth " + str(self.get_caravan_depth()) + " following " \
               + str(self.get_following_car_message().get_name())

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
        if self.get_intention() is "s":
            virtual_distance_value = self.get_virtual_x_position()
        elif self.get_intention() is "r":
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
        Sets the variable follow to True to indicate that this car has started following another car.
        """
        if self.get_name() == message.get_following_car_name():
            self.set_following_car_message(message)
            self.set_controller(follower_controller.follower_controller)
            self.set_following(True)
        for car in self.get_cars_at_intersection():
            if car.get_name() == message.get_following_car_name():
                car.set_following_car_message(message)
                car.set_controller(follower_controller.follower_controller)
                car.set_following(True)
                break

    def set_following(self, following):
        self.following = following

    def new_image(self):
        """
        Creates the image representation of a car, with his rotated image and his screen representation (with the rect).
        """
        self.image = image.load(images_directory + "car.png")
        self.rotated_image = transform.rotate(self.image, self.get_direction())  # image of the car rotated
        self.rotated_image = transform.scale(self.rotated_image, (  # reduction of the size of the image
            int(self.rotated_image.get_rect().w * self.get_image_scale_rate()),
            int(self.rotated_image.get_rect().h * self.get_image_scale_rate())))
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

    def get_followers(self):
        """
        Returns all the car that are following this car.
        :return: followers of this car.
        """
        return self.follower_cars

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

    def set_left_intersection_time(self):
        """
        Set the left_intersection_time to this time. Time stored in seconds.
        """
        self.left_intersection_time = time()

    def set_creation_time(self, creation_time=None):
        """
        Sets the creation time of a car. Used for simulations with car list.
        :param creation_time: time of "creation" of the car. If none passed, time at which the function was called.
        """
        if creation_time is None:
            self.creation_time = time()
        else:
            self.creation_time = creation_time

    def set_active_supervisory(self, active):
        """
        Sets the active_supervisory to active.
        :param active: True to set this car as the supervisor. False otherwise.
        """
        self.active_supervisory = active

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

    def get_active_supervisor(self):
        """
        Check if this has it's supervisor level active.
        :return: <boolean>True if this car is running the supervisro level. False otherwise.
        """
        return self.active_supervisory

    def is_new(self):
        """
        Function to check if this car is new in the intersection.
        :return: <boolean> True if the car is new (and haven't been assigned a following car). False otherwise.
        """
        return self.new_car

    def get_following(self):
        """
        Returns the follow variable.
        :return: True if the car is following other. False otherwise.
        """
        return self.following

    def add_follower(self, car):
        """
        Adds a follower to the list of followers of the car.
        :param car: new follower car.
        """
        self.follower_cars.append(car)

    def get_car_length(self):
        """
        Get the length of the car based on it's screen representation.
        :return: <int> length of a car.
        """
        return abs((self.get_rect().right - self.get_rect().left) * sin(self.get_direction() * pi / 180) + (
            self.get_rect().top - self.get_rect().bottom) * cos(self.get_direction() * pi / 180))

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

    def reset(self):
        """
        Sets all the attributes of the car as if it just arrived at the intersection.
        """
        initial_positions = [(435, 760, 0, 0), (760, 345, 90, 1), (345, 10, 180, 2), (10, 435, 270, 3)]
        self.set_x_position(initial_positions[self.get_lane()][0])
        self.set_y_position(initial_positions[self.get_lane()][1])
        self.set_direction(initial_positions[self.get_lane()][2])
        self.set_origin_x_position(initial_positions[self.get_lane()][0])
        self.set_origin_y_position(initial_positions[self.get_lane()][1])
        self.set_origin_direction(initial_positions[self.get_lane()][2])

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

    def add_new_car(self, new_car_message):
        """
        Adds a car to the list of cars present at the intersection.
        :return:
        """
        new_car = Car(new_car_message.get_name(), lane=new_car_message.get_lane(),
                      intention=new_car_message.get_intention())
        if self.get_active_supervisor():
            self.supervisor_level(new_car)
        self.get_cars_at_intersection().append(new_car)

    def delete_car(self, left_intersection_message):
        """
        Deletes a car from the list of cars at the intersection
        :param left_intersection_message: message of the car that left the intersection
        """
        cars_at_intersection = self.get_cars_at_intersection()
        cars_at_intersection.sort(key=lambda car: car.get_name())
        cars_to_remove = []
        # update car information
        for car in cars_at_intersection:
            following_car_name = car.get_following_car_message().get_name()
            if car.get_name() == left_intersection_message.get_name():
                cars_to_remove.append(car)
            if left_intersection_message.get_name() == following_car_name:
                car.set_controller(default_controller.default_controller)
                car.set_following(False)
        # remove cars that left
        for car in cars_to_remove:
            cars_at_intersection.remove(car)
        # update following car information
        cars_at_intersection_dict = {car.get_name(): car for car in cars_at_intersection}
        for car in cars_at_intersection:
            following_car_name = car.get_following_car_message().get_name()
            if following_car_name in cars_at_intersection_dict.keys():
                car.set_following_car_message(InfoMessage(cars_at_intersection_dict[following_car_name]))

        if left_intersection_message.get_name() == self.get_following_car_message().get_name():
            self.set_controller(default_controller.default_controller)
            self.set_following(False)

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
        self.cars_at_intersection = cars_at_intersection

    def make_supervisor(self, supervisor_left_message):
        """
        Makes this car the supervisor of the intersection.
        :param supervisor_left_message: message with the information needed for this car to be supervisor.
        """
        self.set_active_supervisory(True)
        self.set_cars_at_intersection(supervisor_left_message.get_cars_at_intersection())

    def get_new_messages(self):
        return self.new_messages

    def set_new_messages(self, new_messages_list):
        self.new_messages = new_messages_list

    def supervisor_level(self, new_car, attack=False):
        """
        Function that emulates the functioning of the supervisor level of the T-intersection coordination algorithm in a
        distributed way.
        As the original supervisor level, check if a new car needs to follow and "old" car at the intersection, but it
        works with messages (received and sent info).
        :param attack: if true, all cars will be set default controller, driving at maximum speed.
        :param new_car: information of the new car at the intersection
        :return
        """
        self.new_supervisor_name = new_car.get_name()
        if not attack:
            old_cars = self.get_cars_at_intersection()
            old_cars.sort(key=lambda car: car.get_name(), reverse=True)
            old_cars.sort(key=lambda car: car.get_caravan_depth(), reverse=True)
            for old_car in old_cars:
                if new_car.cross_path(old_car.get_lane(), old_car.get_intention()):
                    new_car.start_following(FollowingCarMessage(old_car, new_car.get_name()))
                    self.get_new_messages().append(FollowingCarMessage(old_car, new_car.get_name()))
                    break

    def get_new_supervisor_name(self):
        """
        Returns the name of the car that is the objective to be the new supervisor.
        :return: <int> name of the car that will be the new supervisor.
        """
        return self.new_supervisor_name
