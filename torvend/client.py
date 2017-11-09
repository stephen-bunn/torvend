#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import inspect

from . import (const, meta, spiders,)

import blinker
import scrapy.crawler
import scrapy.signals
import twisted.internet


class Client(meta.Loggable):
    on_torrent = blinker.Signal()

    def __init__(self, settings={}, ignored=[], verbose=False):
        (self.settings, self.ignored, self.verbose,) = \
            (settings, ignored, verbose,)

    @property
    def verbose(self):
        if not hasattr(self, '_verbose'):
            self._verbose = False
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        assert isinstance(verbose, bool), (
            "verbose must be a boolean, received '{verbose}'"
        ).format(**locals())
        self._verbose = verbose
        if not self._verbose:
            const.verbose = False

    def _handle_torrent(self, item, spider):
        self.log.info((
            'discovered torrent `{item}` from spider `{spider}`'
        ).format(**locals()))
        self.on_torrent.send(item, spider=spider)

    def get_spiders(self):
        return [
            spider_class
            for (_, spider_class,) in inspect.getmembers(
                spiders,
                predicate=inspect.isclass
            )
        ]

    def search(self, query, results=30):
        crawl_runner = scrapy.crawler.CrawlerRunner({
            'BOT_NAME': const.module_name,
            'USER_AGENT': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) '
                'Gecko/20100101 Firefox/39.0'
            ),
            'LOG_ENABLED': self.verbose,
        })

        for spider_class in self.get_spiders():
            if spider_class not in self.ignored:
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
                '`{self._handle_torrent}`'
            ).format(**locals()))
            crawler.signals.connect(
                self._handle_torrent,
                scrapy.signals.item_scraped
            )

        self.log.info((
            'starting crawl for query `{query}` with `{crawler_count}` '
            'different crawlers'
        ).format(crawler_count=len(crawl_runner.crawlers), **locals()))
        delay = crawl_runner.join()
        delay.addBoth(lambda _: twisted.internet.reactor.stop())
        twisted.internet.reactor.run()
