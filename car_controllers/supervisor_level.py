from car_controllers.deafult_controller import default_controller
from car_controllers.follower_controller import follower_controller


def supervisor_level(new_cars, old_cars, attack=False):
    """
    Function that emulates the functioning of the supervisor level of the T-intersection coordination algorithm.
    For every car in new_cars, the functions checks, from the last car to the first in the list old_cars, if the new car
    crosses its path with an old car. If the paths cross, the new car follows that old car and a follower controller
    is assigned to it, and the new car is added to the list of followers of the old_car.
    If the new car does not cross path with any other car, the default controller is assigned to it.
    :param new_cars: list of new cars in the intersection
    :param old_cars: old cars in the intersection
    :param attack: if true, all cars will be set default controller, driving at maximum speed.
    """
    for new_car in new_cars:
        new_car.set_old()
        if not attack:
            for i in range(len(old_cars)):
                if new_car.cross_path(old_cars[len(old_cars)-(i+1)]):
                    old_cars[len(old_cars) - (i + 1)].add_follower(new_car)
                    new_car.set_controller(follower_controller)
                    old_cars.append(new_car)
                    new_car.start_following()
                    break
            if not new_car.follow:
                old_cars.append(new_car)
                new_car.set_controller(default_controller)
        else:
            old_cars.append(new_car)
            new_car.set_controller(default_controller)