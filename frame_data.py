
from logger import logger


class BaseFrame:
    def __init__(self, etabs_object):

        self.etabs = etabs_object

    def general_frame_data(self, flag_group=False):
        qs = self.etabs.FrameObj.GetLabelNameList()
        ids = []
        label = []
        story = []
        if flag_group:
            group_name = self.etabs.Group.GetAssignments("All Frames")[2]
            for k in range(len(qs[1])):
                if qs[1][k] in group_name:
                    ids.append(qs[1][k])
                    label.append(qs[2][k])
                    story.append(qs[3][k])
        result = {
            'NumberNames': len(ids),
            'MyName': ids,
            'MyLabel': label,
            'MyStory': story
        }
        if not qs[-1]:
            logger.info("frame's name get successfully")
        else:
            logger.warning("can't get frame's name successfully")
        return result