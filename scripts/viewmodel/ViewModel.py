import logging

import networkx as nx

right_node_count = 50
left_node_count = 3


class ViewModel:
    def __init__(self, model):
        self.model = model
        self.link = None
        self.network = None
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
        # self.link = link
        #         read network
        print(self.link)
        await self.model.get_article_data(title="Bitwa pod Cedynią")
        self.network = self.model.network
        print(self.network)
        self.available_languages = ["pl", "en", "de", "fr", "cz"]
        self.selected_languages = self.available_languages
        self.timeline_values = ["2019-01-01", "2020-12-31"]
        self.selected_timeline_value = self.timeline_values[0]

    def is_existing(self, link):
        return link == "wiki"

    def update_selected_languages(self, selected):
        self.selected_languages = selected
        print("selected languages:", selected)
        # update network

    def update_analysis_mode(self, selected):
        self.analysis_mode = selected
        print(selected)
        # update network

    def get_network(self):
        G = self.model.network
        return G, nx.bipartite.sets(G)[0], nx.bipartite.sets(G)[1]

    def get_nodes_names(self):
        return ["art %d" % i for i in range(0, len(self.network))]

    def get_nodes_fragments(self):
        return ["fragment %d" % i for i in range(0, len(self.network))]

    def update_timeline_value(self, selected):
        print(selected)
        self.selected_timeline_value = selected
        #         update network
