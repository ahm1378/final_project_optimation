from properties import Concerete


class RunConcrete(Concerete):

    def __init__(self, flag_design=False, flag_analysis=False, *args, **kwargs ):

        super().__init__(*args, **kwargs)
        if flag_analysis:
            self.etabs.Analyze.RunAnalysis()
        if flag_design:
            self.etabs.DesignConcrete.StartDesign()

    def run_model(self):
        return self.etabs.Analyze.RunAnalysis()

    def start_design(self):

        self.etabs.DesignConcrete.StartDesign()

    def get_summary_beams(self, general_frame_data):
        beams_unique_name = self.get_beams_unique_names(general_frame_data)
        result = {
            'FrameName': [],
            'TopArea': [],
            'BotCombo': [],
            'BotArea': [],
            'VMajorArea': [],
            'TLArea': [],
            'TTArea': []
        }

        for i in beams_unique_name:
            result['FrameName'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[1][0])
            result['TopArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[4][-1])
            result['BotArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[6][-1])
            result['VMajorArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[8][-1])
            result['TLArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[10][-1])
            result['TTArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[12][-1])
        return result

    def get_summary_rebar_beams(self, general_frame_data):
        beams_unique_name = self.get_beams_unique_names(general_frame_data)
        result = {
            'FrameName': [],
            'TopArea': [],
            'BotCombo': [],
            'BotArea': [],
            'VMajorArea': [],
            'TLArea': [],
            'TTArea': []
        }

        for i in beams_unique_name:
            result['FrameName'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[1][0])
            result['TopArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[4][-1])
            result['BotArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[6][-1])
            result['VMajorArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[8][-1])
            result['TLArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[10][-1])
            result['TTArea'] .append(self.etabs.DesignConcrete.GetSummaryResultsBeam(i)[12][-1])
        return result

    def get_one_beam_summary(self, name):
        return self.etabs.DesignConcrete.GetSummaryResultsBeam(name)

    def get_beams_as_av(self, general_frame_data):
        result = []
        beam_result = self.get_summary_beams(general_frame_data)
        beams_unique_name = self.get_beams_unique_names(general_frame_data)
        for i in range(len(beams_unique_name)):
            summation_long_as = beam_result['TopArea'][i] + beam_result['BotArea'][i] + beam_result['TLArea'][i]
            summation_av_transb = beam_result['VMajorArea'][i] + 2 * beam_result['TTArea'][i]
            result .append({
                "beam_number": beams_unique_name[i],
                "frame_number": beam_result['FrameName'][i],
                'frame_As_area': summation_long_as,
                "frame_Av_area": summation_av_transb
            })

        return result