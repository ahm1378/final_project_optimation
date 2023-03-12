import operator
from itertools import groupby

from checkmodel import CheckModel
from constants import Data_25
from runetabs import RunConcrete
import numpy as np

class ColBeam(CheckModel):
    def beams_dimension(self, general_data):
        name_id = self.get_beams_unique_names(general_frame_data=general_data)
        result = []
        width = []
        height = []
        for i in name_id:
            result.append(self.etabs.FrameObj.GetSection(i)[0])
        for j in result:
            width.append(j[1:3])
        for k in result:
            height.append(k[4:6])
        section = list(zip(width, height))
        final = dict(zip(name_id, section))
        return final

    def columns_dimension(self, general_data):
        name_id = self.get_columns_unique_names(general_frame_data=general_data)
        result = []
        width = []
        height = []
        for i in name_id:
            result.append(self.etabs.FrameObj.GetSection(i)[0])
        for j in result:
            width.append(j[1:3])
        for k in result:
            height.append(k[4:6])
        section = list(zip(width, height))
        final = dict(zip(name_id, section))
        return final

    def get_beam_inlines(self,general_data,beam_unique_names):
        get_beams_points = self.get_beam_points(general_data)[0]
        joints_data = self.etabs.PointObj.GetAllPoints()
        joints_unique_names = joints_data[1]
        joints_x = joints_data[2]
        joints_y = joints_data[3]
        joints_z = joints_data[4]
        joints_story = []
        for r in range(len(joints_unique_names)):
            story = []
            for t in range(len(joints_unique_names)):
                if joints_z[r] == joints_z[t]:
                    story.append(joints_unique_names[t])
            if story not in joints_story:
                joints_story.append(story)
        align_x = []
        align_y = []
        for join in joints_story:
            temp_x = {}
            temp_y = {}
            for w in join:
                x_core = joints_x[joints_unique_names.index(w)]
                y_core = joints_y[joints_unique_names.index(w)]
                try:
                    temp_x[x_core].append(w)
                except:
                    temp_x[x_core] = [w]
                try:
                    temp_y[y_core].append(w)
                except:
                    temp_y[y_core] = [w]
            align_y.append(temp_x)
            align_x.append(temp_y)
        beam_align_x = []
        for z in range(len(align_x)):
            k = list(align_x[z].keys())
            bb = {}
            for c in range(len(k)):
                bb[k[c]] = []
            beam_align_x.append(bb)
        beam_align_y = []
        for z1 in range(len(align_y)):
            k1 = list(align_y[z1].keys())
            bb1 = {}
            for c1 in range(len(k1)):
                bb1[k1[c1]] = []
            beam_align_y.append(bb1)
        for q in range(len(beam_unique_names)):
            beam = beam_unique_names[q]
            beam_joints = [get_beams_points[q][0], get_beams_points[q][1]]
            joints_coord = [self.etabs.PointObj.GetCoordCartesian(beam_joints[0]), self.etabs.PointObj.GetCoordCartesian(beam_joints[1])]
            if joints_coord[0][1] == joints_coord[1][1]:
                for align in align_x:
                    keys = list(align.keys())
                    for key in keys:
                        if (beam_joints[0] in align[key]) and (beam_joints[1] in align[key]):
                            beam_align_x[align_x.index(align)][key].append(beam)
            elif joints_coord[0][0] == joints_coord[1][0]:
                for align in align_y:
                    keys = list(align.keys())
                    for key in keys:
                        if (beam_joints[0] in align[key]) and (beam_joints[1] in align[key]):
                            beam_align_y[align_y.index(align)][key].append(beam)
        beams_inline = []
        for zz in range(len(beam_align_x)):
            kk = list(align_x[zz].keys())
            for cc in range(len(kk)):
                if len(beam_align_x[zz][kk[cc]]) > 1:
                    beams_inline.append(beam_align_x[zz][kk[cc]])
        for zz1 in range(len(beam_align_y)):
            kk1 = list(align_y[zz1].keys())
            for cc1 in range(len(kk1)):
                if len(beam_align_y[zz1][kk1[cc1]]) > 1:
                    beams_inline.append(beam_align_y[zz1][kk1[cc1]])
        nested_beam = set([x for l in beams_inline for x in l])
        single_beams = list(set(beam_unique_names)-nested_beam)
        for k in single_beams:
            beams_inline.append([k])
        return beams_inline

    def set_beam_depth_inline(self, general_data):
        beams_dimension = self.beams_dimension(general_data)
        beams_inline = self.get_beam_inlines(general_data=general_data)
        beams_inline_dimension = []
        for beams in beams_inline:
            temp_b_dim = []
            for beam in beams:
                temp_b_dim.append(int(beams_dimension[beam][1]))
            beams_inline_dimension.append(temp_b_dim)
        beams_inline_max_dimension = []
        for count20 in beams_inline_dimension:
            beams_inline_max_dimension.append(max(count20))
        result1 = 0
        result2 = 0
        for count21 in range(len(beams_inline)):
            for count22 in range(len(beams_inline[count21])):
                beam_name = beams_inline[count21][count22]
                if int(beams_dimension[beam_name][1]) < beams_inline_max_dimension[count21]:
                    result1 = result1 + 1
                    prop_name = 'B{}X{}'.format(beams_inline_max_dimension[count21], beams_dimension[beam_name][0])
                    self.etabs.SapModel.SetModelIsLocked(False)
                    result2 = result2 + self.etabs.FrameObj.SetSection(beam_name, prop_name)
        if (result1 > 0) and (result2 == 0):
            return 0
        elif result1 == 0:
            return 1
        elif (result1 > 0) and (result2 > 0):
            return -1

    def col_beam_width_temp(self, general_data):
        beam_unique_names = self.get_beams_unique_names(general_frame_data=general_data)
        column_unique_names = self.get_columns_unique_names(general_frame_data=general_data)
        get_beams_points = self.get_beam_points(general_data)[0]
        beams_dimension = self.beams_dimension(general_data)
        result1 = 0
        result2 = 0
        count =0
        for elem in range(len(beam_unique_names)):
            b_unique_name = beam_unique_names[elem]
            b_joints = [get_beams_points[elem][0], get_beams_points[elem][1]]
            bi_connect = self.etabs.PointObj.GetConnectivity(b_joints[0])
            bj_connect = self.etabs.PointObj.GetConnectivity(b_joints[1])
            coord_i = self.etabs.PointObj.GetCoordCartesian(b_joints[0])
            coord_j = self.etabs.PointObj.GetCoordCartesian(b_joints[1])
            bi_connected = []
            bj_connected = []
            beam_width = int(beams_dimension[b_unique_name][1])
            beam_depth = int(beams_dimension[b_unique_name][0])
            for q in range(len(bi_connect[1])):
                if bi_connect[1][q] == 2:
                    bi_connected.append(bi_connect[2][q])
            for w in range(len(bj_connect[1])):
                if bj_connect[1][w] == 2:
                    bj_connected.append(bj_connect[2][w])
            bi_column_connected = []
            bj_column_connected = []
            for e in range(len(bi_connected)):
                if bi_connected[e] in column_unique_names:
                    bi_column_connected.append(bi_connected[e])
            for r in range(len(bj_connected)):
                if bj_connected[r] in column_unique_names:
                    bj_column_connected.append(bj_connected[r])
            column_width_i = []
            for t in range(len(bi_column_connected)):
                angle_i = self.etabs.FrameObj.GetLocalAxes(bi_column_connected[t])[0]

                column_dimension_i = self.columns_dimension(general_data)[bi_column_connected[t]]
                if coord_i[0] == coord_j[0]:
                    if angle_i == 0.0:
                        column_width_i.append(int(column_dimension_i[0]))
                    elif angle_i == 90.0:
                        column_width_i.append(int(column_dimension_i[1]))
                elif coord_i[1] == coord_j[1]:
                    if angle_i == 0.0:
                        column_width_i.append(int(column_dimension_i[1]))
                    elif angle_i == 90.0:
                        column_width_i.append(int(column_dimension_i[0]))
            if len(column_width_i) > 0:
                column_width_i = max(column_width_i)
            column_width_j = []
            for t in range(len(bj_column_connected)):
                angle_j = self.etabs.FrameObj.GetLocalAxes(bj_column_connected[t])[0]
                col_unique_name = bj_column_connected[t]
                column_dimension_j = self.columns_dimension(general_data)[bj_column_connected[t]]
                if coord_i[0] == coord_j[0]:
                    if angle_j == 0.0:
                        column_width_j.append(int(column_dimension_j[0]))
                    elif angle_j == 90.0:
                        column_width_j.append(int(column_dimension_j[1]))
                elif coord_i[1] == coord_j[1]:
                    if angle_j == 0.0:
                        column_width_j.append(int(column_dimension_j[1]))
                    elif angle_j == 90.0:
                        column_width_j.append(int(column_dimension_j[0]))
            if len(column_width_j) > 0:
                column_width_j = max(column_width_j)

            if (isinstance(column_width_i, int)) and (isinstance(column_width_j, int)):
                column_width = min(column_width_i, column_width_j)
            elif isinstance(column_width_i, int):
                column_width = column_width_i
            elif isinstance(column_width_j, int):
                column_width = column_width_j
            else:
                column_width = []
            if isinstance(column_width_i, int):
                if beam_width > column_width*0.75:

                    # print(beam_width,column_width)
                    result1 = result1 + 1
                    section = self.etabs.FrameObj.GetSection(col_unique_name)

                    prop_name = 'B{}X{}'.format(column_width*0.75, 55)
                    self.etabs.SapModel.SetModelIsLocked(False)

                    result2 = result2 + self.etabs.FrameObj.SetSection(b_unique_name, prop_name)
        if (result1 > 0) and (result2 == 0):
            return 0
        elif result1 == 0:
            return 1
        elif (result1 > 0) and (result2 > 0):
            return -1

    def col_beam_width(self, general_data, full_data, height=55, increase = False):
        col_points = self.get_columns_points(general_data=general_data)[0]
        z = 0
        for cal in col_points:
            for i in range(2):
                point_1 = cal[i]
                point_1_info = self.group_column_beam(full_data=full_data, point=point_1)
                for elms in point_1_info:
                    key_col = list(elms.keys())[0]
                    key_beam = list(elms.keys())[1]
                    if elms[key_beam]['width'] > elms[key_col]['width']:
                        if not increase:
                            new_beam_width = int(elms[key_col]['width'])
                            section_name = 'B{}X{}'.format(new_beam_width, height)
                            z = self.etabs.FrameObj.SetSection(key_beam, section_name)

                        else:
                            new_col_width = int(elms[key_beam]['width'])
                            col_height = elms[key_col]['height']
                            section_name = 'C{}X{}'.format(col_height, new_col_width)
                            z = self.etabs.FrameObj.SetSection(key_col, section_name)
        return z









    def group_column_beam(self, full_data, point):
        point_info = self.etabs.PointObj.GetConnectivity(point)
        n_objects = point_info[0]
        result = []
        all_types = point_info[1]
        ids = point_info[2]
        columns = []
        beams = []
        for t in range(n_objects):
            if all_types[t] == 2:
                if full_data[ids[t]]['frame_type'] == 'Column':
                    columns.append(ids[t])
                elif full_data[ids[t]]['frame_type'] == 'Beam':
                    beams.append(ids[t])
        for c in columns:
            for b in beams:
                dict_temp = {c: {
                    'type': full_data[c]['frame_type'],
                    'section': full_data[c]['section'],
                    'height': full_data[c]['height'],
                    'width': full_data[c]['width']
                }, b: {
                    'section': full_data[b]['section'],
                    'height': full_data[b]['height'] ,
                    'width': full_data[b]['width']}
                }
                result.append(dict_temp)
        return result
    def ldh_control(self, general_frame_data):
        number = self.etabs.Story.GetStories()[0]
        name_id = self.get_normal_frame_data_index_id(general_frame_data)
        input_dim = []
        width_org = []
        for i in range(0, number):
            ele = int(input('please enter your diameter: '))
            input_dim.append(ele)
        for j in input_dim:
            width_org.append(Data_25[j][1])
        result_y = {}
        result_x = {}
        elev = []
        for i in name_id.keys():
            if name_id[i]['frame_type'] == 'Column':
                try:
                    result_y[(name_id[i]['y1'])].append(i)
                except:
                    result_y[(name_id[i]['y1'])] = []
        maximum_y = max(result_y.items())
        minimum_y = min(result_y.items())
        grid = list(result_y.keys())[1:-1]
        for k in name_id.keys():
            for n in range(len(grid)):
                if name_id[k]['frame_type'] == 'Column' and name_id[k]['y1'] == grid[n]:
                    try:
                        result_x[(name_id[k]['x1'])].append(k)
                    except:
                        result_x[(name_id[k]['x1'])] = []
        maximum_x = max(result_x.items())
        minimum_x = min(result_x.items())
        acceptable = []
        acceptable_2 = []
        for i in maximum_x, maximum_y, minimum_x, minimum_y:
            acceptable.append(i[1])
        for l in acceptable:
            for t in l:
                elev.append(name_id[t]['z1'])
        for i in acceptable:
            for q in i:
                acceptable_2.append(q)
        together = dict(zip(acceptable_2, elev))
        sorting = {k: v for k, v in sorted(together.items(), key=lambda item: item[1])}
        by_value = operator.itemgetter(1)
        final = [dict(g) for k, g in groupby(sorted(sorting.items(), key=by_value), by_value)]
        accept_id = []
        width_now = []
        for h in final:
            accept_id.append(list(h.keys()))
        for ac in accept_id:
            temp = []
            for w in ac:
                temp.append(self.etabs.FrameObj.GetSection(w)[0][1:3])
            width_now.append(temp)
        for i in range(len(width_now)):
            limit = width_org[i]
            t = [p for p in width_now[i] if int(p) > limit]
            if len(t) > 0:
                return -1
        return True

    def modify_ldh(self, general_frame_data):
        number = self.etabs.Story.GetStories()[0]
        name_id = self.get_normal_frame_data_index_id(general_frame_data)
        input_dim = []
        width_org = []
        for i in range(0, number):
            ele = int(input('please enter your diameter: '))
            input_dim.append(ele)
        for j in input_dim:
            width_org.append(Data_25[j][1])
        result_y = {}
        result_x = {}
        elev = []
        for i in name_id.keys():
            if name_id[i]['frame_type'] == 'Column':
                try:
                    result_y[(name_id[i]['y1'])].append(i)
                except:
                    result_y[(name_id[i]['y1'])] = []
        maximum_y = max(result_y.items())
        minimum_y = min(result_y.items())
        grid = list(result_y.keys())[1:-1]
        for k in name_id.keys():
            for n in range(len(grid)):
                if name_id[k]['frame_type'] == 'Column' and name_id[k]['y1'] == grid[n]:
                    try:
                        result_x[(name_id[k]['x1'])].append(k)
                    except:
                        result_x[(name_id[k]['x1'])] = []
        maximum_x = max(result_x.items())
        minimum_x = min(result_x.items())
        acceptable = []
        acceptable_2 = []
        for i in maximum_x, maximum_y, minimum_x, minimum_y:
            acceptable.append(i[1])
        for l in acceptable:
            for t in l:
                elev.append(name_id[t]['z1'])
        for i in acceptable:
            for q in i:
                acceptable_2.append(q)
        together = dict(zip(acceptable_2, elev))
        sorting = {k: v for k, v in sorted(together.items(), key=lambda item: item[1])}
        by_value = operator.itemgetter(1)
        final = [dict(g) for k, g in groupby(sorted(sorting.items(), key=by_value), by_value)]
        accept_id = []
        for h in final:
            accept_id.append(list(h.keys()))
        for ac in range(len(accept_id)):
            limit = width_org[ac]
            for p in accept_id[ac]:
                section_geo = self.etabs.FrameObj.GetSection(p)
                if int(section_geo[0][1:3]) < limit:
                    depth = int(section_geo[0][4:6])
                    width = limit
                    prop_name = 'C{}X{}'.format(depth, width)
                    self.etabs.SapModel.SetModelIsLocked(False)
                    self.etabs.FrameObj.SetSection(p, prop_name)