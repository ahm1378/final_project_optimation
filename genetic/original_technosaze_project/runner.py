import json

import numpy as np
from Final_cost import FinalCost
from beam_operation import ColBeam
from checkmodel import CheckModel
# # pre = PreProcces(etabs_object=my_etabs)
from cost import Cost
from create import my_etabs


# from fobj import fobj
# from prepare_data import final_cost
# from preprocces import PreProcces
# from test_etabs import column_var, beam_var, bound
#
# nV = (len(column_var)+len(beam_var))*2
# Lb = np.array([-3]*nV)  # upper bound limit for variable
# Ub = np.array([+3]*nV)  # lower bound limit
# nV = len(Lb)  # number of variables
# nL = 50  # number of population
# maxNFEs = 10000

check = CheckModel(etabs_object=my_etabs,flag_design=False,flag_analysis=False)

# general_data = pre.general_frame_data()
# beam_name, column_name =pre.create_init_section(general_data=general_data)
# # #
# ho = Cost(etabs_object=my_etabs)
general_data = check.general_frame_data(flag_group=True)
print(check.etabs.PropFrame.GetRectangle("B40X55"))
col_u = check.get_columns_unique_names(general_frame_data=general_data)
beam_u = check.get_beams_unique_names(general_frame_data=general_data)
# full_normal = ho.get_normal_frame_data_index_id(general_frame_data=general_data)
# full_normal_data = ho.get_full_frame_data_index_id(general_frame_data=general_data, result=full_normal)
# # # # result = pre.get_normal_frame_data_index_id(general_frame_data=general_data)
unique_names = check.get_unique_names(general_frame_data=general_data)
labels = check.get_labels(general_frame_data=general_data)
co=Cost(etabs_object=my_etabs)

# beam_op = ColBeam(etabs_object=my_etabs,flag_design=False,flag_analysis=False)
# print(beam_op.columns_dimension(general_data=general_data))
# x = check.get_section_names(general_data)


# bound=[45, 45, 45, 45, 45, 45, 45.0, 45.0, 45, 45, 45, 45, 45, 45, 45.0, 45.0, 45, 45, 45.0, 45.0, 45, 45, 45, 45, 45.0, 45.0, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 50, 55.0, 40.0, 55.0, 40.0, 55.0, 40.0, 55.0, 40.0, 55.0, 45.0, 55.0, 40.0, 55.0, 35.0, 55.0, 40.0, 55.0, 40.0, 55.0, 35.0, 55.0, 40.0, 55.0, 40.0, 55.0, 40.0, 55.0, 40.0, 55.0, 40.0, 50.0, 40.0, 55.0, 40.0, 55.0, 40.0, 55.0, 35.0, 55.0, 40.0, 55.0, 40.0, 55.0, 40.0, 55.0, 40.0, 55.0, 40.0, 45.0, 35.0, 40.0, 40.0, 45.0, 35.0, 45.0, 35.0, 45.0, 35.0, 40.0, 40.0]
# beam_op.col_beam_width(general_data=general_data)
# beam_name, column_name = pre.create_init_section(general_data=general_data)
# print(beam_op.columns_dimension(general_data=general_data))

