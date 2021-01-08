__all__ = ["LangGraph"]

import networkx as nx


class LangGraph(nx.Graph):
    def __init__(self, incoming_graph_data=None, **kwargs):
        super().__init__(incoming_graph_data=incoming_graph_data, **kwargs)
