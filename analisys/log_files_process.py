from models.car import Car
from models.message import Message
from json import JSONDecoder


def generate_left_intersection_cars_from_file(left_intersection_file):
    """
    Create cars from the information at a file. Every line of the file must have the form
    {"time":<log_time, str>, "message":[{"name":<car_name, int>,"following":<following_car_name, int>,"lane":<lane, int>
    ,"speed":<speed, float>, "creation_time":<creation time of the car, float>,
    "left_intersection_time":<left intersection time of the car, float>,"intention":<intention, str>,
    "actual_coordinates": { "x_coordinate":<x_coordinate, float>,"y_coordinate":<y_coordinate, float>,
    "direction":<direction, float>}}]},
    :param left_intersection_file: log file of the cars that left the intersection.
    :return: <dict> Dictionary that for key has the car and the values is the car.
    """
    all_cars = {}
    for line in left_intersection_file:
        cars_information = JSONDecoder().decode(line[:len(line) - 2])['message']
        for car_information in cars_information:
            all_cars[car_information["name"]] = Car(int(car_information["name"]),
                                                    pos_x=car_information["actual_coordinates"]["x_coordinate"],
                                                    pos_y=car_information["actual_coordinates"]["y_coordinate"],
                                                    direction=car_information["actual_coordinates"]["direction"],
                                                    lane=car_information["lane"],
                                                    intention=car_information["intention"],
                                                    creation_time=car_information["creation_time"],
                                                    left_intersection_time=car_information["left_intersection_time"])
            if car_information["following"] in all_cars.keys():
                all_cars[car_information["name"]].set_following_car_message(
                    Message(all_cars[car_information["following"]]))
    return all_cars


def generate_collision_cars_from_file(collisions_file, all_cars):
    """
    Generates the cars of all the collisions in a collision log file. Returns a dict that for value has dicts that are
    all the cars present at a collision.
    :param collisions_file: log file of the collisions.
    :param all_cars: all the cars of the simulation.
    :return: dict that for keys has an int (from 0 and on) and for value has another dict, that for key has a car name
    and for value a car.
    """
    collisions_cars = {}
    collided_cars = {}
    counter = 0
    for line in collisions_file:
        collision_information = JSONDecoder().decode(line[:len(line) - 2])['message']
        collided_cars_information = collision_information["collided_cars"]
        collisions_cars[counter] = {}
        collision_cars = collisions_cars[counter]
        collided_cars[counter] = []
        for car_information in collision_information["collision_initial_conditions"]:
            collision_cars[car_information["name"]] = Car(car_information["name"],
                                                          pos_x=car_information["actual_coordinates"]["x_coordinate"],
                                                          pos_y=car_information["actual_coordinates"]["y_coordinate"],
                                                          direction=car_information["actual_coordinates"]["direction"],
                                                          lane=car_information["lane"],
                                                          intention=car_information["intention"],
                                                          creation_time=car_information["creation_time"])
            if collision_cars[car_information["name"]].get_name() == collided_cars_information[0]["name"] or collision_cars[car_information["name"]].get_name() == collided_cars_information[1]["name"]:
                collided_cars[counter].append(collision_cars[car_information["name"]])
        for car_information in collision_information["collision_initial_conditions"]:
            if car_information["following"] in collision_cars.keys():
                collision_cars[car_information["name"]].set_following(True)
                collision_cars[car_information["name"]].set_following_car_message(
                    Message(collision_cars[car_information["following"]]))
            else:
                collisions_cars[counter][car_information["name"]].set_following_car_message(
                    Message(all_cars[car_information["following"]]))
        counter += 1
    return collisions_cars, collided_cars
