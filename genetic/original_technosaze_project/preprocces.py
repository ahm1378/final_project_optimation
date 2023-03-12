from properties import Concerete

from section_generator import beams_generation,columns_generation


class PreProcces(Concerete):

    def create_init_section(self, general_data):

        beam_name = self.get_beams_unique_names(general_frame_data=general_data)
        column_name = self.get_columns_unique_names(general_frame_data=general_data)
        section_beam, section_column = self.etabs.FrameObj.GetSection(beam_name[0])[0], self.etabs.FrameObj.GetSection(column_name[0])[0]

        material_beam, material_column = self.etabs.PropFrame.GetRectangle(section_beam)[1],self.etabs.PropFrame.GetRectangle(section_column)[1]
        rebar_beam, rebar_column = self.etabs.PropFrame.GetRebarBeam(section_beam), self.etabs.PropFrame.GetRebarColumn(section_beam)
        for beam in beams_generation:
            self.etabs.PropFrame.SetRectangle(beam, material_beam, int(beam[4:]), int(beam[1:3]))
            self.etabs.PropFrame.SetRebarBeam(beam, rebar_beam[0], rebar_beam[1], rebar_beam[2],
                                              rebar_beam[3], rebar_beam[4], rebar_beam[5], rebar_beam[6], rebar_beam[7],
                                              )
            self.etabs.PropFrame.SetModifiers(beam, [1, 1, 1, 1, 1, 1, 1, 1])
        for column in columns_generation:
            self.etabs.PropFrame.SetRectangle(column, material_column, int(column[4:]), int(column[1:3]))
            self.etabs.PropFrame.SetRebarColumn(column, rebar_column[0], rebar_column[1],
                                                rebar_column[2], rebar_column[3], rebar_column[4], rebar_column[5],
                                                rebar_column[6],
                                                rebar_column[7],
                                                rebar_column[8],
                                                rebar_column[9],
                                                rebar_column[10],
                                                rebar_column[11],
                                                rebar_column[12],
                                                True)
            self.etabs.PropFrame.SetModifiers(column, [1, 1, 1, 1, 1, 1, 1, 1])
        return beam_name, column_name

    def create_section_by_x(self, x, column_id , beam_id):
        global columns
        global beams
        for section in range(len(x)):
            if section<len(column_id):
                self.set_section(frame_name=column_id[section], section_name=columns[section])
            else:
                self.set_section(frame_name=beam_id[section], section_name=beams[section])

    def init_section(self, general_frame_data, x, flag_modified=False):
        unique_names = self.get_unique_names(general_frame_data=general_frame_data)
        data = self.get_full_frame_data_index_id(general_frame_data)
        print(data)
        i = 0
        for name in unique_names:
            if data[name]["frame_type"] == "Beam":
                rebar_beam = self.etabs.PropFrame.GetRebarBeam(data[name]["section"])
                self.etabs.PropFrame.SetRectangle("Beam{}".format(name), data[name]['material'], data[name]["height"]+x[i]*5, data[name]
                ["width"]+x[i+1]*5)
                self.etabs.PropFrame.SetRebarBeam("Beam{}".format(name), rebar_beam[0], rebar_beam[1], rebar_beam[2],
                                                  rebar_beam[3], rebar_beam[4], rebar_beam[5], rebar_beam[6], rebar_beam[7],
                                       )
                self.etabs.FrameObj.SetSection(name, "Beam{}".format(name))
                if flag_modified:
                    self.etabs.PropFrame.SetModifiers("Beam{}".format(name), [1, 1, 1, 0.15, 1, 0.35, 1, 1])
            else:
                rebar_column = self.etabs.PropFrame.GetRebarColumn(data[name]["section"])
                self.etabs.PropFrame.SetRectangle("column{}".format(name), data[name]["material"], data[name]["height"]+x[i]*5, data[name]["width"]+x[i+1]*5)

                self.etabs.PropFrame.SetRebarColumn("column{}".format(name), rebar_column[0], rebar_column[1],
                                                    rebar_column[2], rebar_column[3], rebar_column[4], rebar_column[5], rebar_column[6],
                                         rebar_column[7],
                                         rebar_column[8],
                                         rebar_column[9],
                                         rebar_column[10],
                                         rebar_column[11],
                                         rebar_column[12],
                                         True)
                self.etabs.FrameObj.SetSection(name, "column{}".format(name))
                if flag_modified:
                    self.etabs.PropFrame.SetModifiers("column{}".format(name), [1, 1, 1, 1, 0.7, 0.7, 1, 1])
            i += 2
        return "sections created"

    def set_over_write(self):
        self.etabs.FrameObj.SetSection('92', "C50X50")



