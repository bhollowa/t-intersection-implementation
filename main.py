import os
import pygame
from auxiliary_functions.auxiliary_functions import check_close_application, random_car, colliding_cars, \
    display_info_on_car, create_logs, supervisor, separate_new_and_old_cars, create_random_cars
from car_controllers.supervisor_level import supervisor_level
import threading
from datetime import datetime
import copy


def main_simulation(graphic_environment, limit, *args, **kwargs):
    attack_supervisory = "attack_supervisory" in args
    wait = "wait" in args
    no_same_lane = "no_same_line" in args
    distributed = "distributed" in args
    log = "log" in kwargs
    images_directory = os.path.dirname(os.path.abspath(__file__)) + "/images/"
    if log:
        collision_log, left_intersection_log, total_cars_log = create_logs(kwargs["log"])
        left_intersection_cars = []
    cars = []
    iteration = True
    intersection = pygame.Rect(280, 280, 210, 210)
    collisions = 0
    collision_list = []

    if graphic_environment:
        fps = 60
        screen = pygame.display.set_mode((768, 768))
        screen_rect = screen.get_rect()
        bg = pygame.image.load(images_directory + "background.jpg")
        clock = pygame.time.Clock()
        pygame.init()
        font = pygame.font.SysFont('Arial', 20)
        pygame.display.set_caption('Car simulation')
    else:
        screen_rect = pygame.Rect(0, 0, 768, 768)
    counter = 0
    car_name_counter = 0
    cars_per_second = 4
    collision = False
    collision_message = ""
    min_speed = 10
    max_speed = 20
    last_lane = -1
    not_created_vehicles = 0

    while iteration and car_name_counter < limit:
        counter += 1
        if counter % (60/cars_per_second) == 0:
            if "cars" in kwargs:
                new_car = kwargs["cars"][counter / (60/cars_per_second)-1]
                kwargs["cars"][counter / (60 / cars_per_second) - 1] = None
                new_car.set_creation_time()
                new_car.new_image()
                cars.append(new_car)
                car_name_counter += 1
            else:
                new_car = random_car(car_name_counter, min_speed, max_speed, last_lane=last_lane)
                if no_same_lane:
                    last_lane = new_car.get_lane()
                new_car.new_image()
                if not new_car.collide(cars):
                    cars.append(new_car)
                    car_name_counter += 1
                else:
                    not_created_vehicles += 1
        if graphic_environment:
            events = pygame.event.get()
            iteration = check_close_application(events)
            screen.blit(bg, (0, 0))
        if not distributed:
            new_cars, old_cars = separate_new_and_old_cars(cars)
            supervisor_level(new_cars, old_cars, attack_supervisory)
        for car in cars:
            if car.is_supervisor() and distributed:
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
            if not supervisor(cars) and car.is_new() and distributed:  # TODO: change name of supervisor function and move it to car class
                car.set_active_supervisory_level()
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
            if not car.screen_car.colliderect(screen_rect):
                cars.remove(car)
                car.set_left_intersection_time()
                for follower in car.get_followers():
                    follower.stop_following()
                if log:
                    left_intersection_cars.append(car)
                continue
            car.update(*car.controller(car))
            if graphic_environment:
                screen.blit(car.rotated_image, car.screen_car)
                display_info_on_car(car, screen, font, "name", "following")
        collided_cars, collide = colliding_cars(cars)
        if collide and collided_cars[0].screen_car.colliderect(intersection):
            code = str(collided_cars[0].get_name()) + "to" + str(
                collided_cars[1].get_name())
            if code not in collision_list:
                collision = True
                collision_list.append(code)
                collisions += 1
                collision_message = '{"collision_code":"' + code + '", "collision_initial_conditions":['
                for car in cars:
                    collision_message += car.to_json() + ','
                collision_message = collision_message[:len(collision_message)-1] + '],"collided_cars":['
                for car in collided_cars:
                    collision_message += car.to_json() + ','
                collision_message = collision_message[:len(collision_message) - 1] + ']}'
                if graphic_environment and wait:
                    pygame.time.wait(10000)
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
            pygame.display.update(screen_rect)
            clock.tick(fps)
    if graphic_environment:
        pygame.display.quit()

    print "Last record. Total collisions: " + str(collisions), "Not created vehicles: " + str(not_created_vehicles)


def print_percentages(times_tuple):
    total_time = (times_tuple[2] - times_tuple[0]).total_seconds()
    graphic_time = (times_tuple[1] - times_tuple[0]).total_seconds()
    no_graphic_time = (times_tuple[2] - times_tuple[1]).total_seconds()
    final_string = "Total simulation time: "+ str(total_time)
    final_string += "\nTotal graphic time: " + str(graphic_time)
    final_string += "\nTotal no graphic time: " + str(no_graphic_time)
    final_string += "\nPercentages:\n   -graphic_time/total_time: " + str(graphic_time / total_time)
    final_string += "\n   -no_graphic_time/total_time: " + str(no_graphic_time / total_time)
    final_string += "\n   -no_graphic_time/graphic_time: " + str(no_graphic_time / graphic_time)
    print final_string


# initial_times = []
# mid_times = []
# final_times = []
# for i in range(10):
#     car_limit = 100
#     cars = create_random_cars(car_limit, False)
#     other_cars = copy.deepcopy(cars)
#     initial_times.append(datetime.now())
#     main_simulation(True, car_limit, "distributed", cars=cars)
#     mid_times.append(datetime.now())
#     main_simulation(False, car_limit, "distributed", cars=other_cars)
#     final_times.append(datetime.now())
#     print "\nIteration " + str(i+1) + ":\n"
#     print_percentages((initial_times[i], mid_times[i], final_times[i]))

# threading.Thread(target=main_simulation, args=(False, car_limit, "distributed")).start()
# threading.Thread(target=main_simulation, args=(False, car_limit, "distributed")).start()
car_limit = 1000000
main_simulation(True, car_limit, "distributed")
