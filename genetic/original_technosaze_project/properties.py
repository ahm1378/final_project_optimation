import math
import random
import numpy as np
from logger import logger
from lower_band import find_lower
from frame_data import BaseFrame


class FrameProb(BaseFrame):

    def get_num_story(self):
        qs = self.etabs.story.GetStories()
        result = {
            'NumberStories': self.etabs.story.GetStories()[0],
            'StoryNames': self.etabs.story.GetStories()[1],
            'StoryElevations': self.etabs.story.GetStories()[2]
        }
        if not qs[-1]:
            logger.info("stories  get successfully")
        else:
            logger.warning("can't get stories name successfully")
        return result

    def get_load_pattern(self):
        return self.etabs.load_patern.GetNameList()[1]

    def get_load_type(self, load_patern):
        return self.etabs.load_patern.GetLoadType(load_patern)[0]

    def get_earthquake_force(self):
        result = []
        load_patterns = self.get_load_pattern()
        for i in range(len(load_patterns)):
            if self.get_load_type(load_patterns[i]) == 5 or self.get_load_type(load_patterns[i]) == 37:
                result.append(load_patterns[i])
        return result

    @staticmethod
    def get_frames_number(general_frame_data):
        return general_frame_data['NumberNames']

    @staticmethod
    def get_unique_names(general_frame_data):
        return general_frame_data['MyName']

    def get_section_names(self, general_frame_data):
        unique_names = self.get_unique_names(general_frame_data)
        unique_names = sorted(unique_names)
        sections = []
        for i in unique_names:
            sections.append(self.etabs.FrameObj.GetSection(i)[0])
        return sections

    def create_json_from_section(self,general_frame_data):
        unique_names = self.get_unique_names(general_frame_data)
        unique_names = sorted(unique_names)
        sections = {}
        for i in unique_names:
            sections[i] = self.etabs.FrameObj.GetSection(i)[0]
        return sections


    def get_beams_unique_names(self, general_frame_data):
        beams = []
        lentgh = self.get_frames_number(general_frame_data)
        labels = self.get_labels(general_frame_data)
        uniq_name = self.get_unique_names(general_frame_data)
        for i in range(lentgh):
            if labels[i][0] == "B":
                beams.append(uniq_name[i])
        beams = set(beams)-{'18','19'}

        return list(beams)

    def get_unique_names_group(self,group_name):
        unique_names = self.etabs.Group.GetAssignments(group_name)
        return unique_names

    def get_columns_beams_names_group(self,uniqe_name_frames):
        el_nums = len(uniqe_name_frames)
        el_names_all = [[[] for i in range(el_nums)],
                        [[] for i in range(el_nums)],
                        [[] for i in range(el_nums)]]
        el_names_all[0] = uniqe_name_frames
        for i in range(el_nums):
            res = self.etabs.FrameObj.GetLabelFromName(el_names_all[0][i])
            el_names_all[1][i] = res[0]
            el_names_all[2][i] = res[1]
        u_name_cols = []
        u_name_beams = []
        for i in range(el_nums):
            lb = el_names_all[1][i]
            if lb[0] == 'C':
                u_name_cols.append(el_names_all[0][i])
            elif lb[0] == 'B':
                u_name_beams.append(el_names_all[0][i])
        return u_name_cols,u_name_beams

    def get_columns_unique_names(self, general_frame_data):
        columns = []
        labels = self.get_labels(general_frame_data)
        length = self.get_frames_number(general_frame_data)
        uniq_name = self.get_unique_names(general_frame_data)
        for i in range(length):
            if labels[i][0] == "C":
                columns.append(uniq_name[i])
        return columns

    def get_points(self, general_frame_data):
        frame_uniq_names = self.get_unique_names(general_frame_data)
        all_points = []
        for frame in frame_uniq_names:
            all_points.append(self.etabs.FrameObj.GetPoints(frame))
        return all_points

    def get_columns_points(self, general_data):
        columns = self.get_columns_unique_names(general_frame_data=general_data)
        points, names = [], []
        for u in columns:
            points.append(self.etabs.FrameObj.GetPoints(u))
            names.append(u)
        return points, names

    def get_beam_points(self, general_data):
        beams = self.get_beams_unique_names(general_frame_data=general_data)
        points, names = [], []
        for u in beams:
            points.append(self.etabs.FrameObj.GetPoints(u))
            names.append(u)
        return points, names

    def tip_columns(self, id_under, n_tip):
        result =[]
        for id in id_under:
            leng = len(id)
            it =0
            while it<leng:
                up = it+n_tip
                if it+n_tip>leng:
                    up = leng
                result.append(id[it:up])
                it +=2
        return result

    def get_length(self, points):

        re = []

        for x in points:
            x1, y1, z1 = self.etabs.PointObj.GetCoordCartesian(x[0])[0:3]
            x2, y2, z2 = self.etabs.PointObj.GetCoordCartesian(x[1])[0:3]
            re.append(((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5)
        return re

    @staticmethod
    def get_labels(general_frame_data):
        return general_frame_data['MyLabel']


class Concerete(FrameProb):

    def get_lower(self, type_construction=1, type_plasticity=1):
        story_number = self.get_num_story()['NumberStories']
        result = find_lower(number_of_story=story_number, type=type_construction, platicity_type=type_plasticity)
        logger.info('columns_minimum_width set to {}'.format(result['columns_minimum_width']))
        logger.info('columns_minimum_height set to {}'.format(result['columns_minimum_height']))
        logger.info('beams_minimum_width set to {}'.format(result['beams_minimum_width']))
        logger.info('beams_minimum_height set to {}'.format(result['beams_minimum_height']))
        return result

    def get_type(self, general_frame_data):
        column = 'Column'
        beam = "Beam"
        other = 'other'
        frame_types = []
        labels = self.get_labels(general_frame_data)
        for label in labels:
            if label[0] == "C":
                frame_types.append(column)

            elif label[0] == 'B' or labels[0] == "F":
                frame_types.append(beam)
            else:
                frame_types.append(other)
        return frame_types

    def get_section_dim(self, sections):
        # sections = self.get_section_names()
        widths = []
        heights = []
        mate = []
        for se in sections:

            dimentios = self.etabs.PropFrame.GetRectangle(se)
            widths.append(math.ceil(dimentios[2]))
            heights.append(math.ceil(dimentios[3]))
            mate.append(dimentios[1])
        heights_width = {
            "widths": widths,
            "heights": heights,
            "material": mate

        }
        return heights_width

    def get_combo(self):
         comb = self.etabs.Combination.GetNameList()
         return comb[1]

    def create_envelop(self):
        self.etabs.RespCombo.Add("envelop", 1)

    def add_case_envelope(self):
        combo = self.get_combo()
        for u in combo:
            self.etabs.RespCombo.SetCaseList("envelop", 1, u, 1)
        return combo

    def get_normal_frame_data_index_id(self, general_frame_data):
        unique_names = self.get_unique_names(general_frame_data=general_frame_data)
        labels = self.get_labels(general_frame_data)
        points = self.get_points(general_frame_data)
        lengths = self.get_length(points)
        frame_types = self.get_type(general_frame_data)
        number_of_items = self.get_frames_number(general_frame_data)
        result = {}
        for i in range(number_of_items):
            point = self.etabs.FrameObj.GetPoints(unique_names[i])
            x1, y1, z1 = self.etabs.PointObj.GetCoordCartesian(point[0])[0:3]
            x2, y2, z2 = self.etabs.PointObj.GetCoordCartesian(point[1])[0:3]
            result[unique_names[i]] = {
                    "id":unique_names[i],
                    'label': labels[i],
                    'frame_type': frame_types[i],
                    'length': lengths[i],
                    'x1': x1,
                    'y1': y1,
                    'z1': z1,
                    'x2': x2,
                    'y2': y2,
                    'z2': z2
                }
        return result

    def find_width_height_beam(self, u_name_beam):

        [p1, p2, ret] = self.etabs.FrameObj.GetPoints(u_name_beam, ' ', ' ')
        u_name_point1 = p1
        [x1, y1, z1, ret] = self.etabs.PointObj.GetCoordCartesian(u_name_point1, 0, 0, 0, 'Global')
        u_name_point2 = p2
        [x2, y2, z2, ret] = self.etabs.PointObj.GetCoordCartesian(u_name_point2, 0, 0, 0, 'Global')
        p1 = np.array([x1, y1, z1])
        p2 = np.array([x2, y2, z2])
        v = p2 - p1
        norm2 = np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        ev = v / norm2
        res1 = self.etabs.FrameObj.GetSection(u_name_beam)
        res = self.etabs.PropFrame.GetRectangle(res1[0])
        section_name = res1[0]
        if ev[0] >= -np.sqrt(2) / 2 and ev[0] <= np.sqrt(2) / 2:
            height = res[2]
            width = res[3]
        else:
            height = res[2]
            width = res[3]
        return width, height, section_name

    def find_width_height_column(self,u_name_column):
        res1 = self.etabs.FrameObj.GetSection(u_name_column)
        res = self.etabs.PropFrame.GetRectangle(res1[0])
        section_name = res1[0]
        height = res[2]
        width = res[3]
        return width, height, section_name

    def get_full_frame_data_index_id(self, general_frame_data, result):

        final_result = {}
        for r in result:
            if result[r]['frame_type']=='Column':
                width, height ,section = self.find_width_height_column(r)
            else:
                width, height, section = self.find_width_height_beam(r)
            final_result[r] = {**result[r],
                    'section': section,
                    'width': width,
                    'height': height,
                }
        return final_result

    def set_c_to_load_case(self, c, load_pattern_x, load_pattern_y):
        for load in load_pattern_x:
            a = self.etabs.LoadCases.StaticLinear.SetLoads(load, 1, ['load'], [load], [c[0]])
            if a[3] == 1:
                raise Exception("Coef Factor in x axis wasn't set successfully")
        for load in load_pattern_y:
            b = self.etabs.LoadCases.StaticLinear.SetLoads(load, 1, ['load'], [load], [c[1]])
            if b[3] == 1:
                raise Exception("Coef Factor in y axis wasn't set successfully")
        return a, b

    @staticmethod
    def extract_story(data_output):
        result = {}
        for data in data_output:
            if data['story'] in result:
                if data['frame_type'] == 'Column':
                    # newlist = sorted(data, key=lambda d: d['y2'])
                    result[data['story']].append(data)

            else:
                result[data['story']]=[]
                result[data['story']].append(data)
        for x in result:
            result[x] = sorted(result[x], key=lambda d: d['label'])

        return result

    @staticmethod
    def group_by_label(data, labels):

        result = {key: [] for key in labels}
        for re in result:
            for daton in data:
                if daton['label'] == re and daton['type'] == 'Column':
                    result[re].append(daton)
        return result

    def get_rebar(self, general_data):
        rebar_beam = []
        rebar_column = []
        data = self.get_full_frame_data(general_frame_data=general_data)
        for x in range(len(data)):
            if data[x]["frame_type"] == "Beam":
                rebar_beam.append(self.etabs.PropFrame.GetRebarBeam(data[x]["section"]))
            if data[x]["frame_type"] == "Column":
                rebar_column.append(self.etabs.PropFrame.GetRebarBeam(data[x]["section"]))
        return rebar_beam, rebar_column

    def set_section(self, frame_name, section_name):

        return self.etabs.FrameObj.SetSection(frame_name, section_name)



    @staticmethod
    def get_underneath_column(full_normal_data):
        result = {}
        for k in full_normal_data.keys():
            if full_normal_data[k]['frame_type']=='Column':
                x = full_normal_data[k]['x1']
                y = full_normal_data[k]['y1']
                result_key = str(x) +'-' +str(y)
                try:
                    result[result_key].append(k)
                except KeyError:
                    result[result_key] = [k]

        return list(result.values())

    def get_z(self,id ):
        point = self.etabs.FrameObj.GetPoints(id)
        z1 = self.etabs.PointObj.GetCoordCartesian(point[0])[2]
        return z1

    def sort_by_z(self,columns_under):
        for list_c in columns_under:
            list_c.sort(key=self.get_z)
        return columns_under

    @staticmethod
    def calculate_c(a, i, ru, t, t_zero, s_zero, t_s, s):
        if a == 0.35 or a == 0.3:
            if 0 <= t <= t_zero:
                b = s_zero + (s-s_zero+1)*(t/t_zero)
            elif t_zero < t <= t_s:
                b = s+1
            elif t_zero < t <= 4:
                b_1 = (s+1)*(t_s/t)
                n_1 =(0.7*(t-t_s/(4-t_s))+1)
                n_1 = ((0.7/(4-t_s))*(t-t_s))+1
                b=b_1*n_1
            else:
                b = 1.7 * (s+1)*(t_s/t)
        else:
            if 0 <= t <= t_zero:
                b = s_zero + (s-s_zero+1)*(t/t_zero)
            elif t_zero < t <= t_s:
                b = s+1
            elif t_zero < t <= 4:
                b = (s+1)*(t_s/t)*(0.4*(t-t_s/(4-t_s))+1)
            else:
                b = 1.4 * (s+1)*(t_s/t)
        c = a*b*i/ru
        return max(0.12*a*i, c)

    @staticmethod
    def calculate_period(height, system):
        if system == 1:
            period = 0.05*(height ** 0.9)
        else:
            period = 0.05*(height ** 0.75)
        return 1.25 * period

    def set_modifier_drift(self, unique_names, labels):
        for id in range(len(unique_names)):
            if labels[id][0] =="B":
                a =self.etabs.FrameObj.SetModifiers(unique_names[id], [1, 1, 1, 1, 1, 0.5, 0.8, 0.8])
            else:
                 b = self.etabs.FrameObj.SetModifiers(unique_names[id], [1, 1, 1, 1, 1, 1, 1, 1])

    def set_normal_modifier(self, unique_names, labels):
        for id in range(len(unique_names)):
            if labels[id][0] =="B":
                a = self.etabs.FrameObj.SetModifiers(unique_names[id], [1, 1, 1, 0.15, 0.35, 0.35, 0.8, 0.8])
            else:
                 b = self.etabs.FrameObj.SetModifiers(unique_names[id], [1, 1, 1, 1, 0.7, 0.7, 1, 1])

    def cantilever_beam(self, general_data):
        columns_full = self.get_columns_points(general_data)
        columns = columns_full[0]
        points = []
        for point in columns:
            points.append(self.etabs.PointObj.GetConnectivity(point[0]))
            points.append(self.etabs.PointObj.GetConnectivity(point[1]))
        result = []
        final = []
        for i in points:
            for x in i:
                result.append(x)
        for index, tuple in enumerate(result):
            final.append(result[index])
            candids = final[2: -1: 5]
        return candids

    def get_id_from_story(self, n_story):
        result = {}
        for i in range(len(n_story)):
            group_name = "beam-story{}".format(i+1)
            id_s = self.etabs.Group.GetAssignments("beam-story{}".format(i+1))
            result[group_name] = id_s[2]
        return result



    def get_full_frame_data(self, general_frame_data):
        unique_names = self.get_unique_names(general_frame_data)
        labels = self.get_labels(general_frame_data)
        points = self.get_points(general_frame_data)
        lengths = self.get_length(points)

        # sections = self.get_section_names(general_frame_data)
        #
        sections = self.get_section_names(general_frame_data)
        #
        heights = self.get_section_dim(sections)['heights']
        width = self.get_section_dim(sections)['widths']
        materials = self.get_section_dim(sections)['material']
        frame_types = self.get_type(general_frame_data)
        number_of_items = self.get_frames_number(general_frame_data)
        result = []
        for i in range(number_of_items):
            point = self.etabs.FrameObj.GetPoints(unique_names[i])
            x1, y1, z1 = self.etabs.PointObj.GetCoordCartesian(point[0])[0:3]
            x2, y2, z2 = self.etabs.PointObj.GetCoordCartesian(point[1])[0:3]
            result.append(
                {
                    'id': unique_names[i],
                    'label': labels[i],
                    'material': materials[i],
                    'frame_type': frame_types[i],
                    'length': lengths[i],
                    'section': sections[i],
                    'width': width[i],
                    'height': heights[i],
                    'x1': x1,
                    'y1': y1,
                    'z1': z1,
                    'x2': x2,
                    'y2': y2,
                    'z2': z2
                }
            )
        return result




