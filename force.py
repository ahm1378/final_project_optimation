import json

from runetabs import RunConcrete


class LoadForce(RunConcrete):

    def set_combo(self):
        comb = self.etabs.Combination.GetNameList()
        self.etabs.AnalysisResultsSetup.DeselectAllCasesAndCombosForOutput()
        for u in comb[1]:
            self.etabs.AnalysisResultsSetup.SetComboSelectedForOutput(u)
        return comb

    def beam_load(self, general_data):
        self.etabs.AnalysisResultsSetup.DeselectAllCasesAndCombosForOutput()
        self.etabs.AnalysisResultsSetup.SetComboSelectedForOutput("envelop")
        name_id = self.get_beams_unique_names(general_frame_data=general_data)
        return self.etabs.AnalysisResults.FrameForce(name_id[0], 0)









