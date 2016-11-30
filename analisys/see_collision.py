import pygame
import os
from auxiliary_functions.auxiliary_functions import display_info_on_car, show_caravan, continue_simulation, \
    init_graphic_environment
from log_files_process import generate_left_intersection_cars_from_file, generate_collision_cars_from_file, \
    generate_coordination_info_from_file


def see_collision(log):
    """
    Function that generates all the information to see all the collisions of a simulation. To see the next collision
    image, press a key.
    :param log: log name of the simulation to see.
    """
    log_directory = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"
    all_cars_file = open(log_directory + "left_intersection" + log + ".log")
    collisions_file = open(log_directory + "collisions" + log + ".log")
    coordination_file = open(log_directory + "coordination" + log + ".log")

    all_cars = generate_left_intersection_cars_from_file(all_cars_file)
    collisions_cars, collided_cars = generate_collision_cars_from_file(collisions_file, all_cars)
    coordination_info = generate_coordination_info_from_file(coordination_file)
    cars_at_creation_of_collided_car = {}
    all_cars_values = all_cars.values()
    for collided_car in collided_cars.values():
        cars_at_creation_of_collided_car[collided_car[1].get_name()] = []
        for car in all_cars_values:
            if car.get_name() <= collided_car[1].get_name() and car.get_left_intersection_time() > collided_car[1].get_creation_time():
                cars_at_creation_of_collided_car[collided_car[1].get_name()].append(car)
    screen, background, intersection_background, font = init_graphic_environment(1468, 768)
    actual_collision = 0
    printed = False
    while actual_collision < len(collisions_cars.keys()):
        screen.blit(background, (0, 0))
        screen.blit(intersection_background, (0, 0))
        actual_collision_cars = sorted(collisions_cars[actual_collision].values(), key=lambda car: car.get_name())
        first_car_name = actual_collision_cars[0].get_name()

        if not printed:
            print "Vehiculos colisionados: " + str(collided_cars[actual_collision][1].get_name()) + " y " + str(
                collided_cars[actual_collision][0].get_name())
            print "Orden de vehiculos en coordinacion:\n"
            for coso in coordination_info[collided_cars[actual_collision][1].get_name()]:
                print "Car " + str(coso.get_name() - first_car_name + 1) + " lane " + str(
                    coso.get_lane()) + " intention " + coso.get_intention() + " depth " + str(
                    coso.get_registered_caravan_depth()) + " following " + str(
                    coso.get_following_car_message().get_name() - first_car_name + 1) + " supervisor " + str(
                    coso.is_supervisor())
            print "Vehiculos al momento de la creacion:"
            for coso in cars_at_creation_of_collided_car[collided_cars[actual_collision][1].get_name()]:
                print "Car " + str(coso.get_name() - first_car_name + 1) + " lane " + str(
                    coso.get_lane()) + " intention " + coso.get_intention() + " depth " + str(
                    coso.get_caravan_depth()) + " following " + str(
                    coso.get_following_car_message().get_name() - first_car_name + 1) + " supervisor " + str(
                    coso.is_supervisor())
            printed = True
            print "\n"

        for car in actual_collision_cars:
            car.new_image()
            screen.blit(car.rotated_image, car.screen_car)
            display_info_on_car(car, screen, font, first_car_name, "name", "following")
        show_caravan(collisions_cars[actual_collision].values(), screen, font, collided_cars[actual_collision],
                     screen.get_width(), first_car_name)
        pygame.display.update(screen.get_rect())
        if continue_simulation(pygame.event.get()):
            printed = False
            actual_collision += 1
    screen.blit(background, (0, 0))
    screen.blit(font.render("No hay mas colisiones para analizar", True, (0, 0, 0)),
                (screen.get_width() / 3, screen.get_height() / 2))
    pygame.display.update(screen.get_rect())
    pygame.time.wait(2000)
