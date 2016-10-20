from car_controllers.default_controller import default_controller


def follower_controller(car):
    """
    Controller of a car that is following some other. If the car is more than 3/2 headway distance to the center than
    the distance to the center of its following car, the car will accelerate, otherwise it will stay at the following
    car speed.
    :param car: car to bre controlled
    :return: new inputs of the car.
    """
    headway_time = 0.7
    k_p = 0.2
    k_d = 0.7
    stand_still_distance = car.get_car_length() * 4
    if not car.is_following():
        car.set_controller(default_controller)
    car_message = car.get_following_car_message()
    if car_message is not None:
        virtual_distance = car_message.virtual_distance() - car.virtual_distance()
        value_1 = -1 * car.get_control_law_value() + car_message.get_acceleration()
        value_2 = k_p * (virtual_distance - stand_still_distance - headway_time * car.get_speed())
        value_3 = k_d * ((virtual_distance - car.get_last_virtual_distance()) - headway_time * car.get_acceleration())
        control_law_derivative = (value_1 + value_2 + value_3) / headway_time
        car.set_last_virtual_distance(virtual_distance)
        car.set_control_law_value((car.get_acceleration() + control_law_derivative)%3)
        car.set_acceleration(car.get_acceleration() + control_law_derivative)
