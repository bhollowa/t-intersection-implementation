def default_controller(inputs, car):
    """
    Default controller of a car. It only commands the car to accelerate to maximum speed and go.
    :param inputs: old inputs.
    :param car: car to be controlled.
    :return: inputs to move the car.
    """
    r, l, u, d = inputs
    return r, l, u + 4, d
