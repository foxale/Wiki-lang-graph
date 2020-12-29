import logging

import asyncio
from typing import Iterable
from typing import Optional

import httpx
import networkx as nx

from scripts.wikilanggraph.page import Page

logger = logging.getLogger(__name__)


def initialize_graph() -> nx.Graph:
    """Create and return an empty graph structure"""
    graph = nx.Graph()
    logger.info("Created an empty graph structure")
    return graph


def initialize_starting_page(language: str, title: str) -> Page:
    """Create and return a starting wikipedia Page"""
    page = Page(language=language, title=title)
    logging.info('Initialized starting page "%s"', page)
    return page


async def fetch_starting_page(client: httpx.AsyncClient, page: Page) -> None:
    """Fetch starting page details"""
    await page.fetch_page(client=client, make_unique=True)
    logging.info('Fetched starting page details "%s"', page)


async def fetch_starting_page_langlinks(
    client: httpx.AsyncClient, page: Page, languages: Optional[Iterable[str]]
) -> None:
    """Fetch details of starting page's langlinks"""
    await page.fetch_langlinks(client=client, languages=languages, make_unique=True)
    logging.info('Fetched starting page langlinks "%s"', set(page.langlinks))


def add_starting_page_to_graph(graph: nx.Graph, page: Page) -> None:
    """Add starting page to graph"""
    graph.add_node(page.wikibase_item, page=page)
    logging.info('Added starting page "%s" to graph "%s"', page, graph.nodes(data=True))


def add_starting_pages_langlinks_to_graph(graph: nx.Graph, page: Page) -> None:
    """Add starting page's langlinks to graph"""
    graph.add_nodes_from(page.langlinks_as_graph_nodes)
    logging.info(
        'Added starting page langlinks "%s" to graph "%s"',
        set(page.langlinks),
        graph.nodes(data=True),
    )


async def fetch_pages_links(client: httpx.AsyncClient, page: Page) -> None:
    """Fetch details of page's links"""
    await page.fetch_links(client=client)
    logging.info('Fetched pages "%s" links "%s"', page, set(page.links))


async def generate_page_graph(
    article_name: str, article_language: str, languages: Iterable[str]
) -> nx.Graph:

    G = initialize_graph()
    starting_page = initialize_starting_page(
        language=article_language, title=article_name
    )
    async with httpx.AsyncClient() as client:
        await fetch_starting_page(client=client, page=starting_page)
        add_starting_page_to_graph(graph=G, page=starting_page)
        await fetch_starting_page_langlinks(
            client=client, page=starting_page, languages=languages
        )
        add_starting_pages_langlinks_to_graph(graph=G, page=starting_page)

        tasks = {}
        for langlink in starting_page.all_language_versions:
            tasks[langlink] = fetch_pages_links(client=client, page=langlink)
        await asyncio.gather(*tasks.values())

        for langlink in starting_page.all_language_versions:
            G.add_nodes_from(langlink.links_as_graph_nodes)
            G.add_edges_from(langlink.links_as_graph_edges)

    return G
