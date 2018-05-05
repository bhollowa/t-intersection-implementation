from pygame.locals import KEYDOWN, K_RIGHT, K_LEFT, K_UP, K_DOWN


def car_user_input(user_inputs, actual_values):
    """
    Function so a user can move a car with the keyboard.
    :param user_inputs: pygame inputs.
    :param actual_values: actual values of the right, left, up and down
        variables,
    :return: updated values.
    """
    k_right, k_left, k_up, k_down = actual_values
    for event in user_inputs:
        if not hasattr(event, 'key'):
            continue
        down = event.type == KEYDOWN     # key down or up?
        if event.key == K_RIGHT:
            k_right = down * -5
        elif event.key == K_LEFT:
            k_left = down * 5
        elif event.key == K_UP:
            k_up = down * 2
        elif event.key == K_DOWN:
            k_down = down * -2
    return k_right, k_left, k_up, k_down
