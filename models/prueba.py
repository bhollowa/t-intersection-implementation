# INITIALISATION
import pygame
import math
from models.car import Car
from pygame.locals import *
outfile = "car.png"
screen = pygame.display.set_mode((1024, 768))
car = Car(100, 100, pygame.image.load("car.png"))
clock = pygame.time.Clock()
k_up = k_down = k_left = k_right = 0
TURN_SPEED = 5
ACCELERATION = 2
MAX_FORWARD_SPEED = 10
MAX_REVERSE_SPEED = -5
BLACK = (0, 0, 0)
iterar = True
while iterar:
    # USER INPUT
    clock.tick(120)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            iterar = False
        if not hasattr(event, 'key'):
            continue
        down = event.type == KEYDOWN     # key down or up?
        if event.key == K_RIGHT:
            k_right = down * -5
        elif event.key == K_LEFT:
            k_left = down * 5
        elif event.key == K_UP:
            k_up = down * 2
        elif event.key == K_DOWN:
            k_down = down * -2
        elif event.key == K_SPACE:
            print car
        elif event.key == K_ESCAPE:
            iterar = not iterar     # quit the game
    screen.fill(BLACK)
    car.update(k_right, k_left, k_up, k_down)
    screen.blit(car.rotated_image, car.screen_car)
    pygame.display.flip()


def reposition_car_in_screen(car):
    old_position = (car.get_rect().x, car.get_rect().y)
    if old_position[0] > (screen.get_rect().x + screen.get_rect().w):
        old_position = (0, old_position[1])
    elif old_position[0] < screen.get_rect().x:
        old_position = (screen.get_rect().x + screen.get_rect().w, old_position[1])
    if old_position[1] > (screen.get_rect().y + screen.get_rect().h):
        old_position = (old_position[0], 0)
    elif old_position[1] < screen.get_rect().y:
        old_position = (old_position[0], screen.get_rect().y + screen.get_rect().h)
