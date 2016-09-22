def follower_controller(inputs, car):
    r, l, u, d = inputs
    if car.get_message() is not None:
        if car.distance_to_center() - car.get_message().distance_to_center() - car.absolute_speed * 60 < 0:
            return r, l, u, d - 5

    return r, l, u + 8, d
