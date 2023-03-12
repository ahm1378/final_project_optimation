from runetabs import RunConcrete


class ForceColumn(RunConcrete):

    def column_load(self, name):
        combos = self.get_combo()
        self.etabs.AnalysisResultsSetup.DeselectAllCasesAndCombosForOutput()
        for u in combos:
            self.etabs.AnalysisResultsSetup.SetComboSelectedForOutput(u)

        x = self.etabs.AnalysisResults.FrameForce(name, 0)
        data = [x[2], x[5], x[8], x[9], x[10], x[11], x[12], x[13]]
        P_M3 = []
        for x in range(len(data[1])):
            P_M3.append((data[7][x] ** 2) + (data[2][x] ** 2))
        for u in range(len(data)):
            data[u] = [x for _, x in sorted(zip(P_M3, data[u]))]
        loads = {}
        for x in range(len(data[1])):
            try:
                loads[data[0][x]].append({"P": data[2][x], "M2": data[6][x], "M3": data[7][x]})
            except KeyError:
                loads[data[0][x]] = []
        return loads