import numpy as np
import json


def create_json_file(co,name):
    all_data = co.get_full_frame_data()
    json_name = '{}'.format(name)
    json_file = open(json_name + ".json", "w")
    # magic happens here to make it pretty-printed
    json_file.write(json.dumps(all_data, indent=4, sort_keys=True))
    json_file.close()


def polygon_area(coords):
    # get x and y in vectors
    x = [point[0] for point in coords]
    y = [point[1] for point in coords]
    # shift coordinates
    x_ = x - np.mean(x)
    y_ = y - np.mean(y)
    # calculate area
    correction = x_[-1] * y_[0] - y_[-1] * x_[0]
    main_area = np.dot(x_[:-1], y_[1:]) - np.dot(y_[:-1], x_[1:])
    return 0.5 * np.abs(main_area + correction)


def check_sorted(test_list):
    flag = 0
    if (all(test_list[i+1] <= test_list[i] for i in range(len(test_list) - 1))):
        flag = 1

    # printing result
    if (flag):
        return True
    else:
        return False


def convert_df_to_dict(df):
    return df.df.to_dict('dict')