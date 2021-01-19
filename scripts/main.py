import logging
import os

import asyncio

import httpx
import networkx as nx
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

from scripts.wikilanggraph import generate_lang_graph
from scripts.view.View import View
from scripts.viewmodel.ViewModel import ViewModel
from scripts.wikilanggraph import enable_logging
from scripts.wikilanggraph.metrics.dissimilarity import calculate_dissimilarity_metrics
from scripts.wikilanggraph.lang_graph.generate_lang_graph import initialize_graph
from scripts.wikilanggraph.lang_graph.generate_lang_graph import (
    initialize_starting_page,
)
from scripts.wikilanggraph.wikipedia_page import Page
from scripts.wikilanggraph.Model import Model


async def main() -> int:
    # languages = ("pl", "en", "de", "fr", "cz")
    languages = None
    article_name = "Bitwa pod Cedynią"
    article_language = "pl"

    graph: nx.Graph = initialize_graph()
    starting_page: Page = initialize_starting_page(
        language=article_language, title=article_name
    )
    graph = await generate_lang_graph(
        graph=graph, starting_page=starting_page, languages=languages
    )
    metrics = calculate_dissimilarity_metrics(graph=graph)
    timestamps = starting_page.timepoints_all_languages

    logging.info("Graph: \n %s", nx.info(graph))
    logging.info("Metrics: \n %s", metrics.to_string())
    logging.info("Timestamps: %s", timestamps)

    async with httpx.AsyncClient() as client:
        tasks = []
        for timestamp in timestamps:
            page = Page(
                language=timestamp.language,
                title=timestamp.title,
                revision=timestamp.oldid,
                timestamp=timestamp.timestamp,
            )

            task = await page.fetch_page(client=client, make_unique=True)
            tasks.append(task)
        await asyncio.gather(*tasks)

    return 0


def init_logging() -> None:
    parent_dir = os.path.dirname(os.path.realpath(__file__))
    enable_logging(root_path=parent_dir)


if __name__ == "__main__":
    init_logging()
    model = Model()
    view_model = ViewModel(model=model)
    view = View(view_model=view_model)
    server = Server({"/": view.modify_doc}, io_loop=IOLoop.current(), num_procs=1)
    server.start()

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
