import pygame
from auxiliary_functions.auxiliary_functions import check_close_application, random_car, colliding_cars, \
    display_info_on_car, create_logs, continue_simulation, show_caravan, init_graphic_environment
from models.message import NewCarMessage, LeftIntersectionMessage, SupervisorLeftIntersectionMessage
from models.car import Car
import sys
import numpy as np


def main_simulation(graphic_environment, limit, *args, **kwargs):
    attack_supervisory = "attack_supervisory" in args
    wait = "wait" in args
    distributed = "distributed" in args
    log = "log" in kwargs
    show_virtual_caravan = "show_caravan" in args
    if log:
        collision_log, left_intersection_log, total_cars_log = create_logs(kwargs["log"])
        collision_message = ""
    cars = []
    iteration = True
    intersection_rect = pygame.Rect(280, 280, 210, 210)
    collisions = 0
    collision_list = []

    if graphic_environment:
        screen_width = 768
        if show_virtual_caravan:
            screen_width = 1468
        screen, background, intersection_background, font = init_graphic_environment(screen_width, 768)

    full_intersection_rect = pygame.Rect(0, 0, 768, 768)
    counter = 0
    car_name_counter = 0
    cars_per_second = 4
    collision = False
    min_speed = 20
    max_speed = 20
    not_created_vehicles = 0
    collision_wait = False
    display_time_counter = 0
    lanes_waiting_time = [(0, 0), (0, 0), (0, 0), (0, 0)]
    rate = 0.7

    for i in range(len(lanes_waiting_time)):
        lane = lanes_waiting_time[i]
        lanes_waiting_time[i] = (np.random.exponential(1.0/rate), lane[1])
    print_collision_message = False

    collided_car_surface = pygame.Surface((50, 50))
    collided_car_surface.fill((255, 0, 0, 0))
    messages = []
    new_messages = []
    creation_dummy_cars = []
    for coordinates in [(435, 760, 0, 0), (760, 345, 90, 1), (345, 10, 180, 2), (10, 435, 270, 3)]:
        dummy_car = Car(-1, coordinates[0], coordinates[1], direction=coordinates[2], lane=coordinates[3])
        dummy_car.new_image()
        creation_dummy_cars.append(dummy_car)
    number_of_lanes = 3
    while iteration and car_name_counter < limit:
        if not collision_wait or not wait or not graphic_environment:
            display_time_counter += 1
            counter += 1
            for i in range(len(lanes_waiting_time)):
                lanes_waiting_time[i] = (lanes_waiting_time[i][0], lanes_waiting_time[i][1] + 1)
                if lanes_waiting_time[i][0] <= lanes_waiting_time[i][1]/60.0:
                    lane = car_name_counter % number_of_lanes
                    if not creation_dummy_cars[lane].collide(cars):
                        new_car = random_car(car_name_counter, min_speed, max_speed, lane=lane)
                        new_car.new_image()
                        lanes_waiting_time[i] = (np.random.exponential(1.0 / rate), 0)
                        if len(cars) == 0:
                            new_car.set_active_supervisory(True)
                        cars.append(new_car)
                        new_messages.append(NewCarMessage(new_car))
                        car_name_counter += 1
                    else:
                        not_created_vehicles += 1
            left_intersection_cars = []
            left_intersection_cars_log = []
            messages.sort(key=lambda not_sorted_message: not_sorted_message.get_value(), reverse=True)
            for car in cars:
                for message in messages:
                    message.process(car)
                car.update()
                for new_message in car.get_new_messages():
                    new_messages.append(new_message)
                car.set_new_messages([])
                if not car.screen_car.colliderect(full_intersection_rect):
                    left_intersection_cars.append(car)
                    car.set_left_intersection_time()
                    new_messages.append(LeftIntersectionMessage(car))
                    if car.get_active_supervisor():
                        new_messages.insert(0,SupervisorLeftIntersectionMessage(car))
                    if log:
                        left_intersection_cars_log.append(car)
                    continue
                car.update()
            for left_car in left_intersection_cars:
                cars.remove(left_car)
            messages = new_messages
            new_messages = []
            collided_cars, collide = colliding_cars(cars)
            if collide and collided_cars[0].screen_car.colliderect(intersection_rect):
                collision_code = str(collided_cars[0].get_name()) + "to" + str(collided_cars[1].get_name())
                if collision_code not in collision_list:
                    collision = True
                    collision_wait = True
                    collision_list.append(collision_code)
                    collisions += 1
                    if log:
                        collision_message = '{"collision_code":"' + collision_code + \
                                            '", "collision_initial_conditions":['
                        for car in cars:
                            collision_message += car.to_json() + ','
                        collision_message = collision_message[:len(collision_message)-1] + '],"collided_cars":['
                        for car in collided_cars:
                            collision_message += car.to_json() + ','
                        collision_message = collision_message[:len(collision_message) - 1] + ']}'
            if "log" in kwargs:
                if collision:
                    collision_log.info(collision_message)
                    collision = False
                    collision_message = ""
                if car_name_counter % 250 == 0 and counter % (60 / cars_per_second) == 0:
                    message = '{"cars_simulated":' + str(car_name_counter) + '}'
                    total_cars_log.info(message)
                log_message = "["
                for car in left_intersection_cars_log:
                    log_message += car.to_json() + ','
                if len(log_message) > 1:
                    log_message = log_message[:len(log_message)-1] + ']'
                    left_intersection_log.info(log_message)
            if graphic_environment:
                events = pygame.event.get()
                iteration = check_close_application(events)
                collision_wait = not continue_simulation(events)
                screen.blit(background, (0, 0))
                screen.blit(intersection_background, (0, 0))
                for car in cars:
                    screen.blit(car.rotated_image, car.screen_car)
                    display_info_on_car(car, screen, font, "name", "following")
                if show_virtual_caravan:
                    show_caravan(cars, screen, font, collided_cars, screen_width)
                pygame.display.update(screen.get_rect())
        else:
            if print_collision_message:
                print_collision_message = False
                sys.stdout.write("\r" + " Simulation paused. Press a key to continue")
                sys.stdout.flush()
                display_time_counter = 0
            events = pygame.event.get()
            iteration = check_close_application(events)
            collision_wait = continue_simulation(events)
            if not collision_wait:
                print_collision_message = True
    if graphic_environment:
        pygame.display.quit()
    print "\nLast record. Total collisions: " + str(collisions), "Not created vehicles: " + str(not_created_vehicles)


def print_percentages(times_tuple):
    total_time = (times_tuple[2] - times_tuple[0]).total_seconds()
    graphic_time = (times_tuple[1] - times_tuple[0]).total_seconds()
    no_graphic_time = (times_tuple[2] - times_tuple[1]).total_seconds()
    final_string = "Total simulation time: " + str(total_time)
    final_string += "\nTotal graphic time: " + str(graphic_time)
    final_string += "\nTotal no graphic time: " + str(no_graphic_time)
    final_string += "\nPercentages:\n   -graphic_time/total_time: " + str(graphic_time / total_time)
    final_string += "\n   -no_graphic_time/total_time: " + str(no_graphic_time / total_time)
    final_string += "\n   -no_graphic_time/graphic_time: " + str(no_graphic_time / graphic_time)
    print final_string

# threading.Thread(target=main_simulation, args=(False, car_limit, "distributed")).start()
# threading.Thread(target=main_simulation, args=(False, car_limit, "distributed")).start()
car_limit = 100000
main_simulation(False, car_limit, log="_test4")
