def default_controller(car):
    """
    Default controller of a car. It only commands the car to accelerate to maximum speed and go.
    :param car: car to be controlled.
    :return: inputs to move the car.
    """
    car.set_acceleration(3)
    if car.get_intention() == "r":
        if car.virtual_distance() >= 248:
            if car.get_direction_variation() < 90:
                car.set_direction(car.get_direction() - 15)
    elif car.get_intention() == "l":
        if car.virtual_distance() >= 281:
            if car.get_direction_variation() < 90:
                car.set_direction(car.get_direction() + 15)
