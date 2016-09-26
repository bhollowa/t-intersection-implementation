from pygame.locals import *
import pygame
from models.car import Car
from random import randint


white = (255, 255, 255)
black = (0, 0, 0)
initial_positions = [(430, 700, 0, 1), (760, 350, 90, 2), (350, 10, 180, 3), (10, 430, 270, 4)]


def distance_to_center(**kwargs):
    if 'car' in kwargs:
        return kwargs['car'].distance_to_center()
    elif 'message' in kwargs:
        return kwargs['message'].distance_to_center()


def reposition_car_in_screen(screen, car):
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
    return True


def random_car(name, max_speed):
    pos_x, pos_y, direction, lane = initial_positions[randint(0, len(initial_positions) - 1)]
    initial_speed = randint(0, max_speed)
    return Car(str(name), pos_x, pos_y, direction=direction, lane=lane, absolute_speed=initial_speed)


def colliding_cars(car_list):
    for i in range(len(car_list)):
        for j in range(i+1,len(car_list)):
            if car_list[i].screen_car.colliderect(car_list[j].screen_car):
                return (car_list[i], car_list[j]), True
    return None, False


def display_info_on_car(car, display, letter, *args):
    x, y = car.get_position()
    if "name" in args:
        display.blit(letter.render(car.name, True, black), (x, y))
    if "speed" in args:
        display.blit(letter.render(str(car.get_speed()), True, black), (x - 30, y))
    if "followers" in args:
        followers = car.get_followers()
        for follower in followers:
            x, y = follower.get_position()
            display.blit(letter.render(car.name, True, black), (x + 30, y))
