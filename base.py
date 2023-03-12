import comtypes.client as cm
import comtypes
from logger import logger


class BaseEtabsObject:
    def __init__(self, model_path):
        etabs_object = cm.GetActiveObject("CSI.ETABS.API.ETABSObject")
        self.SapModel = etabs_object.SapModel
        self.load_patern = self.SapModel.LoadPatterns
        self.autoseismic = self.load_patern.AutoSeismic
        self.Analyze = self.SapModel.Analyze
        self.FrameObj = self.SapModel.FrameObj
        self.PointObj = self.SapModel.PointObj
        self.LoadCases = self.SapModel.LoadCases
        self.PropFrame = self.SapModel.PropFrame
        self.PropArea = self.SapModel.PropArea
        self.Group = self.SapModel.GroupDef
        self.Story = self.SapModel.Story
        self.RespCombo = self.SapModel.RespCombo
        self.DesignConcrete = self.SapModel.DesignConcrete
        self.ACI318_08_IBC2009 = self.DesignConcrete.ACI318_08_IBC2009
        self.Combination = self.SapModel.RespCombo
        self.DesignSteel = self.SapModel.DesignSteel
        self.AnalysisResults = self.SapModel.Results
        self.AnalysisResultsSetup = self.AnalysisResults.Setup
        self.AreaObj = self.SapModel.AreaObj
        self.ResponseSpectrum = self.LoadCases.ResponseSpectrum
        self.Detailing = self.SapModel.Detailing
        self.Select = self.SapModel.SelectObj
        self.story = self.SapModel.Story
        self.DatabaseTables = self.SapModel.DatabaseTables
        self.Results = self.SapModel.Results
        self.LinkObj = self.SapModel.LinkObj
        qs = self.SapModel.SetPresentUnits_2(5, 5, 2)
        if not qs:
            logger.info("units set to kgf_centimeter")
        else:
            logger.warning("units don't set successfully")


class EtabsDefaultSetting:

    def __init__(self, etabs_object):

        self.etabs = etabs_object

    def lock_unlock(self, status=False):

        qs = self.etabs.SapModel.SetModelIsLocked(status)
        if not qs:
            logger.info("{} lock successfully".format(status))
        else:
            logger.warning("lock cant work successfully with file ")

    def set_unit(self):
        # Kn:4
        # kgf:5
        # N:3
        qs = self.etabs.SapModel.SetPresentUnits_2(5, 5, 2)
        if not qs:
            logger.info("units set to kgf_centimeter")
        else:
            logger.warning("units don't set successfully")

    def save_as(self):
        return 0

