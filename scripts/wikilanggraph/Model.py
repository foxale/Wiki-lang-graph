import asyncio

import httpx
import networkx as nx
import logging

from scripts.wikilanggraph import generate_lang_graph, calculate_dissimilarity_metrics
from scripts.wikilanggraph import initialize_graph
from scripts.wikilanggraph import initialize_starting_page
from scripts.wikilanggraph.lang_graph.generate_lang_graph import add_page_to_graph
from scripts.wikilanggraph.wikipedia_page import Page
from scripts.wikilanggraph.wikipedia_page import RevisionKeys

logger = logging.getLogger(__name__)


class Model:
    def __init__(self):
        self.network = None
        self.metrics = None
        self.df = None
        self.timestamps = None

    async def fetch_revisions(self):
        self.timestamps = self.timestamps[:20]
        async with httpx.AsyncClient() as client:
            tasks = []
            for timestamp in self.timestamps:
                page = Page(
                    title=timestamp.title,
                    language=timestamp.language,
                    revision=timestamp.oldid,
                    timestamp=timestamp.timestamp,
                )

                task = page.fetch_page(client=client, make_unique=True)
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def get_article_timestamp(self, article_name: str, moment_in_time: str, article_language='en'):
        async with httpx.AsyncClient() as client:
            graph = initialize_graph()
            starting_page = initialize_starting_page(
                language=article_language, title=article_name
            )
            languages_to_revisions = starting_page.timepoints_all_languages_as_dict

            for language, revisions in languages_to_revisions.items():
                past_revisions = RevisionKeys(revision for revision in revisions if revision.timestamp <= moment_in_time)
                if not past_revisions:
                    logger.warning("At time %s, the article %s was not available in language %s", str(moment_in_time), starting_page.title, language)
                    continue
                nearest_revision = max(past_revisions, key=lambda x: x.timestamp)
                nearest_revision_page = Page(
                    language=nearest_revision.language,
                    title=nearest_revision.title,
                    revision=nearest_revision.oldid,
                    timestamp=nearest_revision.timestamp,
                )
                await nearest_revision_page.fetch_page(client=client, make_unique=True)
                await nearest_revision_page.fetch_links(client=client)
                nearest_revision_page._links.remove_nonexistent()

                add_page_to_graph(graph=graph, page=nearest_revision_page)
                graph.add_nodes_from(nearest_revision_page.links_as_graph_nodes)
                graph.add_edges_from(nearest_revision_page.links_as_graph_edges)

        self.metrics = calculate_dissimilarity_metrics(graph=graph)
        self.network = graph

    async def get_article_data(self, article_name: str, article_language='en'):
        graph = initialize_graph()
        starting_page = initialize_starting_page(
            language=article_language, title=article_name
        )
        graph = await generate_lang_graph(
            graph=graph, starting_page=starting_page, languages=None # ('pl', 'ru', 'fr', 'simple') # ('pl', 'en', 'de', 'ru', 'fr', 'simple')
        )
        self.metrics = calculate_dissimilarity_metrics(graph=graph)
        self.timestamps = starting_page.timepoints_all_languages
        self.network = graph

        logger.info("Graph: \n %s", nx.info(graph))
        logger.info("Metrics: \n %s", self.metrics.to_string())
        logger.info("Timestamps: %s", self.timestamps)
