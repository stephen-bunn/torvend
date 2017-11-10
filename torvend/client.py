#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import inspect

from . import (const, meta, spiders,)

import scrapy.crawler
import scrapy.signals
import twisted.internet


class Client(meta.Loggable):
    """ The client for discovering torrents.
    """

    def __init__(self, settings={}, ignored=[], allowed=[], verbose=False):
        """ Initializes the client.

        :param settings: Any additional settings for the scrapy crawler
        :type settings: dict[str,....]
        :param ignored: Any ignored spiders
        :type ignored: list[torvend.spiders._common.BaseSpider]
        :param bool verbose: A flag to indicate if verbose logging is enabled
        """

        (self.settings, self.ignored, self.allowed, self.verbose,) = \
            (settings, ignored, allowed, verbose,)

        if len(self.ignored) > 0 and len(self.allowed) > 0:
            raise ValueError((
                "usage of both 'ignored' and 'allowed' in client '{self}' "
                "is not supported"
            ).format(**locals()))

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

    def get_spiders(self):
        """ Returns a list of spider classes.

        :returns: A list of spider classes
        :rtype: list[torvend.spiders._common.BaseSpider]
        """

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

        crawl_runner = scrapy.crawler.CrawlerRunner(dict(**self.settings, **{
            'BOT_NAME': const.module_name,
            'USER_AGENT': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) '
                'Gecko/20100101 Firefox/39.0'
            ),
            'LOG_ENABLED': self.verbose,
        }))

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
            self.log.debug((
                'connecting item signal for spider `{crawler}` to '
                '`{callback}`'
            ).format(**locals()))
            crawler.signals.connect(
                callback,
                scrapy.signals.item_scraped
            )

        self.log.info((
            'starting crawl for query `{query}` with `{crawler_count}` '
            'different crawlers'
        ).format(crawler_count=len(crawl_runner.crawlers), **locals()))
        delay = crawl_runner.join()
        delay.addBoth(lambda _: twisted.internet.reactor.stop())
        twisted.internet.reactor.run()
