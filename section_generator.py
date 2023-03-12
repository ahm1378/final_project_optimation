import math

from lower_band import find_lower

min_section = find_lower(5, 1, 1)


def create_possible_section(max_possible, w, h, kind):
    increment = int((max_possible - w) / 5)
    result = {}
    columns = [(w + i * 5) for i in range(0, increment + 1)]
    for u in columns:
        limited_upper = 10 * u / 5
        limited_lower = 5 * u / 10
        result[u] = [i for i in range(max(h, math.ceil(limited_lower / 5) * 5),
                                      min(max_possible, math.ceil(limited_upper / 5) * 5)+5, 5)]
    sections = []
    for k in result.keys():
        for i in result[k]:
            sections.append('{}{}X{}'.format(kind, k, i))
    return sections


cw, ch = min_section['columns_minimum_width'], min_section['columns_minimum_height']
bw, bh = min_section['beams_minimum_width'], min_section['beams_minimum_height']
columns_generation = create_possible_section(max_possible=60, w=30,
                                  h=30, kind='C')
beams_generation = create_possible_section(max_possible=60, w=25,
                                h=55, kind='B')
print(columns_generation)