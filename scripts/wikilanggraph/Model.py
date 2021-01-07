import asyncio

import networkx as nx

from scripts.wikilanggraph import generate_lang_graph
from scripts.wikilanggraph import initialize_graph
from scripts.wikilanggraph import initialize_starting_page


class Model:
    def __init__(self):
        self.network = None
        self.df = None
        self.time = None

    """
    this method should return:
    - a network representing article and links (for all available languages)
    - a pandas dataframe containing information on consecutive nodes of network: title, language, short fragment,
    is node a backlink, is node right-sided (is a language version)
    - a list of available moments in time for analysis of previous versions
    """

    def get_article_data(self, title, moment_in_time=None):
        async def get_info(title, moment_in_time=None):
            languages = ("pl", "en", "de", "fr", "cz")
            article_language = "pl"

            graph: nx.Graph = initialize_graph()
            starting_page = initialize_starting_page(
                language=article_language, title=title
            )
            self.network = await generate_lang_graph(
                graph=graph, starting_page=starting_page, languages=languages
            )
            # here a data frame and list of moments in time should be prepared
            return self.network, self.df, self.time

        # asyncio.set_event_loop(asyncio.new_event_loop())
        # return asyncio.gather(get_info("lol", "xd"))
        # executor = ThreadPoolExecutor()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # result = yield from loop.run_in_executor(executor=None, func=lambda: get_info("lol", "xd"))
        # return executor.submit(lambda: get_info("lol", "xd")).result()
        # IOLoop.current().spawn_callback(callback=lambda: get_info("lol", "xd"))
        # return self.network, self.df, self.time
        # return loop.run_until_complete(get_inf())
        result = asyncio.ensure_future(
            get_info(title="test_title", moment_in_time="test_moment")
        )
        return result
