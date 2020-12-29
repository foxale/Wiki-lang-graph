import os

import asyncio
import sys

import networkx as nx

from scripts.wikilanggraph import generate_page_graph
from scripts.wikilanggraph import enable_logging


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

    return 0


def init_logging() -> None:
    parent_dir = os.path.dirname(os.path.realpath(__file__))
    enable_logging(root_path=parent_dir)


if __name__ == "__main__":
    init_logging()
    sys.exit(asyncio.run(main(), debug=True) or 0)
