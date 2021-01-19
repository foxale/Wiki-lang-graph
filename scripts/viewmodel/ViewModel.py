import logging
import random
import time

from scripts.viewmodel.backlinks import AnalysisMode

right_node_count = 50
left_node_count = 3


class ViewModel:
    def __init__(self, model):
        self.model = model
        self.article = None
        self.network = None
        self.left_nodes = []
        self.colors = []
        self.right_nodes = []
        self.available_languages = []
        self.selected_languages = []
        self.timeline_values = []
        self.selected_timeline_value = None
        self.analysis_mode = AnalysisMode.NO_BACKLINKS
        self.analysis_options = [
            AnalysisMode.NO_BACKLINKS,
            AnalysisMode.USE_BACKLINKS,
        ]
        self.use_backlinks = False
        self.max_metric = None

    async def update_article(self):
        logging.debug("Update link")
        logging.debug("article and language: %s" % self.article)
        article_name, language = self._parse_article_name()
        await self.model.get_article_data(
            article_name=article_name,
            article_language=language
        )
        await self.model.fetch_revisions()
        self._update_network()
        self.colors = ["#%06x" % random.randint(0, 0xFFFFFF) for _ in self.left_nodes]
        self.available_languages = [str(node).split("__")[1] for node in self.left_nodes]
        self.selected_languages = self.available_languages
        metrics = self.model.metrics.sort_values(ascending=False)
        self.max_metric = [metrics.index[0], metrics[0]]
        self.timeline_values = [t.timestamp for t in self.model.timestamps]
        self.selected_timeline_value = self.timeline_values[0]

    def update_selected_languages(self, selected):
        logging.debug("selected languages:", selected)
        self.selected_languages = selected
        self._find_metrics_by_languages()

    async def update_analysis_mode(self):
        logging.debug(self.analysis_mode)
        article_name, language = self._parse_article_name()

        if self.analysis_mode is AnalysisMode.NO_BACKLINKS:
            self.use_backlinks = False
        else:
            self.use_backlinks = True

        await self.model.get_article_data(
            article_name=article_name,
            article_language=language,
            moment_in_time=self.timeline_values.index(self.selected_timeline_value),
            use_backlinks=False
        )

        self._find_metrics_by_languages()

    async def update_timeline_value(self):
        logging.debug("Timestamp: %s" % self.selected_timeline_value)
        article_name, language = self._parse_article_name()
        await self.model.get_article_timestamp(
            article_name=article_name,
            article_language=language,
            moment_in_time=self.selected_timeline_value,
            use_backlinks=False
        )
        self._update_network()

        # slightly ugly solution to cope with new names for left nodes
        # selected languages must be updated somehow, to avoid situation
        # where there is less left nodes than selected languages to render plot properly
        self.available_languages = [str(node).split("__")[1] for node in self.left_nodes]
        initially_selected = self.selected_languages
        selected = []
        for lang in self.available_languages:
            for s_lang in self.selected_languages:
                if s_lang in lang:
                    selected.append(lang)
        self.selected_languages = selected

        self._find_metrics_by_languages()

        self.available_languages = [str(node).split("__")[1][:2] for node in self.left_nodes]
        self.selected_languages = initially_selected

    def _update_network(self):
        self.network = self.model.network
        self.left_nodes = [node for node in self.network if "__" in node]
        self.right_nodes = [node for node in self.network if "__" not in node]

    def _find_metrics_by_languages(self):
        metrics = self.model.metrics
        filtered_by_visible_languages = metrics[
            metrics.index.get_level_values('lang_1').isin(self.selected_languages)
            & metrics.index.get_level_values('lang_2').isin(self.selected_languages)
            ].sort_values(ascending=False)

        self.max_metric = \
            [filtered_by_visible_languages.index[0], filtered_by_visible_languages[0]] \
            if len(filtered_by_visible_languages) > 0 \
            else [("", ""), 0]

    def _parse_article_name(self):
        return self.article.split(' | ') if ' | ' in self.article else (self.article, None)
