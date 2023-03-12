from data import data
import comtypes.client as cm

etabs_object = cm.GetActiveObject("CSI.ETABS.API.ETABSObject")
SapModel = etabs_object.SapModel

# Unlocking model
SapModel.SetModelIsLocked(True)
# SapModel.SetPresentUnits(14)
etabs_file = SapModel.File
# Methods: OpenFile, Save
load_pattern = SapModel.LoadPatterns

Analyze = SapModel.Analyze
AnalysisResults = SapModel.Results
AnalysisResultsSetup = AnalysisResults.Setup
Analyze.RunAnalysis()
SapModel.DesignConcrete.StartDesign()


def read_column_ids(data):
    id_list = []
    for record in data:
        if record["frame_type"] == "Column":
            id_list.append(record["id"])

    return id_list


def get_max_pmm(id_list):
    pmm_list = []
    for id in id_list:
        pmm_list.append(SapModel.DesignConcrete.GetSummaryResultsColumn(id))
    return max(pmm_list)


id_list = ["242"]
print()