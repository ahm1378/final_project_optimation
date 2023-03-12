from preprocces import PreProcces
from collect_data import CollectData
from constants import UnitVolumeCostConcrete


class Concerete_Cost(CollectData):
    @staticmethod
    def concrete_volume(full_data):
        sumation = 0
        for frame in full_data.keys():
            sumation += full_data[frame]['length']*full_data[frame]['width']*full_data[frame]['height']
        return sumation*10**(-6)

    @staticmethod
    def convert_to_m_3(volume):
        return volume*10**(-6)

    @staticmethod
    def concrete_total_price(volume):
        return volume*962760



class IntroDesign(PreProcces):

    def change_section(self, general_data, *args):
        input_variables = self.create_x(general_frame_data=general_data)



