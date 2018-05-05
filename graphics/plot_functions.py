import json
import plotly.plotly as py
import plotly.graph_objs as go


def collisions_per_number_of_cars(file_location):
    """
    Plot the number of collisions per car present in the intersection at the
    collision moment.
    :param file_location: absolute path to the file to read. The file must be
        in json format.
    :return: url to plot.ly with the interactive graph
    """
    reading_file = open(file_location)
    file_string = '['
    for line in reading_file:
        file_string += line
    reading_file.close()
    file_string = file_string[:len(file_string)-2] + ']'
    json_data = json.JSONDecoder().decode(file_string)
    x = []
    y = []
    collision_dict = {}

    for value in json_data:
        if "collision_code" in value["message"]:
            number_of_cars = len(
                value["message"]["collision_initial_conditions"]
            )
            if number_of_cars not in collision_dict:
                collision_dict[number_of_cars] = 0
            collision_dict[number_of_cars] += 1

    for key in collision_dict:
        x.append(key)
        y.append(collision_dict[key])
    trace0 = go.Scatter(x=x, y=y, mode='markers', name='cars in collition')
    data = [trace0]
    return py.plot(data, filename='prueba')
