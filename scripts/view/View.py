import logging
import random

import networkx as nx
from bokeh.document import without_document_lock
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.models import DataTable
from bokeh.models import DateSlider
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
    Div
)
from bokeh.models import Slider
from bokeh.models import TableColumn
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx

from scripts.view.Layouts import degree_bipartite_layout

TITLE = "<b>Wiki-lang-graph</b>"


class View:
    def __init__(self, view_model):
        self.view_model = view_model
        self.input_error_message = None
        self.node_renderer_data_source = {}
        self.edge_renderer_data_source = {}
        self.visualization = None

    @without_document_lock
    def modify_doc(self, doc):
        def make_loading_screen():
            loading_text = Paragraph(text="Loading...")
            loading_text.sizing_mode = 'stretch_both'
            screen = loading_text
            doc.add_root(screen)

        def determine_nodes_visibility(G: nx.Graph, left_nodes):
            languages_indices = [self.view_model.available_languages.index(lang) for lang in
                                 set(self.view_model.selected_languages) & set(self.view_model.available_languages)]
            visible_left_nodes = set(left_nodes[i] for i in languages_indices)
            visible_right_nodes = set(node for left_node in visible_left_nodes for node in nx.neighbors(G, left_node))
            visibility = [
                n in visible_right_nodes or n in visible_left_nodes
                for n in list(G)
            ]
            return visibility

        def init_visualization_data(G, left_nodes, right_nodes, original_nodes_data):
            self.node_renderer_data_source["index"] = original_nodes_data["index"]
            self.node_renderer_data_source["page"] = original_nodes_data["page"]
            self.node_renderer_data_source["name"] = [p["title"] for p in original_nodes_data["page"]]
            self.node_renderer_data_source["details"] = [p["description"] for p in original_nodes_data["page"]]

            left_colors = self.view_model.colors
            colors = [
                Spectral4[1]
                if n not in left_nodes
                else left_colors[left_nodes.index(n)]
                for n in G
            ]
            self.node_renderer_data_source["color"] = colors

            self.node_renderer_data_source["visibility"] = determine_nodes_visibility(G=G, left_nodes=left_nodes)

            max_right_degree = max(G.degree(r) for r in right_nodes)
            alpha = [
                0 if self.node_renderer_data_source["visibility"][list(G).index(n)] is False
                else 0.5 if n in left_nodes
                else 0.3 + (0.7 * G.degree(n) / max_right_degree) for n in G
            ]
            self.node_renderer_data_source["alpha"] = alpha

            self.edge_renderer_data_source["start"] = [e[0] for e in G.edges()]
            self.edge_renderer_data_source["end"] = [e[1] for e in G.edges()]
            edges_colors = determine_edges_colors(G, left_nodes, colors)
            self.edge_renderer_data_source["color"] = edges_colors

            edges_visibility = determine_edges_visibility(G, left_nodes, self.node_renderer_data_source["visibility"])
            edges_alphas = [
                0 if edges_visibility[list(G.edges).index(e)] is False
                else 0.5
                for e in G.edges
            ]
            self.edge_renderer_data_source["alpha"] = edges_alphas

        def determine_edges_visibility(G: nx.Graph, left_nodes: list, nodes_visibility: list):
            visibility = []
            for e in G.edges:
                left_end = e[0] if e[0] in left_nodes else e[1]
                visibility.append(nodes_visibility[list(G).index(left_end)])
            return visibility

        def determine_edges_colors(G: nx.Graph, left_nodes: list, colors: list):
            edges_colors = []
            for e in G.edges:
                left_end = e[0] if e[0] in left_nodes else e[1]
                edges_colors.append(colors[list(G).index(left_end)])
            return edges_colors

        def prepare_plot(width=1000, height=600, vertical_margin=10):
            plot = Plot(
                plot_width=width,
                plot_height=height,
                x_range=Range1d(-1.1, 1.1),
                y_range=Range1d(-0.5 - vertical_margin, 0.5 + vertical_margin),
            )
            plot.title.text = "Visualization of article versions and internal links"
            plot.sizing_mode = 'stretch_width'
            return plot

        def make_graph():
            logging.debug("star drawing")
            G = self.view_model.network
            left_nodes = self.view_model.left_nodes
            right_nodes = self.view_model.right_nodes

            width = 1000
            height = 10 * len(right_nodes)
            vertical_margin = 0.1 * width / height

            plot = prepare_plot(width=width, height=height, vertical_margin=vertical_margin)

            plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

            layout = degree_bipartite_layout(G, left_nodes, right_nodes)
            graph_renderer = from_networkx(G, layout, scale=1, center=(0, 0))
            init_visualization_data(G=G, left_nodes=left_nodes, right_nodes=right_nodes,
                                    original_nodes_data=graph_renderer.node_renderer.data_source.data)

            graph_renderer.node_renderer.data_source.data = self.node_renderer_data_source

            graph_renderer.node_renderer.glyph = Circle(
                size=12,
                fill_color="color",
                fill_alpha="alpha",
                line_color="color",
                line_width=1,
                line_alpha="alpha",
            )

            graph_renderer.node_renderer.selection_glyph = Circle(
                size=12,
                fill_color="color",
                fill_alpha="alpha",
                line_color="color",
                line_width=5,
                line_alpha="alpha",
            )

            graph_renderer.node_renderer.hover_glyph = Circle(
                size=13,
                fill_color="color",
                fill_alpha="alpha",
                line_color="color",
                line_width=3,
                line_alpha="alpha",
            )

            graph_renderer.edge_renderer.data_source.data = self.edge_renderer_data_source
            graph_renderer.node_renderer.glyph.properties_with_values()
            graph_renderer.edge_renderer.glyph = MultiLine(
                line_color="color", line_alpha="alpha", line_width=2
            )
            graph_renderer.edge_renderer.selection_glyph = MultiLine(
                line_color="color", line_alpha="alpha", line_width=5
            )
            graph_renderer.edge_renderer.hover_glyph = MultiLine(
                line_color="color", line_alpha="alpha", line_width=3
            )

            hover = HoverTool(
                tooltips=[("name", "@name"), ("details", "@details")]
            )
            plot.add_tools(hover, TapTool(), BoxSelectTool(), WheelZoomTool())

            graph_renderer.selection_policy = NodesAndLinkedEdges()
            graph_renderer.inspection_policy = NodesAndLinkedEdges()

            plot.renderers.append(graph_renderer)
            logging.debug("network rendered")
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

            # slider = DateSlider(
            #     start=self.view_model.timeline_values[0],
            #     end=self.view_model.timeline_values[-1],
            #     value=self.view_model.selected_timeline_value,
            #     show_value=False,
            #     step=1000 * 60 * 5,
            #     format='%Y-%m-%d %H:%M'
            # )
            # slider = Slider(
            #     start=0,
            #     end=len(self.view_model.timeline_values)-1,
            #     value=self.view_model.timeline_values.index(self.view_model.selected_timeline_value),
            #     step=1000 * 60 * 60 * 24,
            #     # format='%Y-%m-%d %H:%M'
            # )

            slider = Slider(
                start=0,
                end=len(self.view_model.timeline_values) - 1,
                value=selected_index,
                show_value=False,
                step=1,
            )

            def update_timeline_value(attr, old, new):
                index = slider.value

                logging.debug("Update timeline value %s", new)
                # doc.clear()
                # make_loading_screen()

                async def proceed_update():
                    doc.clear()
                    new_value = self.view_model.timeline_values[new]
                    self.view_model.selected_timeline_value = new_value
                    await self.view_model.update_timeline_value()
                    header.text = f"Select moment in time: {new}"
                    doc.clear()
                    self.modify_doc(doc)

                curdoc().add_timeout_callback(proceed_update, timeout_milliseconds=0)

            slider.on_change("value", update_timeline_value)
            return column(header, slider)

        def make_text_input():
            title_input = TextInput(
                title="Search for the Wikipedia article",
                value="article title | language" if self.view_model.article is None else self.view_model.article,
            )

            def update_link(attr, old, new):
                doc.clear()
                make_loading_screen()

                async def proceed_update():
                    self.view_model.article = new
                    self.input_error_message = None
                    await self.view_model.update_article()
                    doc.clear()
                    self.modify_doc(doc)

                curdoc().add_next_tick_callback(proceed_update)

            title_input.on_change("value", update_link)
            return title_input

        def make_static_header(text, font_size='100%', color='black', margin='0 0 0 0'):
            return Div(text=text, style={'font-size': font_size, 'color': color, 'margin': margin})

        def make_language_checkbox():
            def update_selected(attr, old, new):
                doc.clear()
                make_loading_screen()
                selection = [self.view_model.available_languages[i] for i in new]
                self.view_model.update_selected_languages(selection)
                doc.clear()
                self.modify_doc(doc)

            options = self.view_model.available_languages
            checked = self.view_model.selected_languages
            active = [options.index(c) for c in set(checked) & set(options)]
            checkbox_group = CheckboxGroup(
                name="languages", labels=options, active=active
            )
            checkbox_group.on_change("active", update_selected)
            return checkbox_group

        def make_analysis_mode_radio():
            def update_selected(attr, old, new):
                async def proceed_update():
                    await self.view_model.update_analysis_mode()
                    doc.clear()
                    self.modify_doc(doc)

                doc.clear()
                make_loading_screen()
                self.view_model.analysis_mode = new
                curdoc().add_next_tick_callback(proceed_update)

            active = self.view_model.analysis_options.index(self.view_model.analysis_mode)
            radio_group = RadioGroup(
                name="Analysis mode",
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

        def make_dissimilarity_table():
            df = self.view_model.filtered_metrics.to_frame().reset_index()
            df = df.round(3)
            df = df.rename(columns={'lang_1': 'Language 1', 'lang_2': 'Language 2'})

            columns = [TableColumn(field=c, title=c) for c in df.columns]
            dissimilarity_table = DataTable(
                columns=columns,
                source=ColumnDataSource(df),
                autosize_mode='fit_viewport',
                height_policy='fit'
            )
            return column(
                make_static_header(text="Dissimilarity score"),
                dissimilarity_table
            )

        if self.input_error_message is not None:
            logging.info("There was error")
            column1 = column(
                make_text_input(),
                make_error_text(),
                margin=(10, 10, 10, 0),
            )
            column2 = column(
                make_static_header("Most different versions: ", color='dark-gray'),
                make_static_header("Difference is: ", color='dark-gray'),
                prepare_plot(),
                margin=(10, 10, 10, 0),
            )
            column2.sizing_mode = 'stretch_width'
            doc.add_root(
                column(
                    make_static_header(TITLE, font_size='120%'),
                    row(
                        column1,
                        column2
                    ),
                    margin=(10, 10, 0, 10),
                    sizing_mode='stretch_width'
                )
            )
        elif self.input_error_message is None and self.view_model.network is None:
            logging.info("current network was None. Display start screen")
            column1 = column(
                make_text_input(),
                margin=(10, 10, 10, 0),
            )
            column2 = column(
                prepare_plot(),
                margin=(10, 10, 10, 0),
            )
            column2.sizing_mode = 'stretch_width'
            doc.add_root(
                column(
                    make_static_header(TITLE, font_size='120%'),
                    row(
                        column1,
                        column2
                    ),
                    margin=(10, 10, 0, 10),
                    sizing_mode='stretch_width'
                )
            )
        else:
            logging.info("Network was present. Proceed to analysis screen.")
            column1 = column(
                make_text_input(),
                make_static_header("Select from available languages"),
                make_language_checkbox(),
                make_timeline_slider(),
                make_dissimilarity_table(),
                # make_static_header("What kind of analysis is performed?"),
                # make_analysis_mode_radio(),
                margin=(10, 10, 10, 0),
            )
            column2 = column(
                        # make_static_header("Most different versions: %s %s" % self.view_model.max_metric[0]),
                        # make_static_header("Difference is: %f" % self.view_model.max_metric[1]),
                        make_graph(),
                        margin=(10, 10, 10, 0)
                    )
            column2.sizing_mode = 'stretch_width'
            doc.add_root(
                column(
                    make_static_header(TITLE, font_size='120%'),
                    row(
                        column1,
                        column2
                    ),
                    margin=(10, 10, 0, 10),
                    sizing_mode='stretch_width'
                )
            )
