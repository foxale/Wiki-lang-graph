import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

import networkx as nx
from tornado import gen
from tornado.ioloop import IOLoop

from scripts.wikilanggraph import generate_page_graph


class Model:
    def __init__(self):
        self.network = None
        self.df = None
        self.time = None

    """
    this method should return:
    - a network representing article and links (for all available languages)
    - a pandas dataframe containing informations on consecutive nodes of network: title, language, short fragment,
    is node a backlink, is node right-sided (is a language version)
    - a list of available moments in time for analysis of previous versions
    """
    def get_article_data(self, title, moment_in_time=None):

        async def get_info(title, moment_in_time=None):
            languages = ("pl", "en", "de", "fr", "cz")
            article_name = "Bitwa pod Cedynią"
            article_language = "pl"

            print(title)
            self.network = await generate_page_graph(
                article_name=article_name,
                article_language=article_language,
                languages=languages,
            )
            print(moment_in_time)

            # print(list(self.network)[5:])

            # here a data frame and list of moments in time should be prepared

            return self.network, self.df, self.time

        # asyncio.set_event_loop(asyncio.new_event_loop())
        # print(r)
        # return asyncio.gather(get_info("lol", "xd"))
        # executor = ThreadPoolExecutor()

        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # result = yield from loop.run_in_executor(executor=None, func=lambda: get_info("lol", "xd"))
        # return executor.submit(lambda: get_info("lol", "xd")).result()
        IOLoop.current().spawn_callback(callback=lambda: get_info("lol", "xd"))
        return self.network, self.df, self.time
