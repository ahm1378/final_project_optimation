from properties import FrameProb, Concerete
from utils import polygon_area


class CollectData(Concerete):

    def get_load_area(self, name):

        try:
            loads = sum(self.etabs.AreaObj.GetLoadUniform(name)[5])
            points = self.etabs.AreaObj.GetPoints(name)[1]
            print(loads)
            print(points)
            cordinate_points = []
            for i in points:
                cordinate_points.append(self.etabs.PointObj.GetCoordCartesian(i)[0:2])
            print(polygon_area(cordinate_points))
            return abs(polygon_area(cordinate_points) * loads)
        except IndexError:
            return 0

    def find_connectivity(self, name):
        points = self.etabs.FrameObj.GetPoints(name)[0:2]
        x = self.etabs.PointObj.GetConnectivity(points[0])[1:3]
        result = []
        for i in range(len(x[0])):
            if x[0][i] == 2 and x[1][i] != name:
                result.append({''
                               'type': 'frame',
                               'name': x[1][1]})
            if x[0][i] == 5:
                result.append({''
                               'type': 'Area',
                               'name': x[1][1]})
        return result

    def number_of_each_area(self, name, general_data):
        columns = self.get_columns_unique_names(general_frame_data=general_data)

        points = self.etabs.AreaObj.GetPoints(name)[1]
        count = 0
        for i in points:
            x = self.etabs.PointObj.GetConnectivity(i)[1:3]
            for j in range(len(x[0])):
                if (x[0][j] == 2) and (x[1][j] in columns):
                    count += 1
        return count / 2

    def get_points_each_column(self, name):
        return self.etabs.FrameObj.GetPoints(name)

    def get_lengh(self, name):
        points = self.get_points_each_column(name)
        x1, y1, z1 = self.etabs.PointObj.GetCoordCartesian(points[0])[0:3]
        x2, y2, z2 = self.etabs.PointObj.GetCoordCartesian(points[1])[0:3]
        result = ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5
        return result

    def get_load_each_frame(self, name):
        length = self.get_lengh(name)
        try:
            summation_load = sum(self.etabs.FrameObj.GetLoadDistributed(name)[10])

            return abs(summation_load * length)
        except IndexError:
            return 0

    def number_of_each_Area(self, name, general_data):
        colums = self.get_columns_unique_names(general_frame_data=general_data)
        points = self.etabs.AreaObj.GetPoints(name)[1]
        count = 0
        for i in points:
            x = self.etabs.PointObj.GetConnectivity(i)[1:3]
            for j in range(len(x[0])):
                if (x[0][j] == 2) and (x[1][j] in colums):
                    count += 1
        return count / 2

    def get_columns_data(self, name, general_data, mode_predict=False,):
        points = self.get_points_each_column(name)
        x1, y1, z1 = self.etabs.PointObj.GetCoordCartesian(points[0])[0:3]
        length = self.get_lengh(name)
        dimention = self.etabs.PropFrame.GetRectangle(self.etabs.FrameObj.GetSection(name)[0])
        loads = 0
        column_nums = 0
        points = self.etabs.FrameObj.GetPoints(name)[0:2]

        result = {'loads': 0, 'height': dimention[2], 'width': dimention[3], 'columns_over': 0, 'x': x1, 'y': y1,
                  'z': z1, 'length': length}
        for point in points:
            x = self.etabs.PointObj.GetConnectivity(point)[1:3]

            for i in range(len(x[0])):

                if x[0][i] == 2 and x[1][i] != name and (x[1][i] not in self.get_columns_unique_names(general_frame_data = general_data)):
                    loads = loads + self.get_load_each_frame(x[1][i])

                if x[0][i] == 5:
                    column_nums = column_nums + self.number_of_each_Area(x[1][i], general_data=general_data) - 1
                    loads = loads + self.get_load_area(x[1][i])
        result['loads'] = loads
        result['columns_over'] = column_nums

        if not mode_predict:
            self.etabs.Analyze.RunAnalysis()
            self.etabs.DesignConcrete.StartDesign()
            pm_ratio = max(self.etabs.DesignConcrete.GetSummaryResultsColumn(name)[6])
            result['pm_ratio'] = pm_ratio
        return result

    def update_full_frame_data_columns(self, general_frame_data):
        full_last_data = self.get_full_frame_data(general_frame_data)
        for data in full_last_data:
            if data['frame_type'] == 'Column':
                data_go_to_model = self.get_columns_data(data['id'], general_data=general_frame_data, mode_predict=False)
                data['loads'] = data_go_to_model['loads']
                data['columns_over'] = data_go_to_model['columns_over']
                data['x'] = data_go_to_model['x']
                data['y'] = data_go_to_model['y']
                data['z'] = data_go_to_model['z']
        return full_last_data