sections = check.get_section_names(general_frame_data=general_data)
# np_sect = np.array(sections)
# sec_string = np.array2string(np_sect, formatter={'float_kind': lambda x: "%.2f" % x})
# with open("section.txt", 'a') as f:
#     f.write(sec_string)
#     f.write('\n')
# # # # print(pre.get_underneath_column(result))
# # # id_under = pre.get_underneath_column(full_normal)
# # # # final_id_under = pre.sort_by_z(columns_under=id_under)
# # # # print(pre.check_underneath_column(id_underneath=id_under))
# # # # # print(pre.get_modal_period())
# # #
# # # # print(pre.col_beam_width(general_data=general_data))
# # # # location = ho.get_location(general_data=general_data)
# # # # print(ho.check_os_error(general_data=general_data, location=location))
# # result = ho.get_normal_frame_data_index_id(general_frame_data=general_data)
# # full_normal_data =ho.get_full_frame_data_index_id(general_frame_data=general_data, result=result)
# # # #
# # # rebar = ho.total_value_rebar(full_data=full_data, beams=beam_u, columns=col_u)
# # # conc = Concerete_Cost(etabs_object=my_etabs)
# # # volume = conc.concrete_volume(full_data=full_data)
# # # final_price = conc.concrete_total_price(volume)
# # # cst = FrameWorkCost(etabs_object=my_etabs, full_frame_data=full_data)
# # # final_cst = cst.total_value_frame()
# # #
# # # location = ho.get_location(beams=beam_u)
# # # ho.os_error_column(columns=col_u)
# # # ho.os_error_beam(beams=beam_u)
# # # id_under = pre.get_underneath_column(full_normal)
# # # final_id_under = pre.sort_by_z(columns_under=id_under)
# # # pre.check_underneath_column(id_underneath=id_under)
# # # pre.beam_depth_inline(general_data=general_data)
# # # pre.torsional_irregularity()
# # from prepare_data import final_cost
# #
#
# # print(check.get_story_drift_tables(unique_name=unique_names,labels=labels))
#
#
# full_data = check.get_full_frame_data_index_id(general_frame_data=general_data, result=full_normal_data)
# frame = FrameWorkCost(etabs_object=my_etabs, full_frame_data=full_data)
# frame_price = frame.total_value_frame()
# # conc = Concerete_Cost(etabs_object=my_etabs)
# # volume_conc = conc.concrete_volume(full_data=full_data)
# # conc_price = conc.concrete_total_price(volume_conc)
# # print(conc_price+frame_price)
# # beam_name, column_name = pre.create_init_section(general_data=general_data)
# cal = ColBeam(etabs_object=my_etabs, flag_design=False, flag_analysis=False)
# x= Cost(etabs_object=my_etabs)
# print(my_etabs.ResponseSpectrum.GetLoads("SPECX"))
# print(my_etabs.ResponseSpectrum.SetLoads("SPECX", 1, ['U1'], ["2800V4S2"], [1.2],['Global'],[0.0]))
# id_under = cal.get_underneath_column(full_normal_data=full_normal_data)
# id_under_z = cal.sort_by_z(columns_under=id_under)
# print("id_under_z", id_under_z)
# cal.check_underneath_column(id_underneath=id_under_z)
# x = cal.beam_depth_inline(general_data=general_data)
# y = cal.col_beam_width(general_data=general_data)
grou = check.get_unique_names_group("All Frames")[2]
gene = check.etabs.FrameObj.GetLabelNameList()
# pre = PreProcces(etabs_object=my_etabs)
# full_normal_data = pre.get_normal_frame_data_index_id(general_frame_data=general_data)
# unique_names = pre.get_unique_names(general_frame_data=general_data)
# column_id = pre.get_columns_unique_names(general_frame_data=general_data)
# beam_id = pre.get_beams_unique_names(general_frame_data=general_data)
# labels = pre.get_labels(general_frame_data=general_data)
# print(cal.get_story_drift_tables(unique_name=unique_names,labels=labels))
# print(len(x))
# print(len(check.get_beams_unique_names(general_frame_data=general_data)))
# print(len(check.get_columns_unique_names(general_frame_data=general_data)))

a=[-2, -2, -2,  1,  1, -3, -1, -1,  1,  1 ,-1,  2, -2, -3, -3, -2, -3, -2,  1, -3, -3, -2, -3,  0,
-2 ,-1 ,-3 ,-1 ,-3 ,-3 ,-1, -3 ,-2 ,-3 ,-3  ,1 ,-2 ,-3 ,-3 ,-3 ,-3 ,-1, -2, -3, -3, -3 , 1  ,2,
 0  ,2 ,-3 , 0,  1, -2, -2, -2,  0,  1,  2, -1, -1, -1,  1, -3,  0,  1,  1,  2, -2, -3,  1, -3,
-1 ,-2]

f = FinalCost(etabs_object=my_etabs)
full_normal_data = f.get_normal_frame_data_index_id(general_frame_data=general_data)

full_data = f.get_full_frame_data_index_id(general_frame_data=general_data,result=full_normal_data)
#print('Concrete cost',f.get_conc_cost(beam_names=beam_u,column_names=col_u,full_data=full_data))
#print("rebar weight is ",f.get_rebar_weight(beam_names=beam_u,column_names=col_u,full_data=full_data)
      #)
#print("rebar cost is ",f.get_rebar_cost(beam_names=beam_u,column_names=col_u,full_data=full_data)
     # )#
#print('frame work cost',f.get_framework_cost(beam_names=beam_u,column_names=col_u,full_data=full_data))
#p#rint("total_cost is ",f.get_total_cost(beam_names=beam_u, column_names=col_u , full_data=full_data))
co = ColBeam(etabs_object=my_etabs)
# print(co.col_beam_width(general_data=general_data))
# cal.run_model()
# torition = cal.torsional_irregularity()
# print(torition)
# print(f.get_columns_points(general_data=general_data))
point = '60'
print(co.group_column_beam(full_data=full_data, point='60'))






