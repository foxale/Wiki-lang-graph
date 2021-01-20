__all__ = ["LangGraph"]

import networkx as nx


class LangGraph(nx.Graph):
    def __init__(self, incoming_graph_data=None, **kwargs):
        super().__init__(incoming_graph_data=incoming_graph_data, **kwargs)

    def __repr__(self):
        return repr(super())

    def __str__(self):
        return repr(super())

    def __contains__(self, item):
        return super().__contains__(item)

    def __iter__(self):
        return super().__iter__()

