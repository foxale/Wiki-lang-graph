import logging
import random

import networkx as nx

right_node_count = 50
left_node_count = 3


class ViewModel:
    def __init__(self, model):
        self.model = model
        self.link = None
        self.network = None
        self.left_nodes = []
        self.colors = []
        self.right_nodes = []
        self.available_languages = []
        self.selected_languages = []
        self.timeline_values = []
        self.selected_timeline_value = None
        self.analysis_mode = 0
        self.analysis_options = [
            "Article analysis (no backlinks)",
            "Network analysis (with backlinks)",
        ]

    async def update_link(self):
        logging.debug("Update link")
        print(self.link)
        await self.model.get_article_data(title="Bitwa pod Cedynią")
        self._update_network()
        self.colors = ["#%06x" % random.randint(0, 0xFFFFFF) for node in self.left_nodes]
        self.available_languages = [str(node).split("__")[1] for node in self.left_nodes]
        self.selected_languages = self.available_languages
        self.timeline_values = ["2019-01-01", "2020-12-31"]
        self.selected_timeline_value = self.timeline_values[0]

    def is_existing(self, link):
        return link == "wiki"

    def update_selected_languages(self, selected):
        print("selected languages:", selected)
        self.selected_languages = selected
        # update network

    def update_analysis_mode(self, selected):
        self.analysis_mode = selected
        print(selected)
        # update network

    def update_timeline_value(self, selected):
        print(selected)
        self.selected_timeline_value = selected
        #         update network

    def _update_network(self):
        self.network = self.model.network
        self.left_nodes, self.right_nodes = (
            [node for node in self.network if "__" in node],
            [node for node in self.network if "__" not in node],
        )
