from collect_data import CollectData
from constants import Average_Cover, Slab_Thick, Steel_Unit_Weight, UnitWeightCostRebar,UnitVolumeCostConcrete, UnitAreaCostFormWorkColumns


class FinalCost(CollectData):

    def calculate_beam_cost(self, beam_names, full_data):
        conc_Cost = 0
        steel_Cost = 0
        formWork_Cost = 0
        for beam in beam_names:
            width = full_data[beam]["width"]
            height = full_data[beam]['height']
            area = height*width
            perimeter = 2*(height+width)
            be_result = self.etabs.DesignConcrete.GetSummaryResultsBeam(beam)

            location = be_result[2]
            top_area = be_result[4]
            bot_area = be_result[6]
            vm_major_area = be_result[8]
            tl_area = be_result[10]
            tt_area = be_result[12]
            total_as_longb = []
            total_av_tranb = []
            for i in range(len(top_area)):
                total_as_longb.append(bot_area[i]+top_area[i]+tl_area[i])
            for i in range(len(vm_major_area)):
                total_av_tranb.append(vm_major_area[i]+2*tt_area[i])
            for i in range(len(location)-1):
                delta_location = location[i+1]-location[i]
                long_cost = ((total_as_longb[i]+total_as_longb[i+1])/2)
                silence_cost = ((total_av_tranb[i]+total_av_tranb[i+1])/2)*(perimeter-8*Average_Cover)
                steel_Cost += (long_cost + silence_cost)*delta_location*Steel_Unit_Weight*UnitWeightCostRebar*10**(-6)
                conc_Cost += area*delta_location*10**(-6)*UnitVolumeCostConcrete
                formWork_Cost += (perimeter-2*0)*delta_location*UnitAreaCostFormWorkColumns*10**(-4)
        final_beam_cost = steel_Cost +conc_Cost + formWork_Cost
        return final_beam_cost, steel_Cost, conc_Cost, formWork_Cost

    def calculate_column_cost(self,column_names,full_data):
        conc_Cost = 0
        steel_Cost = 0
        formWork_Cost = 0
        for column in column_names:
            width = full_data[column]["width"]
            height = full_data[column]['height']
            area = height*width
            perimeter = 2*(height+width)
            c_result = self.etabs.DesignConcrete.GetSummaryResultsColumn(column)

            location = c_result[3]
            pmm_area = c_result[5]
            av_major = c_result[8]
            av_minor = c_result[10]
            total_As_longc = pmm_area
            total_av_tranC = [max(av_major[i], av_minor[i])for i in range(len(av_major))]

            for i in range(len(location)-1):
                delta_location = location[i+1]-location[i]
                long_cost = ((total_As_longc[i]+total_As_longc[i+1])/2)
                silence_cost = ((total_av_tranC[i]+total_av_tranC[i+1])/2)*(perimeter-6*Average_Cover)
                steel_Cost += (long_cost + silence_cost)*delta_location*Steel_Unit_Weight*UnitWeightCostRebar*10**(-6)
                conc_Cost += area*delta_location*10**(-6)
                formWork_Cost += perimeter*delta_location*UnitAreaCostFormWorkColumns*10**(-4)
        final_column_cost = steel_Cost + conc_Cost + formWork_Cost
        return final_column_cost, steel_Cost, conc_Cost, formWork_Cost

    def get_total_cost(self,beam_names, column_names, full_data):
        beam_cost = self.calculate_beam_cost(beam_names=beam_names, full_data=full_data)[0]
        column_cost = self.calculate_column_cost(column_names=column_names, full_data=full_data)[0]
        final = beam_cost+column_cost
        return final

    def get_rebar_weight(self, beam_names ,column_names, full_data):
        beam_cost = self.calculate_beam_cost(beam_names=beam_names, full_data=full_data)[1]
        column_cost = self.calculate_column_cost(column_names=column_names, full_data=full_data)[1]
        final_cost = beam_cost + column_cost
        wight = final_cost/UnitWeightCostRebar
        return wight

    def get_rebar_cost(self,beam_names ,column_names, full_data):
        beam_cost = self.calculate_beam_cost(beam_names=beam_names, full_data=full_data)[1]
        column_cost = self.calculate_column_cost(column_names=column_names, full_data=full_data)[1]
        final_cost = beam_cost + column_cost
        return final_cost

    def get_conc_cost(self, beam_names ,column_names, full_data):
        beam_cost = self.calculate_beam_cost(beam_names=beam_names, full_data=full_data)[2]
        column_cost = self.calculate_column_cost(column_names=column_names, full_data=full_data)[2]
        final_cost = beam_cost + column_cost
        return final_cost

    def get_framework_cost(self, beam_names ,column_names, full_data):
        beam_cost = self.calculate_beam_cost(beam_names=beam_names, full_data=full_data)[3]
        column_cost = self.calculate_column_cost(column_names=column_names, full_data=full_data)[3]
        final_cost = beam_cost + column_cost
        return final_cost

    def os_error_beam(self, beams,full_data):
        area = []
        for ID in beams:
            results_beam = self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)
            eror = results_beam[-3]
            u = self.etabs.FrameObj.GetSection(ID)[0]
            eff_height = full_data[ID]['height']-4.5
            eff_width = full_data[ID]["width"]
            for k in range(len(eror)):
                if eror[k] == "Reinforcing required exceeds maximum allowed":
                    top_area = results_beam[4][k]
                    bot_area = self.etabs.DesignConcrete.GetSummaryResultsBeam(ID)[6][k]
                    ro = (bot_area+top_area)*100/(eff_width*eff_height)
                    area.append(ro/2.5)
        return area























