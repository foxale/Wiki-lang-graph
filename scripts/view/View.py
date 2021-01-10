import random

from bokeh.document import without_document_lock
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    Plot,
    Range1d,
    HoverTool,
    TapTool,
    BoxSelectTool,
    Circle,
    MultiLine,
    WheelZoomTool,
    NodesAndLinkedEdges,
    Paragraph,
    Slider,
    TextInput,
    CheckboxGroup,
    RadioGroup,
)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx

from scripts.view.Layouts import degree_bipartite_layout, get_degree_map


class View:
    def __init__(self, view_model):
        self.view_model = view_model
        self.input_error_message = None
        self.visualization = None

    @without_document_lock
    def modify_doc(self, doc):
        def make_graph():
            print("star drawing")
            G, left_nodes, right_nodes = (
                self.view_model.network,
                [node for node in self.view_model.network if "__" in node],
                [node for node in self.view_model.network if "__" not in node],
            )
            print("got the network")

            width = 1000

            right_nodes_degree_map = get_degree_map(G, subset=right_nodes)
            print(right_nodes_degree_map)
            key_largest_right_subset = max(right_nodes_degree_map, key=lambda deg: len(right_nodes_degree_map[deg]))
            # print(len(largest_right_subset))
            height = 15 * len(right_nodes_degree_map[key_largest_right_subset])
            vertical_margin = 0.05 * width/height

            plot = Plot(
                plot_width=width,
                plot_height=height,
                x_range=Range1d(-1.1, 1.1),
                y_range=Range1d(-0.5 - vertical_margin, 0.5 + vertical_margin),
            )
            plot.title.text = "Visualization of article versions and links"

            plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

            layout = degree_bipartite_layout(G, left_nodes, right_nodes)
            graph_renderer = from_networkx(G, layout, scale=1, center=(0, 0))

            graph_renderer.node_renderer.data_source.data["name"] = self.view_model.get_nodes_names()
            graph_renderer.node_renderer.data_source.data["fragment"] = self.view_model.get_nodes_fragments()

            left_colors = ["#%06x" % random.randint(0, 0xFFFFFF) for n in left_nodes]
            colors = [
                Spectral4[1]
                if n not in left_nodes
                else left_colors[left_nodes.index(n)]
                for n in G
            ]
            graph_renderer.node_renderer.data_source.data["color"] = colors

            max_right_degree = max([G.degree(r) for r in right_nodes])
            alpha = [0.5 if n in left_nodes else G.degree(n) / max_right_degree for n in G]
            graph_renderer.node_renderer.data_source.data["alpha"] = alpha

            graph_renderer.node_renderer.glyph = Circle(
                size=12,
                fill_color="color",
                fill_alpha="alpha",
                line_color="color",
                line_width=1,
                line_alpha=1,
            )

            graph_renderer.node_renderer.selection_glyph = Circle(
                size=12,
                fill_color="color",
                fill_alpha="alpha",
                line_color="color",
                line_width=5,
                line_alpha=0.5,
            )

            graph_renderer.node_renderer.hover_glyph = Circle(
                size=13,
                fill_color="color",
                fill_alpha="alpha",
                line_color="color",
                line_width=3,
                line_alpha=0.8,
            )

            graph_renderer.node_renderer.glyph.properties_with_values()

            edges_colors = [colors[list(G).index(e[0])] for e in G.edges()]
            graph_renderer.edge_renderer.data_source.data["color"] = edges_colors
            graph_renderer.edge_renderer.glyph = MultiLine(
                line_color="color", line_alpha=0.5, line_width=2
            )
            graph_renderer.edge_renderer.selection_glyph = MultiLine(
                line_color="color", line_alpha=1, line_width=5
            )
            graph_renderer.edge_renderer.hover_glyph = MultiLine(
                line_color="color", line_alpha=0.8, line_width=3
            )

            hover = HoverTool(
                tooltips=[("name", "@name"), ("short description", "@fragment")]
            )
            plot.add_tools(hover, TapTool(), BoxSelectTool(), WheelZoomTool())

            graph_renderer.selection_policy = NodesAndLinkedEdges()
            graph_renderer.inspection_policy = NodesAndLinkedEdges()

            plot.renderers.append(graph_renderer)
            print("rendered")
            return plot

        def make_timeline_slider():
            header = Paragraph(
                text="Select moment in time: %s"
                     % self.view_model.selected_timeline_value
            )

            selected_index = (
                0
                if self.view_model.network is None
                else self.view_model.timeline_values.index(
                    self.view_model.selected_timeline_value
                )
            )
            slider = Slider(
                start=0,
                end=len(self.view_model.timeline_values) - 1,
                value=selected_index,
                show_value=False,
                step=1,
            )

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
                value="link" if self.view_model.link is None else self.view_model.link,
            )

            def update_link(attr, old, new):
                doc.clear()
                
                async def proceed_update(new):
                    await self.view_model.update_link()
                    self.modify_doc(doc)

                if self.view_model.is_existing(new):
                    print("YAY!")
                    self.input_error_message = None
                    self.view_model.link = new
                    curdoc().add_next_tick_callback(lambda: proceed_update(new))
                else:
                    print("boooo....")
                    self.input_error_message = "Link %s not found." % old
                    self.view_model.link = None
                    self.modify_doc(doc)

            text_input.on_change("value", update_link)
            return text_input

        def make_static_header(text):
            return Paragraph(text=text)

        def make_language_checkbox():
            def update_selected(attr, old, new):
                selection = list()
                for i in new:
                    selection.append(i)
                self.view_model.update_selected_languages(selection)
                doc.clear()
                self.modify_doc(doc)

            options = self.view_model.available_languages
            checked = self.view_model.selected_languages
            active = [options.index(c) for c in checked]
            checkbox_group = CheckboxGroup(
                name="languages", labels=options, active=active
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
                active=active,
            )
            radio_group.on_change("active", update_selected)
            return radio_group

        def make_error_text():
            text_output = Paragraph(
                text=self.input_error_message, style={"color": "red"}
            )
            return text_output

        if self.input_error_message is not None:
            print("there was error")
            doc.add_root(
                row(
                    column(
                        make_static_header("Wiki-lang-graph"),
                        make_text_input(),
                        make_error_text(),
                        margin=(10, 10, 10, 10),
                    )
                )
            )
        elif self.input_error_message is None and self.view_model.network is None:
            print("network was none")
            doc.add_root(
                row(
                    column(
                        make_static_header("Wiki-lang-graph"),
                        make_text_input(),
                        margin=(10, 10, 10, 10),
                    )
                )
            )
        else:
            print("network was there")
            self.visualization = make_graph()
            doc.add_root(
                row(
                    column(
                        make_static_header("Wiki-lang-graph"),
                        make_text_input(),
                        make_static_header("Select from available languages"),
                        make_language_checkbox(),
                        make_timeline_slider(),
                        make_static_header("What kind of analysis is performed?"),
                        make_analysis_mode_radio(),
                        margin=(10, 10, 10, 10),
                    ),
                    column(
                        make_static_header("Most different versions: "),
                        make_static_header("Difference is: "),
                        make_graph(),
                        margin=(10, 10, 10, 10),
                    ),
                )
            )
