# INITIALISATION
import pygame
from models.car import Car
from pygame.locals import *
from car_controllers.user_controller import car_user_input
from car_controllers.deafult_controller import default_controller
from car_controllers.supervisor_level import supervisor_level
from random import randint

screen = pygame.display.set_mode((768, 768))
bg = pygame.image.load("background.jpg")
initial_speed = 10
probando = Car("segundo", 70, 430, pygame.image.load("car.png"), direction=270, lane=2, absolute_speed=initial_speed)
dummy_cars = [Car("primero", 430, 700, pygame.image.load("car.png"), lane=1,absolute_speed=initial_speed), probando,
              Car("tercero", 350, 70, pygame.image.load("car.png"), direction=180, lane=3, absolute_speed=initial_speed), Car("cuarto", 700, 350, pygame.image.load("car.png"), direction=90, lane=4, absolute_speed=initial_speed)]
new_cars = []
cars = []
clock = pygame.time.Clock()
inputs = (0, 0, 0, 0)
iteration = True
new_car = False
TURN_SPEED = 5
ACCELERATION = 2
MAX_FORWARD_SPEED = 10
MAX_REVERSE_SPEED = -5
BLACK = (0, 0, 0)
FPS = 120


def reposition_car_in_screen(car):
    old_position = car.get_position()
    new_position = old_position
    if old_position[0] > (screen.get_rect().x + screen.get_rect().w):
        new_position = (0, old_position[1])
    elif old_position[0] < screen.get_rect().x:
        new_position = (screen.get_rect().x + screen.get_rect().w, old_position[1])
    if old_position[1] > (screen.get_rect().y + screen.get_rect().h):
        new_position = (old_position[0], 0)
    elif old_position[1] < screen.get_rect().y:
        new_position = (old_position[0], screen.get_rect().y + screen.get_rect().h)
    car.set_position(new_position)


def check_close_application(user_input):
    for event in user_input:
        if event.type == pygame.QUIT:
            return False
        if hasattr(event, 'key'):
            if event.key == K_ESCAPE:
                return False
            elif event.key == K_SPACE and event.type == KEYDOWN:
                print probando.distance_to_center()
    return True


counter = 0
screen_cars = []
if __name__ == "__main__":
    while iteration:
        counter += 1
        if counter % 20 == 0 and counter < 81:
            number = randint(0,len(dummy_cars)-1)
            new_cars.append(dummy_cars[number])
            dummy_cars.pop(number)
            new_car = True
        if counter == 122:
            for car in cars:
                for follower in car.get_followers():
                    print follower.name + " sigue a " + car.name
        if new_car:
            new_cars = supervisor_level(new_cars, cars)
            new_car = False
        events = pygame.event.get()
        iteration = check_close_application(events)
        clock.tick(FPS)
        for car in cars:
            # if car.following_car is not None and not car.following_car.screen_car.colliderect(screen.get_rect()):
            #     if car.following_car in cars:
            #         cars.remove(car.following_car)
            #     car.following_car = None
            #     car.set_controller(default_controller)
            inputs = car.controller(inputs, car)
            car.update(*inputs)
            screen_cars.append(car.screen_car)
            screen.blit(car.rotated_image, car.screen_car)
            pygame.display.update()
            inputs = (0, 0, 0, 0)
        screen.blit(bg, (0, 0))
        pygame.display.update(screen_cars)
        screen_cars = []
