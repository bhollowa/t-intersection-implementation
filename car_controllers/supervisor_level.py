from car_controllers.deafult_controller import default_controller
from car_controllers.follower_controller import follower_controller


def supervisor_level(new_cars, old_cars):
    for new_car in new_cars:
        following = False
        for i in range(len(old_cars)):
            if new_car.cross_path(old_cars[len(old_cars)-(i+1)]):
                old_cars[len(old_cars) - (i + 1)].add_follower(new_car)
                new_car.set_controller(follower_controller)
                old_cars.append(new_car)
                following = True
                break
        if not following:
            old_cars.append(new_car)
            new_car.set_controller(default_controller)
    return []