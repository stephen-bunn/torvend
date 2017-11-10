#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import re

from .. import (items,)
from ._common import (BaseSpider,)


class KickassTorrentsSpider(BaseSpider):

    name = 'kickasstorrents'
    allowed_domains = [
        'kickasstorrents.to',
        'kat.cr',
        'kickass.to',
        'kickass.cr',
        'kat.am',
    ]

    _paging_results = 25
    _query_url = 'http://{self.allowed_domains[0]}/usearch/{query}/{page}/'
    _category_map = {
        'music': items.TorrentCategory.Audio,
        'movies': items.TorrentCategory.Video,
        'apps': items.TorrentCategory.Application,
        'games': items.TorrentCategory.Game,
        'xxx': items.TorrentCategory.Adult,
        'tv': items.TorrentCategory.Video,
        'books': items.TorrentCategory.Book,
        'anime': items.TorrentCategory.Video,
    }

    @property
    def paging_results(self):
        """ Required property for paging results.

        :returns: The number of results per queried page
        :rtype: int
        """

        return self._paging_results

    @property
    def query_url(self):
        """ Required property for query url template.

        .. note:: Usually requires the existence of the ``query`` and ``page``
            format parameters

        :returns: The query format string
        :rtype: str
        """

        return self._query_url

    def parse(self, response):
        soup = self.get_soup(response.text)

        try:
            results = soup.find(
                'table', {'class': 'data'}
            ).find_all('tr', {'id': re.compile('^torrent_.*')})
        except AttributeError:
            return

        for result in results:
            print(result)
