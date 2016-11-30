from pygame.locals import *
import pygame
from models.car import Car
from random import randint
import logging
import os
from car_controllers.follower_controller import follower_controller

white = (255, 255, 255)  # RGB white color representation
black = (0, 0, 0)  # RGB black color representation
initial_positions = [(435, 760, 0, 0), (760, 345, 90, 1), (345, 10, 180, 2), (10, 435, 270, 3)]  # initial positions
# of the cars per lane with the direction they should face.
logger_directory = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"


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
    :return: False if the simulation must end. True if it must continue.
    """
    for event in user_input:
        if event.type == pygame.QUIT:
            return True
        if hasattr(event, 'key'):
            if event.type == pygame.KEYUP and event.key == K_ESCAPE:
                return True
    return False


def continue_simulation(user_input):
    """
    Check the keyboard user input to continue the simulation.
    :param user_input: user inputs of pygame
    :return: <boolean>
    """
    for event in user_input:
        if event.type == pygame.KEYUP and event.key is not K_ESCAPE:
            return True
    return False


def random_car(name, min_speed, max_speed, creation_time, number_of_lanes, **kwargs):
    """
    Generates a random car with the given name. The max speed is used to give an speed not giver than the maximum a the
    car. the lane can be passed in kwargs value if the lane wants to be specified.
    Example: "random_car(4,20,lane=3)"
    :param number_of_lanes: number of lanes at the simulation
    :param creation_time: creation car of the car
    :param name: name of the car.
    :param min_speed: minimum speed of a car.
    :param max_speed: maximum speed of the car.
    :param kwargs: the lane can be passed in this argument in the "lane" argument.
    :return: a Car object.
    """
    if "lane" in kwargs:
        pos_x, pos_y, direction, lane = initial_positions[kwargs["lane"]]
    else:
        new_lane = randint(0, number_of_lanes - 1)
        pos_x, pos_y, direction, lane = initial_positions[new_lane]
    initial_speed = randint(min_speed, max_speed)
    if "intention" in kwargs:
        intention = kwargs["intention"]
    else:
        intention = "s"
        if number_of_lanes == 4:
            random_intention = randint(0, 2)
            if random_intention == 0:
                intention = "l"
            elif random_intention == 1:
                intention = "r"
        else:
            random_intention = randint(0, 1)
            if lane == 0:
                if random_intention == 0:
                    intention = "r"
            elif lane == 1:
                if random_intention == 0:
                    intention = "r"
                else:
                    intention = "l"
            else:
                if random_intention == 1:
                    intention = "l"
    return Car(name, pos_x, pos_y, direction=direction, lane=lane, absolute_speed=initial_speed,
               intention=intention, creation_time=creation_time)


def colliding_cars(car_list):
    """
    Check if any two cars of the car_list have collided.
    :param car_list: lists of car.
    :return: tuple with the colliding cars and True, if the cars collided. None and false otherwise.
    """
    for i in range(len(car_list)):
        for j in range(i + 1, len(car_list)):
            if car_list[i].screen_car.colliderect(car_list[j].screen_car):
                return (car_list[i], car_list[j]), True
    return None, False


def display_info_on_car(car, display, letter, normalized=1):
    """
    Displays some information of a car on top of it. The Car, display to draw on and the font to write. In args params
    can be passed the "name", "speed" and "following" param depending of which want to be displayed.
    "name" will be displayed at the center, speed to the left and following car to the right.
    :param car: Car to display information on.
    :param display: display in which the car will be drawn.
    :param letter: font to write the information.
    :param args: optional arguments to decide which information will be displayed.
    :param normalized: reduce the number of the names of the cars so they start at 1.
    """
    x, y = car.get_position()
    display.blit(letter.render(str(car.get_name() - normalized + 1), True, black), (x, y - 30))
    display.blit(letter.render(str(int(car.get_following_car_message().get_name()) - normalized + 1), True, black),
                 (x, y))


def create_car_from_json(json_car):
    """
    Function that creates a car from a json representation of a car.
    The json must have the form "{'car_name': <int>, 'following': <int>, 'lane': <int>, 'speed': <float>,
    'creation_time': <float>}
    :param json_car: json representation of a car
    :return: a new car with the json_car information
    """
    pos_x, pos_y, direction, lane = initial_positions[json_car["lane"] - 1]
    left_time = json_car["left_intersection_time"] if "left_intersection_time" in json_car else None
    car = Car(json_car["car_name"], pos_x, pos_y, direction=direction, absolute_speed=json_car["speed"], lane=lane,
              creation_time=json_car["creation_time"], left_intersection_time=left_time)
    return car


def setup_logger(logger_name, log_file, level=logging.DEBUG):
    """
    Set up the loggers of the application.
    :param logger_name:
    :param log_file:
    :param level:
    :return:
    """
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('{"time":"%(asctime)s", "message":%(message)s},')
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(file_handler)


def create_logs(log_name):
    """
    Function to create the logs of a simulation.
    :param log_name: <string> name to store the logs (to difference them with the others).
    :return: tuple with 3 logs in this order: collision, left_intersection, total_cars.
    """
    setup_logger("collision" + log_name, logger_directory + "collisions" + log_name + ".log")
    setup_logger("numbers_of_cars" + log_name, logger_directory + "total_cars" + log_name + ".log")
    setup_logger("left_intersection" + log_name, logger_directory + "left_intersection" + log_name + ".log")
    setup_logger("coordination" + log_name, logger_directory + "coordination" + log_name + ".log")
    return logging.getLogger('collision' + log_name), logging.getLogger(
        'left_intersection' + log_name), logging.getLogger('numbers_of_cars' + log_name), \
        logging.getLogger('coordination' + log_name)


def separate_new_and_old_cars(car_list):
    """
    Function to separate old from new cars. Return a tuple with 2 lists: one with new cars, one with old cars
    ordered by creation time.
    :param car_list: <list> cars at the intersection.
    :return: (<car_list>,<car_list>) Tuple of size 2 with two list: one with new cars, the other with old cars
    ordered by creation time.
    """
    new_cars = []
    old_cars = []
    for car in car_list:
        if car.is_new():
            new_cars.append(car)
        else:
            old_cars.append(car)
    old_cars.sort(key=lambda x: x.creation_time, reverse=False)
    return new_cars, old_cars


def supervisor(car_list):
    """
    Check if there is a supervisor car in the car list
    :param car_list: <list> List of cars.
    :return: <boolean> True if there is a car with active supervisor level. False otherwise.
    """
    for car in car_list:
        if car.is_supervisor:
            return True
    return False


def supervisor_message(messages):
    """
    Check if there is a SupervisorLeftIntersectionMessage in the list of messages.
    :param messages: list of messages.
    :return: <boolean>
    """
    for message in messages:
        if message.__class__.__name__ == "SupervisorLeftIntersectionMessage":
            return True
    return False


def show_caravan(cars, screen, letter, collided_cars, screen_width, normalized=1):
    """
    Function to show the virtual caravan in the graphic simulation.
    :param cars: Cars at the intersection
    :param screen: screen to draw the caravan.
    :param letter: font to write information
    :param collided_cars: information of the collided cars. None if there is no collision present.
    :param screen_width: width of the screen.
    :param normalized: reduce the number of the names of the cars so they start at 1.
    """
    size = (25, 25)
    leaders = []
    not_leaders = []
    car_surface = pygame.Surface(size)
    palette = [(0, 126, 255, 0), (255, 0, 0, 0), (0, 255, 0, 0), (255, 126, 0, 0), (255, 0, 126, 0)]
    car_surface.fill(palette[0])
    collided_car_surface = pygame.Surface(size)
    collided_car_surface.fill(palette[1])
    leader_car_surface = pygame.Surface(size)
    leader_car_surface.fill(palette[2])
    default_controller_surface = pygame.Surface((10, 10))
    default_controller_surface.fill(palette[3])
    follower_controller_surface = pygame.Surface((10, 10))
    follower_controller_surface.fill(palette[4])

    for car in cars:
        if not car.get_following_car_name() in [cars[k].get_name() for k in range(len(cars))]:
            leaders.append(car)
        else:
            not_leaders.append(car)
    leaders.sort(key=lambda real_car: real_car.get_name())
    not_leaders.sort(key=lambda real_car: real_car.get_name())
    virtual_cars = []
    for i in range(len(leaders)):
        virtual_cars.append((leaders[i], pygame.Rect((screen_width - 100, 700 * (i + 1) / (len(leaders) + 1)), size)))
    not_leaders.sort(key=lambda not_leader_car: not_leader_car.get_name())
    for i in range(len(not_leaders)):
        for car in virtual_cars:
            if car[0].get_name() == not_leaders[i].get_following_car_name():
                new_rect = pygame.Rect((car[1].left - 100, car[1].top), size)
                for virtual_car in virtual_cars:
                    if new_rect.colliderect(virtual_car[1]):
                        new_rect.top += 50
                        virtual_car[1].top -= 50
                virtual_cars.append((not_leaders[i], new_rect))
                break

    for car in virtual_cars:
        if collided_cars is not None:
            if car[0].get_name() == collided_cars[0].get_name() or car[0].get_name() == collided_cars[1].get_name():
                screen.blit(collided_car_surface, car[1])
            elif car[0].is_supervisor:
                screen.blit(leader_car_surface, car[1])
            else:
                screen.blit(car_surface, car[1])
        else:
            if car[0].is_supervisor:
                screen.blit(leader_car_surface, car[1])
            else:
                screen.blit(car_surface, car[1])
        if car[0].get_controller() == follower_controller:
            screen.blit(follower_controller_surface, car[1])
        else:
            screen.blit(default_controller_surface, car[1])
        screen.blit(letter.render(str(car[0].get_name() - normalized + 1), True, black), car[1].topleft)
        screen.blit(letter.render(str(car[0].get_caravan_depth()), True, black),
                    (car[1].topleft[0], car[1].topleft[1] - 30))
        screen.blit(letter.render(str(car[0].get_intention() + " " + str(car[0].get_lane())), True, black),
                    car[1].bottomleft)


def init_graphic_environment(screen_width, screen_height):
    """
    Initialize the graphic environment.
    :param screen_width: width of the screen.
    :param screen_height: height of the screen.
    :return: the screen, the backgrounds and the font.
    """
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
    images_directory = os.path.dirname(os.path.abspath(__file__)) + "/../images/"
    intersection_background = pygame.image.load(images_directory + "background.jpg")
    pygame.display.set_icon(intersection_background)
    screen = pygame.display.set_mode((screen_width, screen_height))
    background = pygame.Surface(screen.get_size())
    background = background.convert(background)
    background.fill((250, 250, 250))
    pygame.init()
    font = pygame.font.SysFont('Arial', 20)
    pygame.display.set_caption('Car simulation')

    return screen, background, intersection_background, font
