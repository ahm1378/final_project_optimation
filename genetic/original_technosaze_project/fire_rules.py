

def fire(number_of_stories,type):
    fire_time = 0
    # type1:omumy
    # type2:khososy
    # type3:khososy more than 300
    # type 4:spetial

    columns_minimum_width = 25
    columns_minimum_height = 25
    beams_minimum_width = 20
    beams_minimum_height = 20

    if type == 2 and 2 < number_of_stories < 5:

        columns_minimum_width = 20
        columns_minimum_height = 20
        beams_minimum_width = 20
        beams_minimum_height = 20

    if type == 2 and 6 < number_of_stories < 10:

        columns_minimum_width = 25
        columns_minimum_height = 25
        beams_minimum_width = 20
        beams_minimum_height = 20
    if type == 2 and 11 < number_of_stories < 20:

        columns_minimum_width = 30
        columns_minimum_height = 30
        beams_minimum_width = 25
        beams_minimum_height = 25
    if type == 3:

        columns_minimum_width = 35
        columns_minimum_height = 35
        beams_minimum_width = 25
        beams_minimum_height = 25
    if type == 4:

        columns_minimum_width = 45
        columns_minimum_height = 45
        beams_minimum_width = 35
        beams_minimum_height = 35
    minimum_fire = {
        "columns_minimum_width": columns_minimum_width,
        "columns_minimum_height": columns_minimum_height,
        "beams_minimum_width": beams_minimum_width,
        "beams_minimum_height": beams_minimum_height

    }
    return minimum_fire


def plasticity(type_plasticity):
    columns_minimum_width = 25
    columns_minimum_height = 25
    beams_minimum_width = 25
    beams_minimum_height = 25
    # type1:normal
    # type2:spetcial
    # type3:low
    if type_plasticity == 1:
        columns_minimum_width = 25
        columns_minimum_height = 25
        beams_minimum_width = 25
        beams_minimum_height = 25
    if type_plasticity == 2:
        columns_minimum_width = 30
        columns_minimum_height = 30
        beams_minimum_width = 25
        beams_minimum_height = 25
    result = {
        "columns_minimum_width": columns_minimum_width,
        "columns_minimum_height": columns_minimum_height,
        "beams_minimum_width": beams_minimum_width,
        "beams_minimum_height": beams_minimum_height
    }

    return result

