from simulations.recreate_collisions import create_cars_from_collision_json
from json import JSONDecoder
import os

log_directory = os.path.dirname(os.path.abspath(__file__)) + "/../logs/"
reading_file = open(log_directory + "collisions1.log")
file_string = "["
for line in reading_file:
    file_string += line
file_string = file_string[:len(file_string)-2] + "]"
json_collisions = JSONDecoder().decode(file_string)

collision_positions = [
    "1132", "1134", "2241", "2243", "3312", "3314", "4421", "4423"
]
positive = 0
for json_collision in json_collisions:
    ble = False
    car_dict = create_cars_from_collision_json(json_collision)
    lanes_order = ""
    for car in list(car_dict):
        lanes_order += str(car_dict[car].get_lane())
    for option in collision_positions:
        if option in lanes_order:
            ble = True
            positive += 1
            break
    if not ble:
        print json_collision
        print lanes_order
print positive, len(json_collisions)
