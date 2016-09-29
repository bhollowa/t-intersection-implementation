import os
import pygame
from auxiliar_functions import check_close_application, random_car, colliding_cars, display_info_on_car, setup_logger
from car_controllers.supervisor_level import supervisor_level
from sys import argv
import logging


def main_simulation(log_name, graphic_environment, limit):
    wait = "wait" in argv
    images_directory = os.path.dirname(os.path.abspath(__file__)) + "/images/"
    logger_directory = os.path.dirname(os.path.abspath(__file__)) + "/logs/"
    setup_logger("collision", logger_directory + "collisions" + log_name + ".log")
    setup_logger("numbers_of_cars", logger_directory + "total_cars" + log_name + ".log")
    setup_logger("left_intersection", logger_directory + "left_intersection" + log_name + ".log")
    collision_log = logging.getLogger('collision')
    total_cars_log = logging.getLogger('numbers_of_cars')
    left_intersection_log = logging.getLogger('left_intersection')

    new_cars = []
    cars = []
    iteration = True
    new_car = False
    intersection = pygame.Rect(280, 280, 210, 210)
    FPS = 60
    collisions = 0
    collision_list = []

    if graphic_environment:
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
    while iteration and car_name_counter < limit:
        counter += 1
        if car_name_counter % 250 == 0 and counter % (60/cars_per_second) == 0:
            message = '{"cars_simulated":' + str(car_name_counter) + '}'
            total_cars_log.info(message)
        if counter % (60/cars_per_second) == 0:
            if len(cars) > 0:
                new_cars.append(random_car(car_name_counter, 20, last_lane=cars[len(cars)-1].get_lane()))
            else:
                new_cars.append(random_car(car_name_counter, 20))
            car_name_counter += 1
            new_car = True
        if new_car:
            new_cars = supervisor_level(new_cars, cars)
            new_car = False
        if graphic_environment:
            events = pygame.event.get()
            iteration = check_close_application(events)
            screen.blit(bg, (0, 0))
        for car in cars:
            if not car.screen_car.colliderect(screen_rect):
                cars.remove(car)
                car.set_left_intersection_time()
                left_intersection_log.info(str(car))
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
                collision_list.append(code)
                collisions += 1
                message = '{"collision_code":"' + code + '",'
                message += ' "collision_initial_conditions":['
                for car in cars:
                    message += car.to_json() + ','
                message = message[:len(message)-1] + '],'
                message += '"collided_cars":['
                for car in collided_cars:
                    message += car.to_json() + ','
                    if graphic_environment and wait:
                        pygame.time.wait(10000)
                message = message[:len(message) - 1] + ']}'
                collision_log.info(message)
        if graphic_environment:
            pygame.display.update(screen_rect)
            clock.tick(FPS)
    print "Last records. Total collisions: " + str(collisions)

car_limit = 10000
main_simulation("_no_graphic", False, car_limit)
main_simulation("_graphic", True, car_limit)