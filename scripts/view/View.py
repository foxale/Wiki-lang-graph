import random

from bokeh.document import without_document_lock
from bokeh.layouts import column, row
from bokeh.models import Plot, Range1d, HoverTool, TapTool, BoxSelectTool, Circle, MultiLine, WheelZoomTool, \
    NodesAndLinkedEdges, Paragraph, Slider, TextInput, CheckboxGroup, RadioGroup
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
from tornado.ioloop import IOLoop

from scripts.view.Layouts import degree_bipartite_layout


class View:
    def __init__(self, view_model):
        self.view_model = view_model
        self.input_error_message = None
        self.visualization = None

    # @without_document_lock
    def modify_doc(self, doc):

        def make_graph():
            print("star drawing")
            G, left_nodes, right_nodes = self.view_model.network, \
                                         ['Q551419', 'Q53436', 'Q1902443', 'Q2607319', 'Q7695'], \
                                         ['Q184481', 'Q8030290', 'Q697224', 'Q28989', 'Q428713', 'Q9283394', 'Q8083', 'Q511158', 'Q570164', 'Q1733', 'Q42884', 'Q393', 'Q270', 'Q29182', 'Q1540926', 'Q837268', 'Q88598', 'Q53435', 'Q12548', 'Q9379230', 'Q207645', 'Q180898', 'Q11714162', 'Q1187484', 'Q275425', 'Q1569578', 'Q1259667', 'Q11826232', 'Q890527', 'Q2', 'Q313099', 'Q9168901', 'Q10950147', 'Q47315', 'Q23575', 'Q7015', 'Q12554', 'Q11755799', 'Q405155', 'Q192620', 'Q1250916', 'Q2597214', 'Q326712', 'Q2426', 'Q428443', 'Q40623', 'Q696726', 'Q134435', 'Q36', 'Q1937043', 'Q2665', 'Q29171', 'Q201823', 'Q913582', 'Q149425', 'Q12743', 'Q17648140', 'Q11747768', 'Q4191783', 'Q552', 'Q11720431', 'Q350504', 'Q156108', 'Q20643855', 'Q677905', 'Q104520', 'Q3284197', 'Q4501675', 'Q268', 'Q14945', 'Q2429', 'Q183', 'Q40477', 'Q1892006', 'Q43915', 'Q11736229', 'Q2329143', 'Q954143', 'Q680838', 'Q545', 'Q16513244', 'Q703390', 'Q1862', 'Q50872', 'Q1644', 'Q748289', 'Q63166', 'Q8890160', 'Q2150462', 'Q101985', 'Q1541827', 'Q677501', 'Q669970', 'Q150512', 'Q251395', 'Q3044', 'Q59532', 'Q146246', 'Q8052', 'Q11710470', 'Q583223', 'Q212658', 'Q371409', 'Q860981', 'Q207272', 'Q277392', 'Q1140492', 'Q598774', 'Q593045', 'Q723957', 'Q315921', 'Q138107', 'Q422376', 'Q698027', 'Q246863', 'Q74302', 'Q3355920', 'Q13408539', 'Q605977', 'Q1773668', 'Q172107', 'Q1049697', 'Q3636391', 'Q1132994', 'Q170346', 'Q6722016', 'Q152499', 'Q641479', 'Q718839', 'Q2026486', 'Q631991', 'Q1236849', 'Q2985977', 'Q932228', 'Q703893', 'Q2505294', 'Q1132940', 'Q164092', 'Q159512', 'Q840454', 'Q7510414', 'Q631163', 'Q2552993', 'Q581254', 'Q33057', 'Q361', 'Q1259201', 'Q834498', 'Q874784', 'Q162333', 'Q842774', 'Q835649', 'Q570504', 'Q684324', 'Q462964', 'Q2388056', 'Q597533', 'Q720936', 'Q170496', 'Q148505', 'Q11713274', 'Q1044829', 'Q3625471', 'Q289511', 'Q1402078', 'Q1567698', 'Q821283', 'Q473670', 'Q3544088', 'Q78994', 'Q306150', 'Q937255', 'Q74298', 'Q2373506', 'Q582613', 'Q362', 'Q353227', 'Q2065144', 'Q179250', 'Q1207310', 'Q4501692', 'Q211371', 'Q2065551', 'Q2667645', 'Q617281', 'Q186284', 'Q545449', 'Q160928', 'Q199569', 'Q2066991', 'Q158677', 'Q454304', 'Q838931', 'Q33570', 'Q2487', 'Q974251', 'Q2521878', 'Q7969327', 'Q14635000', 'Q211274', 'Q897466', 'Q701627', 'Q200855', 'Q39193', 'Q4122600', 'Q201615', 'Q5202287', 'Q3016850', 'Q2628423', 'Q839234', 'Q897720', 'Q175211', 'Q937332', 'Q1352215', 'Q1645044', 'Q118335', 'Q149234', 'Q654006', 'Q32832', 'Q150812', 'Q4871609', 'Q849176', 'Q2667608', 'Q11710528', 'Q700842', 'Q558423', 'Q719515', 'Q700264', 'Q924600', 'Q1933729', 'Q182865', 'Q977282', 'Q7210108', 'Q160161', 'Q1495944', 'Q2545349', 'Q151616', 'Q2560470', 'Q687151', 'Q260260', 'Q107802', 'Q153080', 'Q157802', 'Q7049', 'Q5124786', 'Q15214996', 'Q158281', 'Q23784', 'Q23647', 'Q148499']
            print("got the network")

            width = 900
            height = 20 * len(right_nodes)
            plot = Plot(plot_width=width, plot_height=height,
                        x_range=Range1d(-1.1, 1.1), y_range=Range1d(-height / (2 * width), height / (2 * width)))
            plot.title.text = "Visualization of article versions and links"

            plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

            layout = degree_bipartite_layout(G, left_nodes, right_nodes)
            graph_renderer = from_networkx(G, layout, scale=1, center=(0, 0))

            graph_renderer.node_renderer.data_source.data['name'] = self.view_model.get_nodes_names()
            graph_renderer.node_renderer.data_source.data['fragment'] = self.view_model.get_nodes_fragments()

            left_nodes_list = list(left_nodes)
            left_colors = ["#%06x" % random.randint(0, 0xFFFFFF) for n in left_nodes_list]
            colors = [Spectral4[1] if n not in left_nodes else left_colors[left_nodes_list.index(n)] for n in G]
            graph_renderer.node_renderer.data_source.data['color'] = colors

            max_right_degree = max([G.degree(r) for r in right_nodes])
            alpha = [0.5 if n in left_nodes else G.degree(n) / max_right_degree for n in G]
            graph_renderer.node_renderer.data_source.data['alpha'] = alpha

            graph_renderer.node_renderer.glyph = Circle(size=15, fill_color="color", fill_alpha="alpha",
                                                        line_color="color", line_width=1, line_alpha=1)
            graph_renderer.node_renderer.selection_glyph = Circle(size=15, fill_color="color", fill_alpha="alpha",
                                                                  line_color="color", line_width=5, line_alpha=0.5)
            graph_renderer.node_renderer.hover_glyph = Circle(size=15, fill_color="color", fill_alpha="alpha",
                                                              line_color="color", line_width=3, line_alpha=0.8)
            graph_renderer.node_renderer.glyph.properties_with_values()

            edges_colors = [colors[list(G).index(e[0])] for e in G.edges()]
            graph_renderer.edge_renderer.data_source.data['color'] = edges_colors
            graph_renderer.edge_renderer.glyph = MultiLine(line_color="color", line_alpha=0.5, line_width=2)
            graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color="color", line_alpha=1, line_width=5)
            graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color="color", line_alpha=0.8, line_width=3)

            hover = HoverTool(tooltips=[("name", "@name"), ("short description", "@fragment")])
            plot.add_tools(hover, TapTool(), BoxSelectTool(), WheelZoomTool())

            graph_renderer.selection_policy = NodesAndLinkedEdges()
            graph_renderer.inspection_policy = NodesAndLinkedEdges()

            plot.renderers.append(graph_renderer)
            print("rendered")
            return plot

        def make_timeline_slider():
            header = Paragraph(text="Select moment in time: %s" % self.view_model.selected_timeline_value)

            selected_index = 0 if self.view_model.network is None else self.view_model.timeline_values.index(
                self.view_model.selected_timeline_value)
            slider = Slider(
                start=0,
                end=len(self.view_model.timeline_values) - 1,
                value=selected_index, show_value=False,
                step=1)

            def update_timeline_value(attr, old, new):
                new_value = self.view_model.timeline_values[new]
                self.view_model.update_timeline_value(new_value)
                header.text = "Select moment in time: %s" % new_value
                doc.clear()
                self.modify_doc(doc)

            slider.on_change("value", update_timeline_value)
            return column(header, slider)

        def make_text_input():
            text_input = TextInput(
                title="Insert link to wikipedia article",
                value="link" if self.view_model.link is None else self.view_model.link
            )

            def update_link(attr, old, new):
                if self.view_model.is_existing(new):
                    print("YAY!")
                    self.input_error_message = None
                    self.view_model.update_link(new)
                else:
                    print("boooo....")
                    self.input_error_message = "Link %s not found." % old
                    self.view_model.update_link(None)
                doc.clear()
                # print(list(self.view_model.model.network)[5:])
                self.modify_doc(doc)

            text_input.on_change('value', update_link)
            return text_input

        def make_static_header(text):
            return Paragraph(text=text)

        def make_language_checkbox():
            options = self.view_model.available_languages
            checked = self.view_model.selected_languages

            def update_selected(attr, old, new):
                selection = list()
                for i in new:
                    selection.append(i)
                self.view_model.update_selected_languages(selection)
                doc.clear()
                self.modify_doc(doc)

            active = [] if checked is None else [options.index(c) for c in checked]
            checkbox_group = CheckboxGroup(
                name="languages",
                labels=options,
                active=active
            )
            checkbox_group.on_change("active", update_selected)
            return checkbox_group

        def make_analysis_mode_radio():
            def update_selected(attr, old, new):
                self.view_model.update_analysis_mode(new)
                doc.clear()
                self.modify_doc(doc)

            active = self.view_model.analysis_mode
            radio_group = RadioGroup(
                name="analysis_mode",
                labels=self.view_model.analysis_options,
                active=active
            )
            radio_group.on_change("active", update_selected)
            return radio_group

        def make_error_text():
            text_output = Paragraph(text=self.input_error_message, style={'color': 'red'})
            return text_output

        if self.input_error_message is not None:
            print("there was error")
            doc.add_root(row(
                column(
                    make_static_header("Wiki-lang-graph"),
                    make_text_input(),
                    make_error_text(),
                    margin=(10, 10, 10, 10)
                )
            ))
        elif self.input_error_message is None and self.view_model.network is None:
            print("network was none")
            doc.add_root(row(
                column(
                    make_static_header("Wiki-lang-graph"),
                    make_text_input(),
                    margin=(10, 10, 10, 10)
                )
            ))
        else:
            print("network was there")
            self.visualization = make_graph()
            doc.add_root(row(
                column(
                    make_static_header("Wiki-lang-graph"),
                    make_text_input(),
                    make_static_header("Select from available languages"),
                    make_language_checkbox(),
                    make_timeline_slider(),
                    make_static_header("What kind of analysis is performed?"),
                    make_analysis_mode_radio(),
                    margin=(10, 10, 10, 10)
                ),
                column(
                    make_static_header("Most different versions: "),
                    make_static_header("Difference is: "),
                    self.visualization,
                    margin=(10, 10, 10, 10)
                )
            ))