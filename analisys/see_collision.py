import pygame
import os
from auxiliary_functions.auxiliary_functions import display_info_on_car, show_caravan, continue_simulation, \
    init_graphic_environment
from log_files_process import generate_left_intersection_cars_from_file, generate_collision_cars_from_file


def see_collision(log):
    """
    Function that generates all the information to see all the collisions of a simulation. To see the next collision
    image, press a key.
    :param log: log name of the simulation to see.
    """
    log_directory = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"
    all_cars_file = open(log_directory + "left_intersection" + log + ".log")
    collisions_file = open(log_directory + "collisions" + log + ".log")

    all_cars = generate_left_intersection_cars_from_file(all_cars_file)
    collisions_cars, collided_cars = generate_collision_cars_from_file(collisions_file, all_cars)

    screen, background, intersection_background, font = init_graphic_environment(1468, 768)

    actual_collision = 0

    while actual_collision < len(collisions_cars.keys()):
        screen.blit(background, (0, 0))
        screen.blit(intersection_background, (0, 0))
        for car in collisions_cars[actual_collision].values():
            car.new_image()
            screen.blit(car.rotated_image, car.screen_car)
            display_info_on_car(car, screen, font, "name", "following")
        show_caravan(collisions_cars[actual_collision].values(), screen, font, collided_cars[actual_collision],
                     screen.get_width())
        pygame.display.update(screen.get_rect())
        if not continue_simulation(pygame.event.get()):
            actual_collision += 1
