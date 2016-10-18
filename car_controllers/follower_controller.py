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
    headway = car.get_car_length() * 3 + 0.5 * car.get_speed()
    if not car.is_following():
        car.set_controller(default_controller)
    car_message = car.get_following_car_message()
    if car_message is not None:
        distance_difference = car_message.virtual_distance() - car.virtual_distance()
        if distance_difference < car.get_car_length():
            car.set_speed(0)
        if distance_difference < headway:
            # car.set_speed(car_message.speed - 10)
            return -20, 0
        elif distance_difference < headway*3/2:
            # car.set_speed(car_message.speed)
            return 10, 0
    return 15, 0
