# arm related method

# arm data
# format:   0 null null null null null null                 do nothing
#           1 left(x y z) right(x,y,z)                      cartesian move
#           2 type file_name null null null null            build_in_move
#             type = 1 : arm init_shutdown
#             type = 2 : arm init_work
#             type = 3 : arm movement according to file_name (non-music)
#             type = 4 : arm movement according to file_name (music)
#             type = 5 : arm start record trajectory into file_name
#             type = 6 : arm end record trajectory
#           3 switch null null null null null               arm_switch
#             switch = 1 : left hand enable
#             switch = 2 : right hand enable
#             switch = 3 : both hands enable


def arm_status(mode="both"):
    data_arms = {
        "left":     [3, 1, 0, 0, 0, 0, 0],
        "right":    [3, 2, 0, 0, 0, 0, 0],
        "both":     [3, 3, 0, 0, 0, 0, 0]
        # to be continued
        # .......
    }.get(mode)
    return data_arms


def arm_close_work():
    data_arms = [11, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    return data_arms


def arm_open_work():
    data_arms = [12, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    return data_arms


def head_move(xy, z):
    data_arms = [10, 0, 0, 0, 0, 0, 0, 0, 0, 0,  1, xy, z]
    return data_arms


def head_down():
    data_arms = [10, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    return data_arms


def arm_last_trajectory():
    data_arms = [2, './data/arm_trajectory/a_word', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    return data_arms


def arm_move_non_music(file_name=None):
    data_arms = [2, 3, file_name, 0, 0, 0, 0]
    return data_arms


def arm_move_music(file_name=None):
    if file_name == 'Music:Music_1':
        data_arms = [5, './data/music/tonghua', 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    elif file_name == 'Music:Music_2':
        data_arms = [5, './data/music/mother', 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    elif file_name == 'Music:Music_3':
        data_arms = [2, './data/arm_trajectory/eryue', 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    elif file_name == 'Music:Music_4':
        data_arms = [2, './data/arm_trajectory/luoshen', 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    else:
        data_arms = [2, './data/arm_trajectory/zhu', 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    return data_arms


def arm_record_trajectory():
    data_arms = [3, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    return data_arms


def arm_end_record_trajectory():
    data_arms = [4, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
    return data_arms


def arm_cartesian_move(mode):

    data_arms = {
            "up":    [10, 0, 0, 0, 0, -1, 1],
            "down":  [10, 0, 0, 0, 0, 1, 1],
            "out":   [10, 0, 0, 0, 0, 0, 1],
            "in":    [10, 0, 0, 0, 0, 0, 0],
            "left":  [10, 0, 0, 0, -1, 0, 1],
            "right": [10, 0, 0, 0, 1, 0, 1]
            # to be continued
            # .......
        }.get(mode)

    return data_arms


