from pygame.locals import *
import pygame
from models.car import Car
from random import randint
import logging


white = (255, 255, 255)  # RGB white color representation
black = (0, 0, 0)  # RGB black color representation
initial_positions = [(415, 760, 0, 1), (760, 365, 90, 2), (365, 10, 180, 3), (10, 415, 270, 4)]  # initial positions
# of the cars per lane with the direction they should face..


def distance_to_center(**kwargs):
    """
    Returns the distance to the center of the indicated object. the car must be passed in the "car" param  and the
    message in the message param.

    Example: car: example_car = Car()
                  distance_to_center(car=example_car)
    Example: message: example_message = Message()
                  distance_to_center(message=example_message)
    :param kwargs: car or message param. If both passed, it will return the distance to the center of the car.
    :return: distance to the center of the car or of the information of a car stored in a message.
    """
    if 'car' in kwargs:
        return kwargs['car'].distance_to_center()
    elif 'message' in kwargs:
        return kwargs['message'].distance_to_center()


def reposition_car_in_screen(screen, car):
    """
    Function to graphically reposition a car in the screen so it doesnt get lost.
    :param screen: screen in which the car is being displayed.
    :param car: car to display.
    """
    old_position = car.get_position()
    new_position = old_position
    if old_position[0] > (screen.get_rect().x + screen.get_rect().w):
        new_position = (0, old_position[1])
    elif old_position[0] < screen.get_rect().x:
        new_position = (screen.get_rect().x + screen.get_rect().w, old_position[1])
    if old_position[1] > (screen.get_rect().y + screen.get_rect().h):
        new_position = (old_position[0], 0)
    elif old_position[1] < screen.get_rect().y:
        new_position = (old_position[0], screen.get_rect().y + screen.get_rect().h)
    car.set_position(new_position)


def check_close_application(user_input):
    """
    Check if the application must be close depending on the user input (for the graphical environment).
    Pressing the x of a pygame window or the escape key will close the window and end the simulation.
    :param user_input: pygame input of the user.
    :return: Flase if the simulation must end. True if it must continue.
    """
    for event in user_input:
        if event.type == pygame.QUIT:
            return False
        if hasattr(event, 'key'):
            if event.key == K_ESCAPE:
                return False
    return True


def random_car(name, max_speed, **kwargs):
    """
    Generates a random car with the given name. The max speed is used to give an speed not giver than the maximum a the
    car. the lane can be passed in kwargs value if the lane wants to be specified.
    Example: "random_car(4,20,lane=3)"
    :param name: name of the car.
    :param max_speed: maximum speed of the car.
    :param kwargs: the lane can be passed in this argument in the "lane" argument.
    :return: a Car object.
    """
    if "lane" in kwargs:
        pos_x, pos_y, direction, lane = initial_positions[kwargs["lane"]-1]
    else:
        pos_x, pos_y, direction, lane = initial_positions[randint(0, len(initial_positions) - 1)]
    initial_speed = randint(0, max_speed)
    return Car(str(name), pos_x, pos_y, direction=direction, lane=lane, absolute_speed=initial_speed)


def colliding_cars(car_list):
    """
    Check if any two cars of the car_list have collided.
    :param car_list: lists of car.
    :return: tuple with the colliding cars and True, if the cars collided. None and false otherwise.
    """
    for i in range(len(car_list)):
        for j in range(i+1,len(car_list)):
            if car_list[i].screen_car.colliderect(car_list[j].screen_car):
                return (car_list[i], car_list[j]), True
    return None, False


def display_info_on_car(car, display, letter, *args):
    """
    Displays some information of a car on top of it. The Car, display to draw on and the font to write. In args params
    can be passed the "name", "speed" and "following" param depending of which want to be displayed.
    "name" will be displayed at the center, speed to the left and following car to the right.
    :param car: Car to display information on.
    :param display: display in which the car will be drawn.
    :param letter: font to write the information.
    :param args: optional arguments to decide which information will be displayed.
    """
    x, y = car.get_position()
    if "name" in args:
        display.blit(letter.render(car.name, True, black), (x, y))
    if "speed" in args:
        display.blit(letter.render(str(car.get_speed()), True, black), (x - 30, y))
    if "following" in args and car.get_message() is not None:
        display.blit(letter.render(str(car.get_message().car_name), True, black), (x + 30, y))


def random_cars(lanes, name, max_speed):
    """
    Create x number of new random cars, with x being the length of the lanes list. The cars will be created on the
    specified lanes, the names will start at the name param (must be integer), and the max_speed must be passed.
    :param lanes: lanes in which the cars will be created.
    :param name: name of the cars. It has the form (name + index(lane, lanes)).
    :param max_speed: max speed of the cars
    :return: list with random cars.
    """
    new_cars = []
    for i in range(len(lanes)):
        new_cars.append(random_car(name+i, max_speed, lane=lanes[i]))
    return new_cars


def create_car_from_json(json_car):
    """
    Function that creates a car from a json representation of a car.
    The json must have the form "{'car_name': <int>, 'following': <int>, 'lane': <int>, 'speed': <float>, 'creation_time': <float>}
    :param json_car: json representation of a car
    :return: a new car with the json_car information
    """
    pos_x, pos_y, direction, lane = initial_positions[json_car["lane"]-1]
    car = Car(json_car["car_name"], pos_x, pos_y, direction=direction, absolute_speed=json_car["speed"], lane=lane,
              creation_time=json_car["creation_time"], left_intersection_time=json_car["left_intersection_time"])
    return car


def setup_logger(logger_name, log_file, level=logging.DEBUG):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('{"time":"%(asctime)s", "message":%(message)s},')
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(file_handler)
    l.addHandler(stream_handler)