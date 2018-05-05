import pygame
import os
from auxiliary_functions.auxiliary_functions import display_info_on_car, \
    show_caravan, continue_simulation, init_graphic_environment
from log_files_process import generate_left_intersection_cars_from_file, \
    generate_collision_cars_from_file


def see_collision(log):
    """
    Function that generates all the information to see all the collisions of a
    simulation. To see the next collision image, press a key.
    :param log: log name of the simulation to see.
    """
    log_directory = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"
    all_cars_file = open(log_directory + "left_intersection" + log + ".log")
    collisions_file = open(log_directory + "collisions" + log + ".log")

    print "Creating cars"
    all_cars = generate_left_intersection_cars_from_file(all_cars_file)
    print "Finished creating cars. Loading collisions."
    collisions_cars, collided_cars = generate_collision_cars_from_file(
        collisions_file, all_cars
    )
    print "Finished"

    cars_at_creation_of_collided_car = {}
    all_cars_values = all_cars.values()
    for collided_car in collided_cars.values():
        cars_at_creation_of_collided_car[collided_car[1].get_name()] = []
        for car in all_cars_values:
            if (car.get_name() <= collided_car[1].get_name() and
                    car.get_left_intersection_time() >
                    collided_car[1].get_creation_time()):
                cars_at_creation_of_collided_car[
                    collided_car[1].get_name()].append(car)
    screen, background, intersection_background, font = (
        init_graphic_environment(1468, 768)
    )
    actual_collision = 0
    false_positive_counter = 0
    false_positive = False

    while actual_collision < len(collisions_cars.keys()):
        screen.blit(background, (0, 0))
        screen.blit(intersection_background, (0, 0))
        actual_collision_cars = sorted(
            collisions_cars[actual_collision].values(),
            key=lambda car: car.get_name()
        )
        for car in actual_collision_cars:
            car.new_image()
            screen.blit(car.rotated_image, car.screen_car)
            display_info_on_car(car, screen, font, 1)
        show_caravan(
            collisions_cars[actual_collision].values(),
            screen,
            font,
            collided_cars[actual_collision],
            screen.get_width(),
            1
        )
        pygame.display.update(screen.get_rect())
        false_positive = (
            collided_cars[actual_collision][0].get_intention() == "r" and
            collided_cars[actual_collision][1].get_intention() == "l" or
            collided_cars[actual_collision][0].get_intention() == "l" and
            collided_cars[actual_collision][1].get_intention() == "r"
        ) and abs(
            (
                collided_cars[actual_collision][0].get_lane() -
                collided_cars[actual_collision][1].get_lane()
            ) % 2 == 1
        )
        if continue_simulation(pygame.event.get()):
            if false_positive:
                false_positive_counter += 1
            print (
                "Actual false_positive: " + str(false_positive_counter) +
                ".\nActual collisions: " + str(actual_collision + 1) +
                "\nActual aprox ticks: " + str(
                    collided_cars[actual_collision][0].get_creation_time()
                ) + "\nActual car: " +
                str(collided_cars[actual_collision][0].get_name())
            )
            collisions_cars[actual_collision] = None
            actual_collision += 1
    print "Final number of false_positive: " + str(false_positive_counter)
    screen.blit(background, (0, 0))
    screen.blit(
        font.render("No hay mas colisiones para analizar", True, (0, 0, 0)),
        (screen.get_width() / 3, screen.get_height() / 2)
    )
    pygame.display.update(screen.get_rect())
    pygame.time.wait(2000)


see_collision("_new_speed_test_distance_11_speed_20")
