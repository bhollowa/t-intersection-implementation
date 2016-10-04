import os
import pygame
from auxiliar_functions import check_close_application, random_car, colliding_cars, display_info_on_car, create_logs, \
    create_random_cars
from car_controllers.supervisor_level import supervisor_level
import copy
import threading


def main_simulation(graphic_environment, limit, *args, **kwargs):
    attack_supervisory = "attack_supervisory" in args
    wait = "wait" in args
    no_same_lane = "no_same_line" in args
    images_directory = os.path.dirname(os.path.abspath(__file__)) + "/images/"
    if "log" in kwargs:
        collision_log, left_intersection_log, total_cars_log = create_logs(kwargs["log"])

    new_cars = []
    cars = []
    iteration = True
    new_car = False
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
    cars_per_second = 2
    collision = False
    collision_message = ""
    left_intersection_cars = []
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
                new_cars.append(new_car)
                car_name_counter += 1
                new_car = True
            else:
                new_car = random_car(car_name_counter, min_speed, max_speed, last_lane=last_lane)
                if no_same_lane:
                    last_lane = new_car.get_lane()
                new_car.new_image()
                if not new_car.collide(cars):
                    new_cars.append(new_car)
                    car_name_counter += 1
                    new_car = True
                else:
                    not_created_vehicles += 1
        if new_car:
            new_cars = supervisor_level(new_cars, cars, attack_supervisory)
            new_car = False
        if graphic_environment:
            events = pygame.event.get()
            iteration = check_close_application(events)
            screen.blit(bg, (0, 0))
        for car in cars:
            if not car.screen_car.colliderect(screen_rect):
                cars.remove(car)
                car.set_left_intersection_time()
                left_intersection_cars.append(car)
                for follower in car.get_followers():
                    follower.stop_following()
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

    print "Last record. Total collisions: " + str(collisions), "Not created vehicles: " + str(not_created_vehicles)

car_limit = 10000
threading.Thread(target=main_simulation, args=(False, car_limit, "no_same_lane"),
                 kwargs={"log": "_no_same_lane"}).start()
threading.Thread(target=main_simulation, args=(False, car_limit),
                 kwargs={"log": "_same_lane"}).start()
threading.Thread(target=main_simulation, args=(False, car_limit, "attack_supervisory", "no_same_lane"),
                 kwargs={"log": "_attack_no_same_lane"}).start()
threading.Thread(target=main_simulation, args=(False, car_limit, "attack_supervisory"),
                 kwargs={"log": "_attack_same_lane"}).start()
