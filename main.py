import os
import pygame
from auxiliar_functions import check_close_application, random_car, random_cars, colliding_cars, display_info_on_car
from car_controllers.supervisor_level import supervisor_level

images_directory = os.getcwd() + "/images/"
# screen = pygame.display.set_mode((768, 768))
screen = pygame.Rect(0, 0, 768, 768)
# bg = pygame.image.load(images_directory + "background.jpg")
new_cars = []
cars = []
# clock = pygame.time.Clock()
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
    # pygame.init()
    # font = pygame.font.SysFont('Arial', 20)
    # pygame.display.set_caption('Car simulation')
    # new_cars = random_cars([1, 1, 3, 2], 0, 20)
    # new_car = True
    while iteration and car_name_counter < 10000:
        counter += 1
        if car_name_counter % 250 == 0:
            print "Number of cars simulated: " + str(car_name_counter)
        if counter % (60/cars_per_second) == 0:
            # lanes = [1, 1, 3, 2]
            new_cars.append(random_car(car_name_counter, 20))
            car_name_counter += 1
            new_car = True
        if new_car:
            new_cars = supervisor_level(new_cars, cars)
            new_car = False
        # events = pygame.event.get()
        # iteration = check_close_application(events)
        # screen.blit(bg, (0, 0))
        for car in cars:
            if not car.screen_car.colliderect(screen):
                cars.remove(car)
                for follower in car.get_followers():
                    follower.stop_following()
                continue
            inputs = car.controller(inputs, car)
            car.update(*inputs)
            screen_cars.append(car.screen_car)
            # screen.blit(car.rotated_image, car.screen_car)
            # display_info_on_car(car, screen, font, "name", "following")
            # pygame.display.update()
            inputs = (0, 0, 0, 0)
        screen_cars = []
        collided_cars, collide = colliding_cars(cars)
        if collide and collided_cars[0].screen_car.colliderect(intersection):
            print "Collision. Start recording. Code: " + str(collided_cars[0].get_name()) + "to" + str(collided_cars[1].get_name())
            for car in cars:
                print car.initial_conditions()
            for car in collided_cars:
                print car
                # pygame.time.wait(10000)
            print "End collision. Finish records"
        # clock.tick(FPS)
