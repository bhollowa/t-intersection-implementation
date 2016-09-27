import os
import pygame
from auxiliar_functions import check_close_application, random_car, random_cars, colliding_cars, display_info_on_car
from car_controllers.supervisor_level import supervisor_level
import sys

graphic_environment = "graphic" in sys.argv
images_directory = os.getcwd() + "/images/"
if graphic_environment:
    screen = pygame.display.set_mode((768, 768))
    scree_rect = screen.get_rect()
    bg = pygame.image.load(images_directory + "background.jpg")
    clock = pygame.time.Clock()
    pygame.init()
    font = pygame.font.SysFont('Arial', 20)
    pygame.display.set_caption('Car simulation')
else:
    screen_rect = pygame.Rect(0, 0, 768, 768)
new_cars = []
cars = []
iteration = True
new_car = False
intersection = pygame.Rect(280, 280, 210, 210)
FPS = 60
counter = 0
screen_cars = []
car_name_counter = 0


if __name__ == "__main__":
    cars_per_second = 2
    while iteration and car_name_counter < 10000:
        counter += 1
        if car_name_counter % 250 == 0:
            print "Number of cars simulated: " + str(car_name_counter)
        if counter % (60/cars_per_second) == 0:
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
                for follower in car.get_followers():
                    follower.stop_following()
                continue
            car.update(*car.controller(car))
            screen_cars.append(car.screen_car)
            if graphic_environment:
                screen.blit(car.rotated_image, car.screen_car)
                display_info_on_car(car, screen, font, "name", "following")
                pygame.display.update()
        screen_cars = []
        collided_cars, collide = colliding_cars(cars)
        if collide and collided_cars[0].screen_car.colliderect(intersection):
            print "Collision. Start recording. Code: " + str(collided_cars[0].get_name()) + "to" + str(
                collided_cars[1].get_name())
            for car in cars:
                print car.initial_conditions()
            for car in collided_cars:
                print car
                pygame.time.wait(10000)
            print "End collision. Finish records"
        if graphic_environment:
            clock.tick(FPS)
