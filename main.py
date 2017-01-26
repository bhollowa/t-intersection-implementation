import pygame
from auxiliary_functions.auxiliary_functions import check_close_application, random_car, colliding_cars, \
    display_info_on_car, create_logs, continue_simulation, show_caravan, init_graphic_environment, supervisor, \
    supervisor_message, get_supervisor, coordinator_fail, coordinator_lies
from models.message import NewCarMessage
from models.car import Car, InfrastructureCar, SupervisorCar
import sys
import numpy as np
from random import randint


def main_simulation(graphic_environment, limit, stand_still_param=5, fix=True, *args, **kwargs):
    distributed = "distributed" in args
    log = "log" in kwargs
    show_virtual_caravan = "show_caravan" in args
    initial_speed = -1
    if "initial_speed" in kwargs:
        initial_speed = kwargs["initial_speed"]
    if log:
        collision_log, left_intersection_log, total_cars_log, coordination_log = create_logs(kwargs["log"])
        collision_message = ""
    cars = {}
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
    rate = 0.1
    number_of_lanes = 4

    infrastructure_supervisor = InfrastructureCar(-1, fix=fix)
    if not distributed:
        infrastructure_supervisor.new_image()
        cars[-1] = infrastructure_supervisor

    for i in range(len(lanes_waiting_time)):
        lane = lanes_waiting_time[i]
        lanes_waiting_time[i] = (np.random.exponential(1.0/rate), lane[1])
    print_collision_message = True

    collided_car_surface = pygame.Surface((50, 50))
    collided_car_surface.fill((255, 0, 0, 0))
    messages = []
    new_messages = []
    creation_dummy_cars = []
    for coordinates in [(435, 760, 0, 0), (760, 345, 90, 1), (345, 10, 180, 2), (10, 435, 270, 3)]:
        dummy_car = Car(-1, coordinates[0], coordinates[1], direction=coordinates[2], lane=coordinates[3])
        dummy_car.new_image(0.1)
        creation_dummy_cars.append(dummy_car)

    while iteration and car_name_counter < limit:
        if not collision_wait or not graphic_environment:
            display_time_counter += 1
            counter += 1
            for lane in range(len(lanes_waiting_time)):
                if not creation_dummy_cars[lane].collide(cars.values()):
                    lanes_waiting_time[lane] = (lanes_waiting_time[lane][0], lanes_waiting_time[lane][1] + 1)
                if lanes_waiting_time[lane][0] <= lanes_waiting_time[lane][1]:
                    new_car = random_car(car_name_counter, min_speed, max_speed, counter, number_of_lanes, fix,
                                         stand_still_param, lane=lane, initial_speed=initial_speed)
                    new_car.new_image()
                    lanes_waiting_time[lane] = (np.random.exponential(1.0 / rate), 0)
                    if len(cars) == 0:  # not supervisor(cars) and not supervisor_message(messages):
                        new_car.__class__ = SupervisorCar
                    cars[car_name_counter] = new_car
                    new_messages.append(NewCarMessage(new_car))
                    car_name_counter += 1
                    if car_name_counter % 500 == 0:
                        print str(car_name_counter) + " cars created"
            left_intersection_cars = []
            left_intersection_cars_log = []
            messages.sort(key=lambda not_sorted_message: not_sorted_message.get_value(), reverse=True)
            for car in cars.values():
                for message in messages:
                    message.process(car)
                car.update()
                for new_message in car.get_new_messages():
                    new_messages.append(new_message)
                car.set_new_messages([])
                if not car.screen_car.colliderect(full_intersection_rect):
                    left_intersection_cars.append(car)
                    car.set_left_intersection_time(counter)
                    if car.get_left_intersection_messages() is not None:
                        new_messages.append(car.get_left_intersection_messages())
                    if log:
                        left_intersection_cars_log.append(car)
            for left_car in left_intersection_cars:
                del cars[left_car.get_name()]
            messages = new_messages
            new_messages = []
            collided_cars, collide = colliding_cars(cars.values())
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
                        for car in cars.values():
                            collision_message += car.to_json() + ','
                        collision_message = collision_message[:len(collision_message)-1] + '],"collided_cars":['
                        for car in collided_cars:
                            collision_message += car.to_json() + ','
                        collision_message = collision_message[:len(collision_message) - 1] + ']}'
            if "log" in kwargs:
                supervisor_car = get_supervisor(cars.values())
                if supervisor_car is not None:
                    for message in supervisor_car.get_log_messages():
                        try:
                            message["coordinated_car"].set_x_position(cars[message["coordinated_car"].get_name()]
                                                                      .get_x_position())
                            message["coordinated_car"].set_y_position(cars[message["coordinated_car"].get_name()]
                                                                      .get_y_position())
                            message["coordinated_car"].set_direction(cars[message["coordinated_car"].get_name()]
                                                                     .get_direction())
                            message["coordinated_car"].set_speed(cars[message["coordinated_car"].get_name()].get_speed())
                            log_string = '{"coordinated_car":' + message["coordinated_car"].to_json()
                            log_string += ',"car_order":['
                            for car in message["old_cars"]:
                                for old_car in cars.values():
                                    if old_car.get_name() == car.get_name():
                                        car.set_x_position(old_car.get_x_position())
                                        car.set_y_position(old_car.get_y_position())
                                        car.set_direction(old_car.get_direction())
                                        car.set_speed(old_car.get_speed())
                                        break
                                log_string += car.to_json() + ","
                            log_string = log_string[:len(log_string) - 1] + "]"
                            log_string += ',"selected_car":' + message["selected_car"].to_json() + "}"
                            coordination_log.info(log_string)
                        except KeyError:
                            pass
                    supervisor_car.set_log_messages([])
                if collision:
                    collision_log.info(collision_message)
                    collision = False
                    collision_message = ""
                    return -1
                if car_name_counter % 250.0 == 0 and counter % (60.0 / cars_per_second) == 0:
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
                supervisor_car = get_supervisor(cars.values())
                if coordinator_fail(events) and supervisor_car:
                    supervisor_car.attack_supervisor = True
                if coordinator_lies(events) and supervisor_car:
                    supervisor_car.supervisor_lies = True
                iteration = not check_close_application(events)
                collision_wait = continue_simulation(events) or collision_wait
                screen.blit(background, (0, 0))
                screen.blit(intersection_background, (0, 0))
                for car in cars.values():
                    screen.blit(car.rotated_image, car.screen_car)
                    display_info_on_car(car, screen, font, 1)
                if show_virtual_caravan:
                    show_caravan(cars.values(), screen, font, collided_cars, screen_width)
                pygame.display.update(screen.get_rect())
        else:
            if print_collision_message:
                print_collision_message = False
                supervisor_car = get_supervisor(cars.values())
                # if supervisor_car is not None:
                #     sys.stdout.write("\r" + str(supervisor_car.get_transmitter_receiver_dict()))
                # sys.stdout.flush()
                display_time_counter = 0
            events = pygame.event.get()
            iteration = not check_close_application(events)
            collision_wait = not continue_simulation(events)
            if not collision_wait:
                print_collision_message = True
    if graphic_environment:
        pygame.display.quit()
    print "\nLast record. Total collisions: " + str(collisions), "\nNot created vehicles: " + str(not_created_vehicles)\
                                                                 + "\nNumber of ticks: " + str(counter)
    return 0

car_limit = 10000
simulation_params = ["_new_not_distributed_no_fix_", "_new_not_distributed_fix_", "_new_distributed_no_fix_", "_new_distributed_fix_"]
stand_still_distances = [5, 7, 9, 11, 13, 15]
initial_speed_values = {5: [0], 7: [0, 5, 10, 20], 9: [0], 11: [20]}
fix_booleans = [False, True, False, True]
distributed_param = ["", "", "distributed", "distributed"]

# for i in range(15, 30, 5):
#     print "Starting simulation for standstill distance " + str(i)
main_simulation(True, car_limit, 5, True, "", "show_caravan") #, log="_standstill_distance_" + str(i))
    # if return_code == 0:
    #     print "Standstill distance " + str(i) + " presented no collisions in " + str(car_limit) + " cars."

# for stand_still_value in stand_still_distances:
#     for initial_speed in initial_speed_values[stand_still_value]:
#         print "Starting simulation " + "_new_speed_test_distance_" + str(stand_still_value) + "_speed_" + str(initial_speed)
#         main_simulation(False, car_limit, stand_still_value, True, "", initial_speed=initial_speed,
#                         log="_new_speed_test_distance_" + str(stand_still_value) + "_speed_" + str(initial_speed))
