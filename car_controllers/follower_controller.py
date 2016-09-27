from car_controllers.deafult_controller import default_controller


def follower_controller(inputs, car):
    """
    Controller of a car that is following some other. If the car is more than 3/2 headway distance to the center than
    the distance to the center of its following car, the car will accelerate, otherwise it will stay at the following
    car speed.
    :param inputs: inputs of the car.
    :param car: car to bre controlled
    :return: new inputs of the car.
    """
    headway = 280
    r, l, u, d = inputs
    if not car.follow:
        car.set_controller(default_controller)
    if car.get_message() is not None:
        if car.distance_to_center() - car.get_message().distance_to_center() < headway:
            car.set_speed(car.get_message().speed - 10)
            return r, l, u, d - 2
        elif car.distance_to_center() - car.get_message().distance_to_center() < headway*3/2:
            car.set_speed(car.get_message().speed)
            return r, l, u, d - 1
    return r, l, u + 1, d
