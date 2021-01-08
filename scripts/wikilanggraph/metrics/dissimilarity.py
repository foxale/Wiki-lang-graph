import itertools

import networkx as nx
import pandas as pd


def _calculate_dissimilarity(set1: set, set2: set, total_size: int):
    union = set1.union(set2)
    intersection = set1.intersection(set2)
    levenshtein = len(union) - len(intersection)
    return levenshtein / total_size


def calculate_dissimilarity_metrics(graph: nx.Graph) -> pd.Series:
    lang_nodes = {node for node in graph if "__" in node}
    scores = pd.DataFrame(columns=["lang_1", "lang_2", "score"]).set_index(
        ["lang_1", "lang_2"]
    )["score"]
    for lang_node1, lang_node2 in itertools.combinations(lang_nodes, 2):
        lang1 = lang_node1.split("__")[-1]
        lang2 = lang_node2.split("__")[-1]
        neighbors1 = {*graph.neighbors(lang_node1)}
        neighbors2 = {*graph.neighbors(lang_node2)}
        scores.loc[(lang1, lang2)] = _calculate_dissimilarity(
            neighbors1, neighbors2, len(graph.nodes) - len(lang_nodes)
        )
    scores = pd.concat([scores, scores.swaplevel(0, 1)])
    scores = scores.sort_index()
    return scores
