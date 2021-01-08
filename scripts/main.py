import logging
import os

import asyncio
import sys

import networkx as nx

from scripts.wikilanggraph import generate_lang_graph
from scripts.wikilanggraph import enable_logging
from scripts.wikilanggraph.metrics.dissimilarity import calculate_dissimilarity_metrics
from scripts.wikilanggraph.lang_graph.generate_lang_graph import initialize_graph
from scripts.wikilanggraph.lang_graph.generate_lang_graph import (
    initialize_starting_page,
)


async def main() -> int:
    languages = ("pl", "en", "de", "fr", "cz")
    article_name = "Bitwa pod Cedynią"
    article_language = "pl"

    graph = initialize_graph()
    starting_page = initialize_starting_page(
        language=article_language, title=article_name
    )
    graph: nx.Graph = await generate_lang_graph(
        graph=graph, starting_page=starting_page, languages=languages
    )
    metrics = calculate_dissimilarity_metrics(graph=graph)
    timestamps = starting_page.timepoints_all_languages

    logging.info("Graph: \n %s", nx.info(graph))
    logging.info("Metrics: \n %s", metrics.to_string())
    logging.info("Timestamps: %s", timestamps)

    return 0


def init_logging() -> None:
    parent_dir = os.path.dirname(os.path.realpath(__file__))
    enable_logging(root_path=parent_dir)


if __name__ == "__main__":
    init_logging()
    sys.exit(asyncio.run(main(), debug=True) or 0)
