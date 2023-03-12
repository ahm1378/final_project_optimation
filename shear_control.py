import numpy as np
import pandas as pd
from runetabs import RunConcrete


class Shear(RunConcrete):

    def approximate_story(self):
        self.etabs.DatabaseTables.SetLoadCasesSelectedForDisplay(['EX'])
        self.etabs.Analyze.RunAnalysis()
        self.etabs.DesignConcrete.StartDesign()
        force = self.etabs.DatabaseTables.GetTableForDisplayArray('Story Forces', [], '', 0, [], 0, [])
        titr = force[2]
        data = force[4]
        lines = [list(titr)]
        j = 0
        for i in range(len(titr), len(data) + len(titr), len(titr)):
            lines.append(list(data[j:i]))
            j += len(titr)

        p_index = lines[0].index('P')
        t_index = lines[0].index('T')
        mx_index = lines[0].index('MX')
        my_index = lines[0].index('MY')
        casetype_index = lines[0].index('CaseType')
        # StepNumber_index = lines[0].index('StepNumber')
        # StepLabel_index = lines[0].index('StepLabel')

        for i in range(len(lines)):
            lines[i].remove(lines[i][casetype_index])
            lines[i].remove(lines[i][p_index - 1])
            lines[i].remove(lines[i][t_index - 2])
            lines[i].remove(lines[i][mx_index - 3])
            lines[i].remove(lines[i][my_index - 4])

        # steptype_index = lines[0].index('StepType')
        # for i in range(len(lines)):
        #     lines[i].remove(lines[i][steptype_index])
        # StepNumber_index = lines[0].index('StepNumber')
        # for i in range(len(lines)):
        #     lines[i].remove(lines[i][StepNumber_index])
        # StepLabel_index = lines[0].index('StepLabel')
        # for i in range(len(lines)):
        #     lines[i].remove(lines[i][StepLabel_index])
        raw_data = list(filter(lambda row: row[0] != "Pent", lines))
        titr = np.array(raw_data).T[0]
        final_force = np.array(raw_data).T[-1]
        clear_item = np.delete(final_force, 0).T
        list1 = clear_item.tolist()
        constant = 1000.0
        new = [float(x) for x in list1]
        res = []
        final = []
        for i in new:
            res.append(i / constant)
        for x in res:
            try:
                final.append(abs(float(x)))
            except:
                final.append(x)
        return final

    def approximate_wall(self):
        drift_cases = self.get_earthquake_force()
        ret = self.etabs.AnalysisResultsSetup.DeselectAllCasesAndCombosForOutput()
        ret = self.etabs.AnalysisResultsSetup.SetCaseSelectedForOutput(drift_cases[3])
        pier = self.etabs.AnalysisResults.PierForce()
        piers = pier[1:-1]
        raw_data = np.array(piers).T
        raw_data = list(filter(lambda row: row[3] != 'Top', raw_data))
        df = pd.DataFrame(
            raw_data,
            columns=["Story", "Pier", "Output Case", "Location", "P", "V2", "V3", "T", "M2", "M3"]
        )
        df = df.drop(["P", "T", "M2", "M3"], axis=1)
        df = df.astype(
            {
                "Story": "string",
                "Pier": "string",
                "Output Case": "string",
                "Location": "string",
                "V2": "float64",
                "V3": "float64",
            }
        )

        df["V2"] = df["V2"] / 1000
        df["V3"] = df["V3"] / 1000
        cumulative_df = df[["Story", "V2"]].groupby(["Story"]).sum()
        cumulative_df.rename(columns={"V2": "ShearSum"}, inplace=True)
        return cumulative_df

    def total_column(self):
        minus_shear = []
        floor = list(self.approximate_story())
        wal = self.approximate_wall()
        df = wal['ShearSum'].tolist()
        w = sorted(df)
        for i in range(len(df)):
            minus_shear.append(floor[i] - w[i])
        return minus_shear

    def check_50_control(self):
        control_50 = []
        floor = list(self.approximate_story())
        wal = self.approximate_wall()
        df = wal['ShearSum'].tolist()
        w = sorted(df)
        for i in range(len(df)):
            control_50.append(w[i] / floor[i])
        for i in control_50:
            if i > 0.5:
                continue
            return False
        return True

    def check_25_control(self):
        control_25 = []
        floor = list(self.approximate_story())
        frame = self.total_column()
        for i in range(len(frame)):
            control_25.append(frame[i] / floor[i])
        for i in control_25:
            if i > 0.25:
                continue
            return False
        return True