import os
import pygame
from auxiliary_functions.auxiliary_functions import check_close_application, random_car, colliding_cars, \
    display_info_on_car, create_logs, supervisor, separate_new_and_old_cars, continue_simulation, show_caravan
from car_controllers.supervisor_level import supervisor_level
import sys
import numpy as np


def main_simulation(graphic_environment, limit, *args, **kwargs):
    attack_supervisory = "attack_supervisory" in args
    wait = "wait" in args
    distributed = "distributed" in args
    log = "log" in kwargs
    show_virtual_caravan = "show_caravan" in args
    images_directory = os.path.dirname(os.path.abspath(__file__)) + "/images/"
    if log:
        collision_log, left_intersection_log, total_cars_log = create_logs(kwargs["log"])
        left_intersection_cars = []
        collision_message = ""
    cars = []
    iteration = True
    intersection_rect = pygame.Rect(280, 280, 210, 210)
    collisions = 0
    collision_list = []

    if graphic_environment:
        fps = 60
        screen_width = 768
        if show_virtual_caravan:
            screen_width = 1468
        screen = pygame.display.set_mode((screen_width, 768))
        intersection_bg = pygame.image.load(images_directory + "background.jpg")
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((250, 250, 250))
        clock = pygame.time.Clock()
        pygame.init()
        font = pygame.font.SysFont('Arial', 20)
        pygame.display.set_caption('Car simulation')

    full_intersection_rect = pygame.Rect(0, 0, 768, 768)
    counter = 0
    car_name_counter = 0
    cars_per_second = 4
    collision = False
    min_speed = 20
    max_speed = 20
    last_lane = -1
    not_created_vehicles = 0
    collision_wait = False
    display_time_counter = 0
    lanes_waiting_time = [(0, 0), (0, 0), (0, 0), (0, 0)]
    rate = 0.5

    for i in range(len(lanes_waiting_time)):
        lane = lanes_waiting_time[i]
        lanes_waiting_time[i] = (np.random.exponential(1.0/rate), lane[1])
    print_collision_message = False

    while iteration and car_name_counter < limit:
        if not collision_wait:
            display_time_counter += 1
            counter += 1
            time = counter / 60.0

            for i in range(len(lanes_waiting_time)):
                lanes_waiting_time[i] = (lanes_waiting_time[i][0], lanes_waiting_time[i][1] + 1)
                if lanes_waiting_time[i][0] <= lanes_waiting_time[i][1]/60.0:
                    new_car = random_car(car_name_counter, min_speed, max_speed, last_lane=last_lane)
                    new_car.new_image()
                    if not new_car.collide(cars):
                        lanes_waiting_time[i] = (np.random.exponential(1.0 / rate), 0)
                        cars.append(new_car)
                        car_name_counter += 1
                    else:
                        not_created_vehicles += 1
            if not distributed:
                new_cars, old_cars = separate_new_and_old_cars(cars)
                if len(new_cars) > 0:
                    supervisor_level(new_cars, old_cars, attack_supervisory)
            for car in cars:
                if distributed:
                    if not supervisor(cars) and car.is_new():  # TODO: change name of supervisor function and move it to car class
                        car.set_active_supervisory_level()
                    if car.is_supervisor():
                        for this_car in cars:
                            car.add_supervisor_message(this_car.get_info_message())
                        car.supervisor_level()
                        for message in car.get_supervisor_result_messages():
                            receiver = None
                            for this_car in cars:
                                if message.get_receiver() == this_car.get_name():
                                    receiver = this_car
                                if message.get_type() is "follower":
                                    if message.get_follower() == this_car.get_name():
                                        message.set_car(this_car)
                            receiver.receive(message)
                        car.clear_supervisor_messages()
                        car.clear_supervisor_results_messages()
                if not car.screen_car.colliderect(full_intersection_rect):
                    cars.remove(car)
                    car.set_left_intersection_time()
                    for follower in car.get_followers():
                        follower.stop_following()
                    if log:
                        left_intersection_cars.append(car)
                    continue
                car.update()
            collided_cars, collide = colliding_cars(cars)
            if collide and collided_cars[0].screen_car.colliderect(intersection_rect):
                code = str(collided_cars[0].get_name()) + "to" + str(
                    collided_cars[1].get_name())
                if code not in collision_list:
                    collision = True
                    collision_list.append(code)
                    collisions += 1
                    if log:
                        collision_message = '{"collision_code":"' + code + '", "collision_initial_conditions":['
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
                log_message = ""
                for car in left_intersection_cars:
                    log_message += '[' + str(car) + ','
                left_intersection_cars = []
                if len(log_message) > 0:
                    log_message = log_message[:len(log_message)-1] + ']'
                    left_intersection_log.info(log_message)
            if graphic_environment:
                events = pygame.event.get()
                iteration = check_close_application(events)
                screen.blit(background, (0, 0))
                screen.blit(intersection_bg, (0, 0))
                for car in cars:
                    screen.blit(car.rotated_image, car.screen_car)
                    display_info_on_car(car, screen, font, "name", "following")
                if show_virtual_caravan:
                    show_caravan(cars, screen, font, collided_cars, screen_width)
                pygame.display.update(screen.get_rect())
                clock.tick(fps)
                if wait and collide and collided_cars[0].screen_car.colliderect(intersection_rect):
                    collision_wait = True
            if display_time_counter / 60 == 1:
                sys.stdout.write("\r" + str(time) + " Waiting times: " + str([(k, j/60.0) for k, j in lanes_waiting_time]))
                sys.stdout.flush()
                display_time_counter = 0
        else:
            if print_collision_message:
                print_collision_message = False
                sys.stdout.write("\r" + " Collision! Press a key to continue")
                sys.stdout.flush()
                display_time_counter = 0
            events = pygame.event.get()
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
car_limit = 1000000
main_simulation(True, car_limit, "show_caravan", "wait", log="_law_control")
