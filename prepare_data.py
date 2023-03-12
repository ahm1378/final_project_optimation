import math

from Final_cost import FinalCost
from beam_operation import ColBeam
from concerete_cost import Concerete_Cost
from preprocces import PreProcces
from setting import my_etabs, default


from cost import Cost, FrameWorkCost




pre = PreProcces(etabs_object=my_etabs)

general_data = pre.general_frame_data(flag_group=True)
chrom_length = len(general_data['MyName'])*2
full_normal_data = pre.get_normal_frame_data_index_id(general_frame_data=general_data)
unique_names = pre.get_unique_names(general_frame_data=general_data)
column_id = sorted(pre.get_columns_unique_names(general_frame_data=general_data))
beam_id = sorted(pre.get_beams_unique_names(general_frame_data=general_data))
labels = pre.get_labels(general_frame_data=general_data)
cal = ColBeam(etabs_object=my_etabs, flag_design=False, flag_analysis=False)
##
pre = ColBeam(etabs_object=my_etabs, flag_design=False, flag_analysis=False)
id_under = pre.get_underneath_column(full_normal_data=full_normal_data)
id_under_z = pre.sort_by_z(columns_under=id_under)


def structure_cost(full_data):
    pre.run_model()
    pre.start_design()
    ho = FinalCost(etabs_object=my_etabs)
    cost = ho.get_total_cost(beam_names=beam_id,column_names=column_id,full_data=full_data)
    return cost


def get_variables():
    cal_var = cal.tip_columns(id_under=id_under_z, n_tip=2)
    beam_var = cal.get_beam_inlines(general_data=general_data, beam_unique_names=beam_id)
    return cal_var, beam_var


def final_cost(coef):
    global beam_id
    global column_id
    final_penalty_list = []
    pre = ColBeam(etabs_object=my_etabs, flag_design=False, flag_analysis=False)
    pre.etabs.SapModel.SetModelIsLocked(False)
    ho = FinalCost(etabs_object=my_etabs)
    pre.check_underneath_column(id_underneath=id_under_z)
    pre.Column_dim_checker("All Frames", delta=10)
    full_data = pre.get_full_frame_data_index_id(general_frame_data=general_data, result=full_normal_data)
    # x= pre.col_beam_width(general_data=general_data,full_data=full_data)
    # if x==-1:
    #     final_penalty_list +=[1.1]
    #     print('beams cant fix')
    full_data = pre.get_full_frame_data_index_id(general_frame_data=general_data, result=full_normal_data)
    cost = structure_cost(full_data)
    os_penalty_list = ho.os_error_beam(beams=beam_id,full_data=full_data)
    drift_penalty_list = pre.get_story_drift_tables(unique_name=unique_names, labels=labels,flag_period=False)
    final_penalty_list += list(drift_penalty_list)+list(os_penalty_list)
    if len(os_penalty_list)>0:
        print("os cant fix")
    if len(drift_penalty_list)>0:
        print("drift cant fix")
    summation = 0
    # for pe in final_penalty_list:
    #     summation += 1+(coef*max(0, p-1))

    # pre.run_model()
    # pre.start_design()
    # column_os = ho.os_error_column(columns=column_id)
    # if not column_os:
    #     print("columns _os")
    #     return 1000000000000
    # beam_os =ho.os_error_beam(beams=beam_id)
    # if not beam_os:
    #     print("beam_os_eror")
    final_cost = cost+cost*sum(final_penalty_list)*coef
    return final_cost, cost, cost*summation

