import pygame
import os
from log_files_process import generate_left_intersection_cars_from_file, generate_collision_cars_from_file
from auxiliary_functions.auxiliary_functions import display_info_on_car, show_caravan, init_graphic_environment, \
    separate_new_and_old_cars
from car_controllers.supervisor_level import supervisor_level


def simulate_collision(log):
    log_directory = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"
    all_cars_file = open(log_directory + "left_intersection" + log + ".log")
    collisions_file = open(log_directory + "collisions" + log + ".log")

    all_cars = generate_left_intersection_cars_from_file(all_cars_file)
    collisions_cars, collided_cars = generate_collision_cars_from_file(collisions_file, all_cars)

    collided_cars[0].sort(key=lambda this_car: this_car.get_name())
    cars_at_creation = []
    counter = 0
    while True:
        actual_car = all_cars[collided_cars[0][1].get_name() - counter]
        if actual_car.get_left_intersection_time() < collided_cars[0][1].get_creation_time():
            break
        actual_car.reset()
        actual_car.new_image()
        cars_at_creation.append(actual_car)
        counter += 1
    cars_at_creation.sort(key=lambda this_car: this_car.get_name(), reverse=True)

    screen, background, intersection_background, font = init_graphic_environment(1468, 768)
    full_intersection_rect = pygame.Rect(0, 0, 768, 768)
    cars = []

    while True:
        if len(cars_at_creation) > 0:
            if not cars_at_creation[0].collide(cars):
                cars.append(cars_at_creation.pop())
        new_cars, old_cars = separate_new_and_old_cars(cars)
        if len(new_cars) > 0:
            supervisor_level(new_cars, old_cars, False)
        screen.blit(background, (0, 0))
        screen.blit(intersection_background, (0, 0))
        for car in cars:
            car.update()
            if not car.screen_car.colliderect(full_intersection_rect):
                cars.remove(car)
                car.set_left_intersection_time()
                for follower in car.get_followers():
                    follower.stop_following()
            screen.blit(car.rotated_image, car.screen_car)
            display_info_on_car(car, screen, font, "name", "following")
        show_caravan(cars, screen, font, collided_cars[0], screen.get_width())
        pygame.display.update(screen.get_rect())
