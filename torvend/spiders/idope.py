#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import re
import math

from .. import (items,)
from ._common import (BaseSpider,)

import furl
import scrapy


class IDopeSpider(BaseSpider):
    """ The spider for idope.se.
    """

    name = 'idope'
    allowed_domains = [
        'idope.se',
    ]

    _paging_results = 10
    _query_url = (
        'https://{self.allowed_domains[0]}/torrent-list/{query}/?p={page}'
    )
    _category_map = {
        'music': items.TorrentCategory.Audio,
        'tv': items.TorrentCategory.Video,
        'anime': items.TorrentCategory.Video,
        'apps': items.TorrentCategory.Application,
        'books': items.TorrentCategory.Book,
        'xxx': items.TorrentCategory.Adult,
        'images': items.TorrentCategory.Image,
        'games': items.TorrentCategory.Game,
        'others': items.TorrentCategory.Unknown,
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

    def start_requests(self):
        """ The scrapy request starters.

        :returns: Yeilds requests for a sequence of pages
        :rtype: list[scrapy.Request]
        """

        for page_index in range(1, math.ceil(
            (self.results / self.paging_results)
        ) + 1):
            yield scrapy.Request(
                self.query_url.format(
                    query=self.query, page=page_index,
                    **locals()
                ),
                callback=self.parse
            )

    def parse(self, response):
        """ Required first level page parser.

        :param request: The request instance from ``start_requests``
        :type request: scrapy.Request
        :returns: Yields torrent items
        :rtype: list[items.Torrent]
        """

        soup = self.get_soup(response.text)

        for result in soup\
                .find('div', {'id': 'div2child'})\
                .find_all('div', {'class': 'resultdiv'}):
            torrent = items.Torrent(spider=self.name)

            torrent['name'] = result.find(
                'div', {'class': 'resultdivtopname'}
            ).contents[0].strip()

            source_url = furl.furl(self.query_url.format(
                query=self.query, page=0,
                **locals()
            ))
            source_url.path = result.find('a').attrs['href']
            torrent['categories'] = [
                self._category_map.get(
                    result.find(
                        'div', {'class': 'resultdivbottoncategory'}
                    ).contents[0].strip().lower()
                ),
                items.TorrentCategory.Unknown
            ]
            torrent['source'] = source_url.url
            info_hash = result.find(
                'div', {'class': 'hideinfohash'}
            ).contents[0].strip()
            torrent['hash'] = info_hash
            torrent['magnet'] = (
                'magnet:?xt=urn:btih:{info_hash}&dn'
            ).format(**locals())

            torrent['seeders'] = int(result.find(
                'div', {'class': 'resultdivbottonseed'}
            ).contents[0])
            torrent['size'] = self.parse_size(result.find(
                'div', {'class': 'resultdivbottonlength'}
            ).contents[0])
            torrent['uploaded'] = self.parse_datetime((
                '{0} ago'
            ).format(result.find(
                'div', {'class': 'resultdivbottontime'}
            ).contents[0]))

            # handle non-reported torrent fields
            torrent['leechers'] = 0
            torrent['uploader'] = None

            yield torrent
