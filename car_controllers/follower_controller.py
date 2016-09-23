from car_controllers.deafult_controller import default_controller


def follower_controller(inputs, car):
    r, l, u, d = inputs
    if not car.follow:
        car.set_controller(default_controller)
    if car.get_message() is not None:
        if car.distance_to_center() - car.get_message().distance_to_center() < 150:
            car.set_speed(car.get_message().speed - 5)
            return r, l, u, d -15
        elif car.distance_to_center() - car.get_message().distance_to_center() < 250:
            car.set_speed(car.get_message().speed)
            return r, l, u, d
    return r, l, u + 12, d
