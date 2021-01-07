import os

import asyncio
import sys

import networkx as nx
from bokeh.io import show
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

from scripts.view.View import View
from scripts.viewmodel.ViewModel import ViewModel
from scripts.wikilanggraph import generate_page_graph
from scripts.wikilanggraph import enable_logging
from scripts.wikilanggraph.Model import Model
from tornado.platform.asyncio import AsyncIOMainLoop

AsyncIOMainLoop().install()

model = Model()
view_model = ViewModel(model=model)
view = View(view_model=view_model)
server = Server({"/": view.modify_doc}, io_loop=IOLoop.current(), num_procs=1)
# IOLoop.current().spawn_callback(view.modify_doc)
server.start()


async def main() -> int:
    languages = ("pl", "en", "de", "fr", "cz")
    article_name = "Bitwa pod Cedynią"
    article_language = "pl"

    graph: nx.Graph = await generate_page_graph(
        article_name=article_name,
        article_language=article_language,
        languages=languages,
    )
    print(nx.info(graph))
    print(list(graph)[10:])

    return 0


def init_logging() -> None:
    parent_dir = os.path.dirname(os.path.realpath(__file__))
    enable_logging(root_path=parent_dir)


if __name__ == "__main__":
    # init_logging()
    # asyncio.run(main(), debug=True)
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
