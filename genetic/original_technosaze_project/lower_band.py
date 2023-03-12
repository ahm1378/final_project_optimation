from fire_rules import plasticity, fire


def find_lower(number_of_story, type, platicity_type):
    result_fire = fire(number_of_stories=number_of_story, type=type)
    result_plastic = plasticity(type_plasticity=platicity_type)
    final_result = {
        "columns_minimum_width": max(result_fire['columns_minimum_width'], result_plastic['columns_minimum_width']),
        "columns_minimum_height":  max(result_fire['columns_minimum_height'], result_plastic['columns_minimum_height']),
        "beams_minimum_width":  max(result_fire['beams_minimum_width'], result_plastic['beams_minimum_width']),
        "beams_minimum_height":  max(result_fire['beams_minimum_height'], result_plastic['beams_minimum_height'])
    }
    return final_result
