from car_controllers.default_controller import default_controller


def follower_controller(car):
    """
    Controller of a car that is following some other. If the car is more than 3/2 headway distance to the center than
    the distance to the center of its following car, the car will accelerate, otherwise it will stay at the following
    car speed.
    :param inputs: inputs of the car.
    :param car: car to bre controlled
    :return: new inputs of the car.
    """
    headway = 200
    if not car.is_following():
        car.set_controller(default_controller)
    if car.get_message() is not None:
        if car.distance_to_center() - car.get_message().distance_to_center() < headway:
            car.set_speed(car.get_message().speed - 10)
            return -2, 0
        elif car.distance_to_center() - car.get_message().distance_to_center() < headway*3/2:
            car.set_speed(car.get_message().speed)
            return -1, 0
    return 1, 0
