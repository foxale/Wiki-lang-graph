import networkx as nx
import logging

from scripts.wikilanggraph import generate_lang_graph, calculate_dissimilarity_metrics
from scripts.wikilanggraph import initialize_graph
from scripts.wikilanggraph import initialize_starting_page
from scripts.wikilanggraph.wikipedia_page import RevisionKey, Page


class Model:
    def __init__(self):
        self.network = None
        self.metrics = None
        self.df = None
        self.timestamps = None

    """
    this method should return:
    - a network representing article and links (for all available languages)
    - a pandas dataframe containing information on consecutive nodes of network: title, language, short fragment,
    is node a backlink, is node right-sided (is a language version)
    - a list of available moments in time for analysis of previous versions
    """

    async def get_article_data(self, title, moment_in_time=None):
        languages = ("pl", "en", "de", "fr", "cz")
        article_language = "pl"

        graph: nx.Graph = initialize_graph()
        starting_page = initialize_starting_page(
            language=article_language, title="Bitwa pod Cedynią"
        )
        graph = await generate_lang_graph(
            graph=graph, starting_page=starting_page, languages=languages
        )

        metrics = calculate_dissimilarity_metrics(graph=graph)
        timestamps = starting_page.timepoints_all_languages
        self.metrics = metrics
        self.timestamps = timestamps

        logging.info("Graph: \n %s", nx.info(graph))
        logging.info("Metrics: \n %s", metrics.to_string())
        logging.info("Timestamps: %s", timestamps)

        temp_timestamp: RevisionKey = timestamps[0]
        temp_graph = initialize_graph()
        page = Page(
            language=temp_timestamp.language,
            title=temp_timestamp.title,
            revision=temp_timestamp.oldid,
            timestamp=temp_timestamp.timestamp,
        )
        temp_graph = await generate_lang_graph(
            graph=temp_graph, starting_page=page, languages=languages
        )

        self.network = temp_graph

