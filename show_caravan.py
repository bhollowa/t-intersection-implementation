from json import JSONDecoder
import pygame


screen = pygame.display.set_mode((768, 768))
not_collision_surface = pygame.Surface((50, 50))
palette = [(0, 0, 255, 0), (255, 0, 0, 0), (0, 255, 0, 255)]
not_collision_surface.fill(palette[0])
collision_surface = pygame.Surface((50, 50))
collision_surface.fill(palette[1])
size = (50, 50)

collision_string = JSONDecoder().decode('{"time":"2016-10-12 17:28:13,453", "message":{"collision_code":"34842to34845", "collision_initial_conditions":[{"name":34840,"following":34838,"lane":1,"speed":17.15,"creation_time":1476304092.08,"left_intersection_time":-1},{"name":34842,"following":34840,"lane":1,"speed":17.125,"creation_time":1476304092.4,"left_intersection_time":-1},{"name":34843,"following":34841,"lane":3,"speed":20.0,"creation_time":1476304092.54,"left_intersection_time":-1},{"name":34844,"following":34843,"lane":2,"speed":19.975,"creation_time":1476304092.71,"left_intersection_time":-1},{"name":34845,"following":34843,"lane":4,"speed":19.975,"creation_time":1476304092.84,"left_intersection_time":-1},{"name":34846,"following":34845,"lane":1,"speed":9.925,"creation_time":1476304093.01,"left_intersection_time":-1},{"name":34847,"following":34846,"lane":2,"speed":0,"creation_time":1476304093.2,"left_intersection_time":-1}],"collided_cars":[{"name":34842,"following":34840,"lane":1,"speed":17.125,"creation_time":1476304092.4,"left_intersection_time":-1},{"name":34845,"following":34843,"lane":4,"speed":19.975,"creation_time":1476304092.84,"left_intersection_time":-1}]}}')
car_follower_tuples = []
colliders = map(str, collision_string["message"]["collision_code"].split("to"))
print colliders
for car in collision_string["message"]["collision_initial_conditions"]:
    car_follower_tuples.append((car["name"], car["following"]))
leaders = []
not_leaders = []
for car_follower_tuple in car_follower_tuples:
    if not car_follower_tuple[1] in [car_follower_tuples[k][0] for k in range(len(car_follower_tuples))]:
        leaders.append(car_follower_tuple[0])
    else:
        not_leaders.append((car_follower_tuple[0], car_follower_tuple[1]))

cars = []
for i in range(len(leaders)):
    cars.append((leaders[i], pygame.Rect((700, 400 * (i + 1) / len(leaders)), size)))
for i in range(len(not_leaders)):
    for car in cars:
        if car[0] == not_leaders[i][1]:
            new_rect = pygame.Rect((car[1].left - 100, car[1].top), size)
            for carsasd in cars:
                if new_rect.colliderect(carsasd[1]):
                    new_rect.top += 50
                    carsasd[1].top -= 50
            cars.append((not_leaders[i][0], new_rect))
            break
print cars
for car in cars:
    if str(car[0]) in colliders:
        screen.blit(collision_surface, car[1])
    else:
        screen.blit(not_collision_surface, car[1])
pygame.display.update(screen.get_rect())
while True:
    continue
