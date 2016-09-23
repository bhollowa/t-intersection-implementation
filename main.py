import pygame
from models.car import Car
from car_controllers.supervisor_level import supervisor_level
from random import randint
from models.auxiliar_functions import check_close_application
import os

images_directory = os.getcwd() + "/images/"
screen = pygame.display.set_mode((768, 768))
bg = pygame.image.load(images_directory + "background.jpg")
initial_positions = [(430, 700, 0, 1), (760, 350, 90, 2), (350, 10, 180, 3), (10, 430, 270, 4)]
new_cars = []
cars = []
clock = pygame.time.Clock()
inputs = (0, 0, 0, 0)
iteration = True
new_car = False
BLACK = (0, 0, 0)
FPS = 60
counter = 0
screen_cars = []


def random_car(config, name):
    pos_x, pos_y, direction, lane = config
    initial_speed = randint(0, 30)
    return Car("auto numero " + str(name / 50), pos_x, pos_y, direction=direction, lane=lane, absolute_speed=initial_speed)

def colliding_cars(car_list):
    for i in range(len(car_list)):
        for j in range(i+1,len(car_list)):
            if car_list[i].screen_car.colliderect(car_list[j].screen_car):
                return True


if __name__ == "__main__":
    while iteration:
        counter += 1
        if counter % 35 == 0:
            new_cars.append(random_car(initial_positions[randint(0, len(initial_positions) - 1)], counter))
            new_car = True
        if new_car:
            new_cars = supervisor_level(new_cars, cars)
            new_car = False
        events = pygame.event.get()
        iteration = check_close_application(events)
        for car in cars:
            if not car.screen_car.colliderect(screen.get_rect()):
                cars.remove(car)
                for follower in car.get_followers():
                    follower.stop_following()
                continue
            inputs = car.controller(inputs, car)
            car.update(*inputs)
            screen_cars.append(car.screen_car)
            screen.blit(car.rotated_image, car.screen_car)
            pygame.display.update()
            inputs = (0, 0, 0, 0)
        screen.blit(bg, (0, 0))
        screen_cars = []
        if colliding_cars(cars):
            pygame.time.wait(1000)
        clock.tick(FPS)
