import io
import math
import operator
import random
from itertools import groupby

from cost import Cost
from runetabs import RunConcrete
import pandas as pd
from constants import *


class CheckModel(RunConcrete):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def deselect_all_combo(self):
        self.etabs.AnalysisResultsSetup.DeselectAllCasesAndCombosForOutput()

    def set_earth_force(self):
        earth_quake = self.get_earthquake_force()
        for ea in earth_quake:
            self.etabs.AnalysisResultsSetup.SetCaseSelectedForOutput(ea)
        return earth_quake

    def get_story_drift_tables(self, unique_name, labels, flag_period=True):
        if flag_period:
            self.etabs.SapModel.SetModelIsLocked(False)
            self.set_modifier_drift(unique_names=unique_name, labels=labels)
            self.run_model()
            t_x, t_y, check = self.get_modal_period()
            if check == 0:
                return [1],[1]
            period_exp = self.calculate_period(height=HEIGHT, system=SYSTEM)
            period_x = min(period_exp, t_x)
            period_y = min(period_exp, t_y)
            self.etabs.SapModel.SetModelIsLocked(False)
            c_x = self.calculate_c(a=A, i=I,ru=RU_X,t=period_x, s_zero=S_ZERO, s=S, t_zero=T_ZERO, t_s=T_S)
            c_y = self.calculate_c(a=A, i=I, ru=RU_X, t=period_y, s_zero=S_ZERO, s=S, t_zero=T_ZERO, t_s=T_S)
            self.set_c_to_load_case(c=[c_x, c_y], load_pattern_x=['EX',"EXN","EXP"], load_pattern_y=["EY","EYN","EYP"])
            # self.delete_all_load_case()
            # self.etabs.AnalysisResultsSetup.DeselectAllCasesAndCombosForOutput()
            # self.etabs.AnalysisResultsSetup.SetCaseSelectedForOutput("EX")
            self.run_model()
        self.etabs.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EX")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EXN")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EXP")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EY")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EYN")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EYP")

        drift_table = self.etabs.DatabaseTables.GetTableForDisplayCSVString('Diaphragm Center Of Mass Displacements', [], '')
        drift = pd.read_csv(io.StringIO(drift_table[2]), sep=",")
        df = drift[['Story', 'Output Case', 'UX', 'UY']]
        df = df[df['Output Case'].isin(['EX',"EXN","EXP","EY","EYN","EYP"])]
        x_u = df.sort_values(['Output Case', "Story"], ascending=False)
        x_g = x_u.groupby(['Output Case'])
        X = {}
        for group_name, df_group in x_g:
            X[group_name] = []
            for row_index, row in df_group.iterrows():
                X[group_name].append((df_group['UX'][row_index], df_group['UY'][row_index]))
        elevations = self.get_num_story()['StoryElevations']
        heights = []
        for i in range(len(elevations) - 1):
            heights.append(elevations[i + 1] - elevations[i])
        heights = heights[::-1]
        result_x = []
        result_y = []
        for k in X:
            for u in range(len(X[k]) - 1):
                result_x.append((X[k][u][0] - X[k][u + 1][0]) / heights[u + 1])
                result_y.append((X[k][u][1] - X[k][u + 1][1]) / heights[u + 1])
        self.etabs.SapModel.SetModelIsLocked(False)
        cd_x = self.get_cd_drift_x()
        cd_y = self.get_cd_drift_y()
        limit_x, limit_y = 0.025/cd_x, 0.025/cd_y
        not_okay_x, not_okay_y = [i/limit_x for i in result_x if i > limit_x], [i/limit_y for i in result_y if i > limit_y]
        if flag_period:
            self.set_normal_modifier(unique_names=unique_name, labels=labels)
        return not_okay_x+not_okay_y

    def modify_drift(self, unique_name, labels,num_story):
        check = self.get_story_drift_tables(unique_name=unique_name, labels=labels)

        if len(check)> 0:
            self.etabs.SapModel.SetModelIsLocked(False)
        res1 = self.etabs.Group.GetAssignments('beam-story1')[2]
        res2 = self.etabs.Group.GetAssignments('beam-story2')[2]
        res3 = self.etabs.Group.GetAssignments('beam-story3')[2]
        res4 = self.etabs.Group.GetAssignments('beam-story4')[2]
        beam_drift = [0]*num_story
        for k in range(len(beam_drift)):
            beam_drift[k] = random.randint(0,len(BEAM_DRIFT))
        final_beam_drift = sorted(beam_drift)
        for p in res1:
            self.etabs.FrameObj.SetSection(str(p), final_beam_drift[0])
        for x in res2:
            self.etabs.FrameObj.SetSection(str(x), final_beam_drift[1])
        for v in res3:
            self.etabs.FrameObj.SetSection(str(v), final_beam_drift[2])
        for i in res4:
            self.etabs.FrameObj.SetSection(str(i), final_beam_drift[3])
        check = self.get_story_drift_tables(unique_name=unique_name , labels=labels)
        return check

    def Column_dim_checker(self, Frames_group_name, delta):
        Story = self.etabs.Story
        Group = self.etabs.Group
        FrameObj = self.etabs.FrameObj
        PropFrame = self.etabs.PropFrame
        PointObj = self.etabs.PointObj
        g_name_frames = Frames_group_name
        res = Story.GetStories()
        num_stories = res[0]
        names_st = res[1]
        res = Group.GetAssignments(g_name_frames)
        uniqe_name_frames = res[2]
        el_nums = len(uniqe_name_frames)
        el_names_all = [[[] for i in range(el_nums)],
                        [[] for i in range(el_nums)],
                        [[] for i in range(el_nums)],
                        [[] for i in range(el_nums)],
                        [[] for i in range(el_nums)]]
        el_names_all[0] = uniqe_name_frames
        i = 0
        for i in range(el_nums):
            res = FrameObj.GetLabelFromName(el_names_all[0][i])
            el_names_all[1][i] = res[0]
            el_names_all[2][i] = res[1]
        Story_names = names_st[1:]
        x = []
        y = []
        for i in range(el_nums):
            lb = el_names_all[1][i]
            if lb[0] == 'C':
                u_name = el_names_all[0][i]  # col's unique name
                [p1, p2, ret] = FrameObj.GetPoints(u_name, ' ', ' ')
                u_name_point1 = p1
                [x1, y1, z1, ret] = PointObj.GetCoordCartesian(u_name_point1, 0, 0, 0, 'Global')
                if len(x) > 0:
                    for j in range(len(x)):
                        if x1 == x[j] and y1 == y[j] and j <= len(x) - 1:
                            r = j
                            nax = r
                            break
                        elif j == len(x) - 1:
                            x.append(x1)
                            y.append(y1)
                            nax = len(x) - 1
                else:
                    x.append(x1)
                    y.append(y1)
                    nax = 0
        max_ax = nax + 2

        col_ax = [[[] for j in range(num_stories)] for i in range(max_ax)]
        col_res = [[[] for j in range(num_stories)] for i in range(max_ax)]
        x = []
        y = []
        for i in range(el_nums):
            lb = el_names_all[1][i]
            if lb[0] == 'C':
                u_name = el_names_all[0][i]
                [p1, p2, ret] = FrameObj.GetPoints(u_name, ' ', ' ')
                u_name_point1 = p1
                [x1, y1, z1, ret] = PointObj.GetCoordCartesian(u_name_point1, 0, 0, 0, 'Global')
                if len(x) > 0:
                    for j in range(len(x)):
                        if x1 == x[j] and y1 == y[j] and j <= len(x) - 1:
                            r = j
                            nax = r
                            break
                        elif j == len(x) - 1:
                            x.append(x1)
                            y.append(y1)
                            nax = len(x) - 1
                else:
                    x.append(x1)
                    y.append(y1)
                    nax = 0
                sti = el_names_all[2][i]
                for j in range(len(Story_names)):
                    if sti == Story_names[j]:
                        n_st = j
                col_ax[nax][n_st] = el_names_all[0][i]
        for i in range(el_nums):
            un_name = el_names_all[0][i]
            res1 = FrameObj.GetSection(un_name)
            res = PropFrame.GetRectangle(res1[0])
            b = res[2]
            h = res[3]
            el_names_all[3][i] = b
            el_names_all[4][i] = h
        for i in range(len(col_ax)):
            col_res[i][0] = 0
            for j in range(1, num_stories):
                if len(col_ax[i][j]) > 0 and len(col_ax[i][j - 1]) > 0:
                    un_name_s = col_ax[i][j - 1]
                    res1 = FrameObj.GetSection(un_name_s)
                    res = PropFrame.GetRectangle(res1[0])
                    hs = res[2]
                    bs = res[3]
                    un_name_f = col_ax[i][j]
                    res1 = FrameObj.GetSection(un_name_f)
                    res = PropFrame.GetRectangle(res1[0])
                    hf = res[2]
                    bf = res[3]
                    if hf < hs:
                        if hs - hf > delta:
                            hf = hs - delta
                    elif hf > hs:
                        hf = hs
                    if bf < bs:
                        if bs - bf > delta:
                            bf = bs - delta
                    elif bf > bs:
                        bf = bs
                    sec_name = 'C{}X{}'.format(int(bf), int(hf))
                    FrameObj.SetSection(un_name_f, sec_name)
                    if (hs - hf) <= delta and (hs - hf) >= 0 and (bs - bf) <= delta and (bs - bf) >= 0:
                        col_res[i][j] = 0
                    else:
                        col_res[i][j] = 1
        return col_res

    def get_unit(self):
        return self.etabs.SapModel.GetPresentUnits()

    def get_cd_drift_x(self):
        cd_driftx = 4.5
        return cd_driftx

    def get_cd_drift_y(self):
        cd_drift_y = 4.5
        return cd_drift_y

    def check_drift(self, result_x, result_y):
        cd_x = self.get_cd_drift_x()
        cd_y = self.get_cd_drift_y()
        limit_x, limit_y = 0.02/cd_x, 0.02/cd_y
        not_okay_x, not_okay_y = [i for i in result_x if i > limit_x], [i for i in result_y if i > limit_y]
        return not_okay_x, not_okay_y

    def get_pm_ratio(self, general_data):
        columns = self.get_columns_unique_names(general_frame_data=general_data)
        result = []
        for column in columns:
            try:
                result.append(max(self.etabs.DesignConcrete.GetSummaryResultsColumn(column)[6]))
            except IndexError:
                print("column {} does not have pm ratio".format(column))
                result.append(0)
        return result

    def get_modal_period(self):
        self.etabs.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self.etabs.Results.Setup.SetCaseSelectedForOutput("MODAL")
        result = self.etabs.Results.ModalParticipationFactors()
        t_x = result[4][result[5].index(max((result[5]), key=abs))]
        t_y = result[4][result[6].index(max((result[6]), key=abs))]
        sum_ux = result[8]
        sum_uy = result[9]
        for i in range(0, len(sum_ux)):
            if (sum_ux[i] >= 0.9) and (sum_uy[i] >= 0.9):
                check = 1
                break
            else:
                check = 0

        return t_x, t_y, check

    def check_connection(self, general_data, result):
        columns_full = self.get_columns_points(general_data)
        columns = columns_full[0]
        names = columns_full[1]
        full_frame_data = self.get_full_frame_data_index_id(general_frame_data=general_data, result=result)
        points = []
        for point in columns:
            points.append(self.etabs.PointObj.GetConnectivity(point[0]))
            points.append(self.etabs.PointObj.GetConnectivity(point[1]))
        result = []
        # print("all points is {}".format(points))
        for point in points:
            i = 0
            for object in range(len(point[1])):
                if point[1][object] == 2 and full_frame_data[point[2][object]]['frame_type']=="Beam":
                    if full_frame_data[point[2][object]]['width'] > full_frame_data[names[math.floor(i)]]['height']:
                        result.append(point)
                if point[1][object] == 2 and full_frame_data[point[2][object]]['frame_type'] == "Column":

                    column_1 = full_frame_data[names[math.floor(i)]]
                    column_2 = full_frame_data[point[2][object]]
                    if column_1['z2'] > column_2['z2']:
                        column_1, column_2 = column_2, column_1
                    if column_1['height'] > column_2['height'] or column_1['width'] > column_2['width']:
                        result.append(point)

            i += 0.5
        return result

    def check_underneath_column(self, id_underneath):
        sections = []
        for ids in id_underneath:
            vr = []
            for id in ids:
                vr.append(self.etabs.FrameObj.GetSection(id)[0])
            sections.append(vr)
        for se in sections:
            se.sort(reverse=True)
            for s in range(len(se)-1):
                if int(se[s+1][-2:]) > int(se[s][-2:]):
                    se[s+1] = se[s+1][:-2]+se[s][-2:]
        for i in range(len(id_underneath)):
            for j in range(len(id_underneath[i])):
                self.etabs.FrameObj.SetSection(id_underneath[i][j], sections[i][j])
        return sections

    def get_story_forces(self):
        self.run_model()
        self.etabs.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EX-All")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EY-All")

        drift_table = self.etabs.DatabaseTables.GetTableForDisplayArray('Story Forces', [], '')
        print("xxxxx",drift_table)

    def get_max_avg_drift(self):
        self.run_model()
        self.etabs.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EX-All")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EY-All")

        drift_table = self.etabs.DatabaseTables.GetTableForDisplayArray('Diaphragm Max Over Avg Drifts', [], '')
        print("xxxxx",drift_table)

    def irreg_mass(self):
        self.run_model()
        self.etabs.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EX")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EY")

        mass_with_pent = self.etabs.DatabaseTables.GetTableForDisplayArray('Mass Summary by Story', [], '', 0, [], 0, [])[4][1::4][:-1]
        if (float(mass_with_pent[0]) / float(mass_with_pent[1])) > 0.25:
            mass = mass_with_pent
        else:
            mass = mass_with_pent[1:]
        mass = [float(ele) for ele in mass]
        i = 1
        for element in mass:
            if element / (mass[i]) > 1.5:
                return False
            elif i > 1:
                if element / (mass[i - 2]) > 1.5:
                    return False
            if i < (len(mass) - 1):
                i = i + 1
        return True

    def check_os_error(self, general_data, location):
        name_id = self.get_beams_unique_names(general_frame_data=general_data)
        fc = 25
        fy = 400
        result1 = []
        result2 = []
        for ID in name_id:
            result1.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[-3])
        tidy = dict(zip(name_id, result1))
        for j in tidy.keys():
            if 'Shear stress due to shear force and torsion together exceeds maximum allowed.' in tidy[j] \
                    or 'Reinforcing required exceeds maximum allowed' in tidy[j]:
                result2.append(j)
        top_area, bot_area, tl_area, total, final, total_max = [], [], [], [], [], []
        for p in result2:
            top_area.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(p)[4])
            bot_area.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(p)[6])
            tl_area.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(p)[10])
        for ID in range(len(result2)):
            for j in range(len(top_area)):
                total.append(top_area[ID][j] + bot_area[ID][j] + tl_area[ID][j])
            total_max.append(max(total))
        if 17 <= fc <= 28:
            beta1 = 0.85
        else:
            beta1 = max(0.85 - (0.05 / 7) * (fc - 28), 0.65)
        if fc > 55:
            a0 = max(0.85 - (0.022 / 7) * (fc - 55), 0.7)
        else:
            a0 = 0.85
        ro_b = (a0 * fc * beta1 * 600) / (0.9 * fy * (600 + fy))
        for i in total_max:
            final.append(i / ro_b)
        result3, eff_height, width, round_width = [], [], [], []
        for t in result2:
            result3.append(self.etabs.FrameObj.GetSection(t)[0])
        for u in result3:
            eff_height.append(int(u[4:6]))
        for k in range(len(eff_height)):
            width.append(final[k] / eff_height[k])
        for d in width:
            if d % 5 == 0:
                width = d
            else:
                z = (int(d) % 5)
                width = int((d) + (5-z))
            round_width.append(width)
        for x in range(len(eff_height)):
            if (eff_height[x]/round_width[x]) >= 0.35:
                eff_height = eff_height
                round_width = round_width
            else:
                change_value = Cost.total_value(self, general_data, location)*10000
        return change_value

    def torsional_irregularity(self):
        # Required Load Cases are : EX & EXP & EXN & EY & EYP & EYN
        # self.etabs.DatabaseTables.SetLoadCasesSelectedForDisplay(['EX'])
        # getting all data for torsional_irregularity control
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EX")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EY")
        torsion = self.etabs.DatabaseTables.GetTableForDisplayArray('Story Max Over Avg Drifts', [], '', 0, [], 0, [])
        # we just need titr and data to control torsional_irregularity ,so we get their indexes
        titr = torsion[2]
        data = torsion[4]
        lines = [list(titr)]
        j = 0
        # list of titr has 7 indexes so by using these indexes we separate all specific data and change them in one list
        for i in range(len(titr), len(data) + len(titr), len(titr)):
            lines.append(list(data[j:i]))
            j += len(titr)

        # in controlling torsional_irregularity we don't need to "CaseType" so we remove titr and total data of it.
        casetype_index = lines[0].index('CaseType')
        for i in range(len(lines)):
            lines[i].remove(lines[i][casetype_index])
        steptype_index = lines[0].index('StepType')
        for i in range(len(lines)):
            lines[i].remove(lines[i][steptype_index])

        vs_pos = []
        vs = []
        # we know for torsional_irregularity control ratio must be lower than 1.2 .so we added a titr as situation to
        # tell us is it ok or not.
        lines[0].append('Situation')
        all_not_ok_ratios = []
        for i in range(1, len(lines)):
            vs_pos.append(abs(float(lines[i][4])))
            vs_pos.append(abs(float(lines[i][5])))
            vs.append(float(lines[i][4]))
            vs.append(float(lines[i][5]))
            ratio = float(lines[i][lines[0].index('Ratio')])
            if ratio < 1.2:
                lines[i].append('OK')
            else:
                lines[i].append('Not OK')
                all_not_ok_ratios.append(ratio - 1.2)

        # type of data are string ,so we must change them to float
        for i in range(1, len(lines)):
            lines[i][-2] = float(lines[i][-2])
            lines[i][-3] = float(lines[i][-3])
            lines[i][-4] = float(lines[i][-4])

        df = pd.DataFrame(lines[1:], columns=lines[0])
        df = df[df['OutputCase'].isin(['EX', "EY"])]
        df = df[df.Situation =="Not OK"]
        return len(df)

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

    def overturning(self):
        grids_name = self.etabs.DatabaseTablesGetTableForDisplayArray('Grid Definitions - Grid Lines', [], '', 0, [], 0, [])[4][2::6]
        grids_spacing = self.etabs.DatabaseTablesGetTableForDisplayArray('Grid Definitions - Grid Lines', [], '', 0, [], 0, [])[4][3::6]
        index_y = grids_name.index(min(grids_name))
        index_x = grids_name.index(max(grids_name))
        dim_y = grids_spacing[index_y]
        dim_x = grids_spacing[index_x]
        self.etabs.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EX")
        self.etabs.Results.Setup.SetCaseSelectedForOutput("EY")
        cummassx = self.etabs.GetTableForDisplayArray('Centers Of Mass And Rigidity', [], '', 0, [], 0, [])[4][6::12]
        cummassy = self.etabs.GetTableForDisplayArray('Centers Of Mass And Rigidity', [], '', 0, [], 0, [])[4][7::12]
        cummass_x = max([float(ele) for ele in cummassx]) * 1000 * 9.81
        cummass_y = max([float(ele) for ele in cummassy]) * 1000 * 9.81
        x_ccm = self.etabs.GetTableForDisplayArray('Centers Of Mass And Rigidity', [], '', 0, [], 0, [])[4][8::12][-1]
        y_ccm = self.etabs.GetTableForDisplayArray('Centers Of Mass And Rigidity', [], '', 0, [], 0, [])[4][9::12][-1]
        d_x = min(float(x_ccm), float(dim_x) - float(x_ccm))
        d_y = min(float(y_ccm), float(dim_y) - float(y_ccm))
        mr_x = float(cummass_x) * d_y
        mr_y = float(cummass_y) * d_x

        self.etabs.SetLoadCasesSelectedForDisplay(['EX'])
        v_x = self.etabs.DatabaseTables.GetTableForDisplayArray('Story Forces', [], '', 0, [], 0, [])[4][15::20]
        m_y = self.etabs.DatabaseTables.GetTableForDisplayArray('Story Forces', [], '', 0, [], 0, [])[4][19::20]
        abs_v_x = [abs(float(ele)) for ele in v_x]
        abs_m_y = [abs(float(ele)) for ele in m_y]
        self.etabs.DatabaseTables.SetLoadCasesSelectedForDisplay(['EY'])
        v_y = self.etabs.DatabaseTables.GetTableForDisplayArray('Story Forces', [], '', 0, [], 0, [])[4][16::20]
        m_x = self.etabs.DatabaseTables.GetTableForDisplayArray('Story Forces', [], '', 0, [], 0, [])[4][18::20]
        abs_v_y = [abs(float(ele)) for ele in v_y]
        abs_m_x = [abs(float(ele)) for ele in m_x]
        mo_x = abs(float(m_x[abs_m_x.index(max(abs_m_x))])) + abs(float(v_y[abs_v_y.index(max(abs_v_y))]) * df)
        mo_y = abs(float(m_y[abs_m_y.index(max(abs_m_y))])) + abs(float(v_x[abs_v_x.index(max(abs_v_x))]) * df)

        sf_x = abs(mr_x / mo_x)
        sf_y = abs(mr_y / mo_y)
        if sf_x > 1 and sf_y > 1:
            return True
        else:
            return False

