import math

from collect_data import CollectData


class Cost(CollectData):
    def longitudinal(self, beams):

        beam = []
        for ID in range(beams):
            beam.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID))
        return beam

    def get_location(self, beams):
        location = []

        for ID in beams:
            location.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[2])
        return location

    def solution(self, beams):
        loct = self.get_location(beams)
        fin_location = []
        for loc in loct:
            result = []
            loc = [0] + list(loc)
            for idx in range(1, len(loc)):
                result.append(loc[idx] - loc[idx - 1])
            fin_location.append(result)
        return fin_location

    def get_top_area(self, beams):
        beam_top_area = []
        for ID in beams:
            beam_top_area.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[4])
        return beam_top_area

    def get_bot_area(self, beams):
        beam_bot_area = []
        for ID in beams:
            beam_bot_area.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[6])
        return beam_bot_area

    def get_tl_area(self, beams):
        beam_tl_area = []
        for ID in beams:
            beam_tl_area.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[10])
        return beam_tl_area

    def total_area(self, beams):
        total_area = []
        top = self.get_top_area(beams=beams)
        bot = self.get_bot_area(beams=beams)
        tl = self.get_tl_area(beams=beams)
        for ID in range(len(beams)):
            for column in range(len(top[ID])):
                total_area.append(top[ID][column] + bot[ID][column] + tl[ID][column])
        return total_area

    def volume_longitudinal_beam(self, beams):
        volume_beam = []
        length = self.solution(beams=beams)
        area = self.total_area(beams=beams)
        index_area = 0
        for ID in range(len(beams)):
            summation = 0
            for j in range(len(length[ID])):
                summation += length[ID][j]*area[index_area]
                index_area += 1
            volume_beam.append(summation)
        return sum(volume_beam)

    def major_area(self, beams):

        major_area_list = []
        for ID in beams:
            major_area_list.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[8])
        return major_area_list

    def tt_area(self, beams):
        tt_area_list = []
        for ID in beams:
            tt_area_list.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[12])
        return tt_area_list

    def trans_beam_area(self, beams):
        trans_area = []
        major = self.major_area(beams=beams)
        tt = self.tt_area(beams=beams)

        for ID in range(len(beams)):
            for column in range(len(major[ID])):
                trans_area.append(major[ID][column] + 2*tt[ID][column])
        return trans_area

    def stirrup_length(self, full_data):
        perimeter = []
        for ID in full_data.keys():
            if full_data[ID]['frame_type'] == "Beam":
                perimeter.append((2*((full_data[ID]['width']-8) + (full_data[ID]['height']-8)))*full_data[ID]['length'])
        return perimeter

    def volume_trans_beam(self, beams, full_data):
        volume_beam = []
        stirrup = self.stirrup_length(full_data=full_data)
        print("stirup",stirrup)
        area = self.trans_beam_area(beams=beams)
        print("area is",area)
        for ID in range(len(stirrup)):
            volume_beam.append(area[ID] * stirrup[ID])
        return sum(volume_beam)

    def location_column(self, columns):
        location_list = []
        for ID in columns:
            location_list.append(self.etabs.DesignConcrete.GetSummaryResultsColumn(ID)[3][-1])
        return location_list

    def area_column(self, columns):
        long_column_list = []
        for ID in columns:
            long_column_list.append(self.etabs.DesignConcrete.GetSummaryResultsColumn(ID)[5][2])
        return long_column_list

    def volume_longitudinal_column(self, columns):
        volume_column = []
        location = self.location_column(columns=columns)
        area = self.area_column(columns=columns)
        for ID in range(len(location)):
            volume_column.append(location[ID] * area[ID])
        return sum(volume_column)

    def major_column(self, columns):
        major_column_list = []
        for ID in columns:
            major_column_list.append(self.etabs.DesignConcrete.GetSummaryResultsColumn(ID)[8])
        return major_column_list

    def minor_column(self, columns):
        minor_column_list = []
        for ID in columns:
            minor_column_list.append(self.etabs.DesignConcrete.GetSummaryResultsColumn(ID)[10])
        return minor_column_list

    def max_minor_major(self, columns):
        maximum = []
        minor = self.minor_column(columns=columns)
        major = self.major_column(columns=columns)
        for ID in range(len(minor)):
            maximum.append(max(minor[ID], major[ID])[0])
        return maximum

    def stirrup_length_column(self, full_data):
        perimeter = []
        for ID in full_data.keys():
            if full_data[ID]['frame_type'] == "Column":
                perimeter.append((2*((full_data[ID]['width']-8) + (full_data[ID]['height']-8)))*full_data[ID]['length'])
        return perimeter

    def volume_trans_column(self, columns, full_data):
        volume_column = []
        stirrup = self.stirrup_length_column(full_data=full_data)
        area = self.max_minor_major(columns=columns)
        for ID in range(len(stirrup)):
            volume_column.append(area[ID] * stirrup[ID])
        return sum(volume_column)

    def total_volume_rebar(self, columns, full_data, beams):
        beam_long = self.volume_longitudinal_beam(beams=beams)
        beam_trans = self.volume_trans_beam(beams=beams, full_data=full_data)
        column_long = self.volume_longitudinal_column(columns=columns)
        column_trans = self.volume_trans_column(columns=columns, full_data=full_data)
        print("beam_long",beam_long)
        print("beam_transe", beam_trans)
        print("column_long",column_long)
        print("column_trans",column_trans)

        total_volume = beam_long + beam_trans + column_trans + column_long
        print("total_volume_rbar",total_volume)
        return total_volume*(10**(-6))

    def total_mass(self, columns, beams, full_data):
        constant_value = 8000
        total = self.total_volume_rebar(columns=columns, beams=beams, full_data=full_data)
        print("total_mass",total)
        total_mass = constant_value*total
        return total_mass

    def total_value_rebar(self, columns, beams, full_data):
        print(full_data)
        constants_value = 24500
        total_value = self.total_mass(columns, beams, full_data)
        print("total value is",total_value)
        final_value = constants_value*total_value
        return final_value

    def calculate_os_columns(self, columns):
        result1 = []
        result2 = []
        for ID in columns:
            result1.append(self.etabs.DesignConcrete.GetSummaryResultsColumn(ID)[-2])
        for num in columns:
            summary_result_column = self.etabs.DesignConcrete.GetSummaryResultsColumn(num)
            result2.append(summary_result_column[-3])
        return result1, result2

    def os_error_column_shear(self, columns):
        fc = 30
        fy = 400
        shear_os_uniq_name, shear_os_section, error, force = [], [], [], []
        critical_sec_v2_max, critical_sec_v2_min = [], []
        critical_sec_v3_max, critical_sec_v3_min = [], []
        height = []
        width = []
        eff_height = []
        error = self.calculate_os_columns(columns)[1]
        tidy = dict(zip(columns, error))
        for j in tidy.keys():
            if 'Shear stress exceeds maximum allowed' in tidy[j]:
                shear_os_uniq_name.append(j)
                shear_os_section.append(self.etabs.FrameObj.GetSection(j)[0])
                design_force = self.etabs.DesignForces.ColumnDesignForces(j)
                p_force = design_force[4]
                v2_force = design_force[5]
                v3_force = design_force[6]
                max_p = max(p_force)
                min_p = min(p_force)
                max_v2 = max(v2_force)
                min_v2 = min(v2_force)
                max_v3 = max(v3_force)
                min_v3 = min(v3_force)
                indx_max_v2 = v2_force.index(max_v2)
                indx_min_v2 = v2_force.index(min_v2)
                indx_max_v3 = v3_force.index(max_v3)
                indx_min_v3 = v3_force.index(min_v3)
                force.append([max_p, min_p, max_v2, min_v2, max_v3, min_v3])
                critical_sec_v2_max.append([p_force[indx_max_v2], max_v2])
                critical_sec_v2_min.append([p_force[indx_min_v2], min_v2])
                critical_sec_v3_max.append([p_force[indx_max_v3], max_v3])
                critical_sec_v3_min.append([p_force[indx_min_v3], min_v3])
        for u in shear_os_section:
            height.append(int(u[4:6]))
        for u in shear_os_section:
            eff_height.append(int(u[4:6]) - 7)
        for q in shear_os_section:
            width.append(int(q[1:3]))
        v_abs, max_v = [], []
        for i in range(len(shear_os_uniq_name)):
            for j in critical_sec_v2_max, critical_sec_v2_min, critical_sec_v3_max, critical_sec_v3_min:
                v_abs.append(abs(j[i][1]))
        v_abs_per_unque, nu_f = [], []
        for z in range(0, len(v_abs), 4):
            v_abs_per_unque.append(max(v_abs[z: z + 4]))
        for y in v_abs_per_unque:
            for x in critical_sec_v2_max[:] + critical_sec_v2_min[:] + critical_sec_v3_max[:] + critical_sec_v3_min[:]:
                if abs(x[1]) == y:
                    nu_f.append(x[0])
        vc_list = []
        for i in range(len(shear_os_uniq_name)):
            if ((-nu_f[i] * 10) / (6 * width[i] * 10 * height[i] * 10)) <= (0.05 * fc):
                vc = (0.17 * math.sqrt(fc) + ((-nu_f[i] * 10) / (6 * width[i] * 10 * height[i] * 10))) * width[i] * 10 * \
                     eff_height[i] * 10
            else:
                vc = (0.17 * math.sqrt(fc) + (0.05 * fc)) * width[i] * 10 * eff_height[i] * 10
            if vc < 0:
                vc = 0
            elif vc > (0.42 * math.sqrt(fc) * width[i] * 10 * eff_height[i] * 10):
                vc = 0.42 * math.sqrt(fc) * width[i] * 10 * eff_height[i] * 10
            else:
                vc = vc
            vc_list.append(vc)

        vs_minor, vs_major, vs, vs_frl = [], [], [], []
        for i in shear_os_uniq_name:
            vs_minor.append(min(self.etabs.DesignConcrete.GetSummaryResultsColumn(i)[10]))
            vs_major.append(min(self.etabs.DesignConcrete.GetSummaryResultsColumn(i)[8]))
            vs.append(max(min(self.etabs.DesignConcrete.GetSummaryResultsColumn(i)[10]),
                          min(self.etabs.DesignConcrete.GetSummaryResultsColumn(i)[8])))
        for z in range(len(shear_os_section)):
            vs_frl.append(fy * vs[z] * eff_height[z])
        v_capacity = []
        demand_capacity = []
        for k in range(len(vs_frl)):
            v_capacity.append(0.75 * (vc_list[k] + vs_frl[k]))
        for q in range(len(v_capacity)):
            demand_capacity.append(((v_abs_per_unque[q]) * 10) / v_capacity[q])
        return demand_capacity

    def os_error_beam_fix(self, beams):
        area = []
        for ID in beams:
            results_beam = self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)
            eror = results_beam[-3]
            u = self.etabs.FrameObj.GetSection(ID)[0]
            eff_height = float(u[4:6]) - 4.5
            eff_width = float(u[1:3])
            for k in range(len(eror)):
                if eror[k] == "Reinforcing required exceeds maximum allowed":
                    top_area = results_beam[4][k]
                    bot_area = self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[6][k]
                    ro = (bot_area+top_area)*100/(eff_width*eff_height)
                    area.append(ro/2.5)
        return area

    def os_error_column(self, columns):
        result1 = []
        result2 = []
        print(columns)
        for ID in columns:
            result1.append(self.etabs.DesignConcrete.GetSummaryResultsColumn(ID)[-2])
        tidy = dict(zip(columns, result1))
        print(result1)
        for j in tidy.keys():
            if 'Shear stress due to shear force and torsion together exceeds maximum allowed.' in tidy[j] \
                    or 'Reinforcing required exceeds maximum allowed' in tidy[j]:
                result2.append(j)
                return False
        return True

    def os_error_beam(self, beams):
        result1 = []
        result2 = []
        for ID in beams:
            result1.append(self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[-3])
        tidy = dict(zip(beams, result1))

        for j in tidy.keys():
            if 'Shear stress due to shear force and torsion together exceeds maximum allowed.' in tidy[j] \
                    or 'Reinforcing required exceeds maximum allowed' in tidy[j]:
                result2.append(j)
                return False
        return True


class FrameWorkCost(CollectData):

    def __init__(self, full_frame_data,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.full_frame_data = full_frame_data

    def total_frame_cost(self):
        data = self.full_frame_data
        cost = 0
        for key in data.keys():
            cost += 2*(data[key]['height'] + data[key]['width'])*data[key]['length']
        return cost

    def total_value_frame(self):
        constants_value = 230000
        total_value = self.total_frame_cost()*10**(-4)
        final_value = constants_value*total_value
        return final_value