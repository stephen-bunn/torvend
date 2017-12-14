# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import inspect

from . import (const, meta, spiders,)

import scrapy.crawler
import scrapy.signals


class TorvendClient(meta.Loggable):
    """ The client for discovering torrents.
    """

    def __init__(self, settings={}, ignored=[], allowed=[], verbose=False):
        """ Initializes the client.

        :param settings: Any additional settings for the scrapy crawler
        :type settings: dict[str,....]
        :param ignored: Any ignored spiders
        :type ignored: list[torvend.spiders._common.BaseSpider]
        :param allowed: Any allowed spiders
        :type allowed: list[torvend.spiders._common.BaseSpider]
        :param bool verbose: A flag to indicate if verbose logging is enabled
        """

        if len(ignored) > 0 and len(allowed) > 0:
            raise ValueError((
                "usage of both 'ignored' and 'allowed' in client '{self}' "
                "is not supported"
            ).format(**locals()))

        (self.settings, self.ignored, self.allowed, self.verbose,) = \
            (settings, ignored, allowed, verbose,)

    @property
    def settings(self):
        """ Overrides for default client scrapy settings.

        :getter: Returns overriding dictionary of client scrapy settings
        :setter: Sets the overriding settings
        :rtype: dict[str,....]
        """

        if not hasattr(self, '_settings'):
            self._settings = {}
        return self._settings

    @settings.setter
    def settings(self, settings):
        """ Sets the overriding client scrapy settings.

        :param settings: The new overriding scrapy settings
        :type settings: dict[str,....]
        :rtype: None
        """

        assert isinstance(settings, dict), (
            "settings must be a dictionary, received '{settings}'"
        ).format(**locals())
        self._settings = settings

    @property
    def ignored(self):
        """ A list of ignored spider classes.

        :getter: Returns a list of ignored spider classes
        :setter: Sets the list of ignored spider classes
        :rtype: list[torvend.spiders._common.BaseSpider]
        """

        if not hasattr(self, '_ignored'):
            self._ignored = []
        return self._ignored

    @ignored.setter
    def ignored(self, ignored):
        """ Sets the list of ignored spider classes.

        :param ignored: A list of ignored spider classes
        :type ignored: list[torvend.spiders._common.BaseSpider]
        :rtype: None
        """

        if ignored:
            assert isinstance(ignored, list) and all(
                inspect.isclass(entry)
                for entry in ignored
            ) and all(
                issubclass(entry, spiders._common.BaseSpider)
                for entry in ignored
            ), (
                "ignored must be a list of spider classes, "
                "received '{ignored}'"
            ).format(**locals())
            if hasattr(self, '_allowed') and len(self._allowed) > 0:
                self.log.debug((
                    'setting ignored spiders clears allowed spiders, '
                    'currently allowed {self._allowed}'
                ).format(**locals()))
                self._allowed = []
        self._ignored = ignored

    @property
    def allowed(self):
        """ A list of allowed spider classes.

        :getter: Returns a list of allowed spider classes
        :setter: Sets the list of allowed spider classes
        :rtype: list[torvend.spiders._common.BaseSpider]
        """

        if not hasattr(self, '_allowed'):
            self._allowed = []
        return self._allowed

    @allowed.setter
    def allowed(self, allowed):
        """ Sets the list of allowed spider classes.

        :param allowed: A list of allowed spider classes
        :type allowed: list[torvend.spiders._common.BaseSpider]
        :rtype: None
        """

        if allowed:
            assert isinstance(allowed, list) and all(
                inspect.isclass(entry)
                for entry in allowed
            ) and all(
                issubclass(entry, spiders._common.BaseSpider)
                for entry in allowed
            ), (
                "allowed must be a list of spider classes, "
                "received '{allowed}'"
            ).format(**locals())
            if hasattr(self, '_ignored') and len(self._ignored) > 0:
                self.log.debug((
                    'setting allowed spiders clears ignored spiders, '
                    'currently ignored {self._ignored}'
                ).format(**locals()))
                self._ignored = []
        self._allowed = allowed

    @property
    def verbose(self):
        """ Indicates if verbose logging is enabled.

        :getter: Returns True if verbose logging is enabled
        :setter: Sets the verbose flag
        :rtype: bool
        """

        if not hasattr(self, '_verbose'):
            self._verbose = False
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        """ Sets the verbose flag.

        :param bool verbose: The new verbose flag
        :rtype: None
        """

        assert isinstance(verbose, bool), (
            "verbose must be a boolean, received '{verbose}'"
        ).format(**locals())
        self._verbose = verbose
        const.verbose = verbose

    def _item_callback(self, item, **kwargs):
        """ An item callback for logging purposes.

        :param item: The yielded item
        :param kwargs: Any additional named arguments
        :type kwargs: dict[str,....]
        :rtype: None
        """

        self.log.debug((
            'client `{self}` received item `{item}`, {kwargs}'
        ).format(**locals()))

    def get_spiders(self):
        """ Returns a list of spider classes.

        :returns: A list of spider classes
        :rtype: list[torvend.spiders._common.BaseSpider]
        """

        # NOTE: assuming allowed > 0 and ignored > 0 is not a case
        compare_allowed = len(self.allowed) > 0
        for (_, spider_class,) in inspect.getmembers(
            spiders,
            predicate=inspect.isclass
        ):
            if compare_allowed:
                if spider_class in self.allowed:
                    yield spider_class
            else:
                if spider_class not in self.ignored:
                    yield spider_class

    def search(self, query, callback, results=30):
        """ Starts the search process for a given query.

        .. note:: The callback method must accept at least a positional
            argument named ``item``.
            This is the discovered torrent item.

        :param str query: The query text to search with
        :param callable callback: A callback which receives torrent items
        :param int results: The minimum number of results for each spider to
            return
        """

        # NOTE: local import to speed up module loading
        import twisted.internet

        crawler_settings = {
            'BOT_NAME': const.module_name,
            'USER_AGENT': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) '
                'Gecko/20100101 Firefox/39.0'
            ),
            'LOG_ENABLED': self.verbose,
        }
        crawler_settings.update(self.settings)
        crawl_runner = scrapy.crawler.CrawlerRunner(crawler_settings)

        # register client available spiders
        for spider_class in self.get_spiders():
            self.log.debug((
                'registering spider `{spider_class.__name__}` to '
                'crawl runner `{crawl_runner}`'
            ).format(**locals()))
            crawl_runner.crawl(
                spider_class,
                query=query, results=results
            )

        for crawler in crawl_runner.crawlers:
            # subscribe crawler item scraped signal to client callback
            crawler.signals.connect(
                self._item_callback,
                scrapy.signals.item_scraped
            )
            # subscribe crawler item scraped signal to user given callback
            self.log.debug((
                'connecting item signal for spider `{crawler}` to '
                '`{callback}`'
            ).format(**locals()))
            crawler.signals.connect(
                callback,
                scrapy.signals.item_scraped
            )

        # begin domain parallel crawling process
        self.log.info((
            'starting crawl for query `{query}` with `{crawler_count}` '
            'different crawlers'
        ).format(crawler_count=len(crawl_runner.crawlers), **locals()))
        delay = crawl_runner.join()
        delay.addBoth(lambda _: twisted.internet.reactor.stop())
        twisted.internet.reactor.run()
