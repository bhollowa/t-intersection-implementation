import pygame
import os
from log_files_process import generate_left_intersection_cars_from_file, generate_collision_cars_from_file, \
    generate_coordination_info_from_file
from auxiliary_functions.auxiliary_functions import display_info_on_car, show_caravan, init_graphic_environment, \
    check_close_application, continue_simulation, colliding_cars
from models.car import Car, SupervisorCar
from models.message import NewCarMessage


def simulate_collisions(log):
    """
    Simulates all the collisions of a log. Every simulation starts paused, pressing any key but ESC will start the
    simulation. All the cars that were present when the second collided car was created will be at their positions with
    their current speeds and directions. Pressing the ESC key will jump to the next collision, or end the simulation.
    :param log: <string> Name of the log with collisions.
    """
    log_directory = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"
    all_cars_file = open(log_directory + "left_intersection" + log + ".log")
    collisions_file = open(log_directory + "collisions" + log + ".log")
    coordination_file = open(log_directory + "coordination" + log + ".log")

    all_cars = generate_left_intersection_cars_from_file(all_cars_file)
    collisions_cars, collided_cars_info = generate_collision_cars_from_file(collisions_file, all_cars)
    coordination_info = generate_coordination_info_from_file(coordination_file)

    collided_cars_info[0].sort(key=lambda this_car: this_car.get_name())

    screen, background, intersection_background, font = init_graphic_environment(1468, 768)
    full_intersection_rect = pygame.Rect(0, 0, 768, 768)

    infrastructure_supervisor = SupervisorCar(-1)
    # infrastructure_supervisor.set_active_supervisory(True)
    screen_width = 1468
    creation_dummy_cars = []
    for coordinates in [(435, 760, 0, 0), (760, 345, 90, 1), (345, 10, 180, 2), (10, 435, 270, 3)]:
        dummy_car = Car(-1, coordinates[0], coordinates[1], direction=coordinates[2], lane=coordinates[3])
        dummy_car.new_image()
        creation_dummy_cars.append(dummy_car)
    for key in collided_cars_info:
        cars = []
        messages = []
        new_messages = []
        collision_wait = True
        iteration = True

        print [collided_cars_info[key][number].get_name() for number in range(2)]

        for car in coordination_info[collided_cars_info[key][1].get_name()]:
            car.new_image()
            cars.append(car)

        cars.sort(key=lambda car: car.get_name())

        for car in cars:
            messages.append(NewCarMessage(car))

        for message in messages:
            message.process(infrastructure_supervisor)
            for car in cars:
                message.process(car)

        messages = infrastructure_supervisor.get_new_messages()
        for message in messages:
            for car in cars:
                message.process(car)

        while iteration:
            if not collision_wait:
                left_intersection_cars = []
                left_intersection_cars_log = []
                messages.sort(key=lambda not_sorted_message: not_sorted_message.get_value(), reverse=True)
                for message in messages:
                    message.process(infrastructure_supervisor)
                for new_message in infrastructure_supervisor.get_new_messages():
                    new_messages.append(new_message)
                infrastructure_supervisor.set_new_messages([])
                for car in cars:
                    for message in messages:
                        message.process(car)
                    car.update()
                    for new_message in car.get_new_messages():
                        new_messages.append(new_message)
                    car.set_new_messages([])
                    if not car.screen_car.colliderect(full_intersection_rect):
                        left_intersection_cars.append(car)
                        for message in car.get_left_intersection_messages():
                            new_messages.append(message)
                        # new_messages.append(LeftIntersectionMessage(car))
                        # if car.get_active_supervisor():
                        #     new_messages.insert(0, SupervisorLeftIntersectionMessage(car))
                        if log:
                            left_intersection_cars_log.append(car)
                        continue
                collided_cars, collide = colliding_cars(cars)
                for left_car in left_intersection_cars:
                    cars.remove(left_car)
                messages = new_messages
                new_messages = []

                events = pygame.event.get()
                iteration = not check_close_application(events)
                collision_wait = continue_simulation(events)
                screen.blit(background, (0, 0))
                screen.blit(intersection_background, (0, 0))
                for car in cars:
                    screen.blit(car.rotated_image, car.screen_car)
                    display_info_on_car(car, screen, font, 1, "name", "following")
                show_caravan(cars, screen, font, collided_cars, screen_width)
                pygame.display.update(screen.get_rect())
            else:
                events = pygame.event.get()
                iteration = not check_close_application(events)
                collision_wait = not continue_simulation(events)
    screen.blit(background, (0, 0))
    screen.blit(font.render("No hay mas colisiones para analizar", True, (0, 0, 0)),
                (screen.get_width() / 3, screen.get_height() / 2))
    pygame.display.update(screen.get_rect())
    pygame.time.wait(2000)
