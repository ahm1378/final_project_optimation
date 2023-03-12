import numpy as np

from prepare_data import final_cost, general_data
from genetic_improved import pre, column_var, beam_var, first_cost


def fobj(x, bounds, Lb, Ub):
    for i in range(len(x)):
        if x[i] > Ub[i]:
            x[i]=Ub[i]
        if x[i] < Lb[i]:
            x[i]=Lb[i]
    x = [round(i) for i in x]
    pre.etabs.SapModel.SetModelIsLocked(False)
    i = 0
    for section in range(len(column_var)):
        for se in column_var[section]:
            w = int(bounds[i] + 5 * x[i])
            h = int(bounds[i + 1] + 5 * x[i+1])
            re = pre.set_section(frame_name=se, section_name="C{}X{}".format(w, h))
            if re!=0:
                print("cant assin section C{}X{}".format(w,h))
        i += 1
    for section in range(len(beam_var)):
        for se in beam_var[section]:
            w = int(bounds[i] + 5 * x[i])
            h = 55
            pre.set_section(frame_name=se, section_name="B{}X{}".format(w, h))
        i = i + 1

    cost = final_cost(10**9)
    co = np.array([cost[0], (first_cost - cost[0]) * 100 / first_cost])
    opt_perc = (first_cost - cost[0]) * 100 / first_cost
    u_x = np.array(x)
    x_string = np.array2string(u_x, formatter={'float_kind': lambda x: "%.2f" % x})
    co_string = np.array2string(co, formatter={'float_kind': lambda x: "%.2f" % x})
    if cost[0] < first_cost:
        sections = pre.get_section_names(general_frame_data=general_data)
        np_sect = np.array(sections)
        sec_string = np.array2string(np_sect, formatter={'float_kind': lambda x: "%.2f" % x})
        with open("test.txt", 'a') as f:
            f.write(x_string)
            f.write(co_string)
            f.write('\n')
    print("cost is", cost[0])
    res = [x, cost[1], cost[2]]
    return res