from json import JSONDecoder
from datetime import datetime
from auxiliar_functions import create_car_from_json, colliding_cars
from car_controllers.follower_controller import follower_controller
import pygame


def create_cars_from_collision_json(collision_json):
    """
    Creates all the cars stored in a json reporting a collision. The json must have the form
    {"time":<string with specified format>, "message":{"collision_code":<string>,
    "collision_initial_conditions":<list of cars>}}. All followers have been assigned.
    Time format: "%Y-%m-%d %H:%M:%S,%f".
    :param collision_json: json with a collision report.
    :return: dictionary with the cars. The key value is the name of the car.
    """
    collision_information = JSONDecoder().decode(collision_json)
    json_cars = collision_information["message"]["collision_initial_conditions"]
    cars_dict = {}
    for json_car in json_cars:
        cars_dict[json_car["car_name"]] = create_car_from_json(json_car)
    for json_car in json_cars:
        if json_car["following"] in cars_dict:
            car = cars_dict[json_car["car_name"]]
            cars_dict[json_car["following"]].add_follower(car)
            car.start_following()
            car.set_controller(follower_controller)
    return cars_dict


def create_times_from_collision_json(collision_json):
    """
    Obtains all the times at which all the cars stored in the collision json entered the intersection (or where created).
     The json must have the form {"time":<string with specified format>, "message":{"collision_code":<string>,
    "collision_initial_conditions":<list of cars>}}. Also returns the time at which the collision in the jason should start.
    Time format: "%Y-%m-%d %H:%M:%S,%f".
    :param collision_json: json with a collision report.
    :return: dictionary with the cars. The key value is the name of the car.
    """
    collision_information = JSONDecoder().decode(collision_json)
    json_cars = collision_information["message"]["collision_initial_conditions"]
    time_format = '%Y-%m-%d %H:%M:%S,%f'
    collision_time = datetime.strptime(collision_information["time"], time_format)
    car_creation_times = []
    for json_car in json_cars:
        car_creation_times.append((datetime.fromtimestamp(json_car["creation_time"]), json_car["car_name"]))
    car_creation_times.sort(key=lambda x: x[0])
    start_simulation_time = collision_time
    for car_time in car_creation_times:
        if car_time[0] < start_simulation_time:
            start_simulation_time = car_time[0]
    return start_simulation_time, car_creation_times


def recreate_collision(collision_json):
    start_simulation_time, car_creation_times = create_times_from_collision_json(collision_json)
    cars_dict = create_cars_from_collision_json(collision_json)
    car_creation_counter = 0
    collisions = 0
    collision_list = []
    cars = []
    intersection = pygame.Rect(280, 280, 210, 210)
    screen_rect = pygame.Rect(0, 0, 768, 768)
    screen_cars = []
    recreation_start_time = datetime.now()
    while True:
        if car_creation_times[car_creation_counter][0] - start_simulation_time < datetime.now() - recreation_start_time and car_creation_counter < len(car_creation_times) -1:
            cars.append(cars_dict[car_creation_times[car_creation_counter][1]])
            car_creation_counter += 1
        for car in cars:
            if not car.screen_car.colliderect(screen_rect):
                cars.remove(car)
                for follower in car.get_followers():
                    follower.stop_following()
                continue
            car.update(*car.controller(car))
            screen_cars.append(car.screen_car)
        screen_cars = []
        collided_cars, collide = colliding_cars(cars)
        if collide and collided_cars[0].screen_car.colliderect(intersection):
            print "collision"
            code = str(collided_cars[0].get_name()) + "to" + str(
                collided_cars[1].get_name())
            if code not in collision_list:
                collision_list.append(code)
                collisions += 1
        if len(cars) <= 0:
            break