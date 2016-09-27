def default_controller(car):
    """
    Default controller of a car. It only commands the car to accelerate to maximum speed and go.
    :param car: car to be controlled.
    :return: inputs to move the car.
    """
    return 4, 0
