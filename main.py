import os
import pygame

from auxiliar_functions import check_close_application, random_car, colliding_cars
from car_controllers.supervisor_level import supervisor_level

images_directory = os.getcwd() + "/images/"
screen = pygame.display.set_mode((768, 768))
bg = pygame.image.load(images_directory + "background.jpg")
new_cars = []
cars = []
clock = pygame.time.Clock()
inputs = (0, 0, 0, 0)
iteration = True
new_car = False
intersection = pygame.Rect(280, 280, 210, 210)
FPS = 60
counter = 0
screen_cars = []
car_name_counter = 0


if __name__ == "__main__":
    cars_per_second = 2
    pygame.init()
    font = pygame.font.SysFont('Arial', 20)
    pygame.display.set_caption('Car simulation')
    while iteration:
        counter += 1
        if counter % (60/cars_per_second) == 0:
            new_cars.append(random_car(car_name_counter, 20))
            car_name_counter += 1
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
        collided_cars, collide = colliding_cars(cars)
        if collide and collided_cars[0].screen_car.colliderect(intersection):
            for car in collided_cars:
                print car
            pygame.time.wait(3000)
        clock.tick(FPS)
