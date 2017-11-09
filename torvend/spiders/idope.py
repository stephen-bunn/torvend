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
        'xxx': items.TorrentCategory.Porn,
        'images': items.TorrentCategory.Image,
        'games': items.TorrentCategory.Game,
        'others': items.TorrentCategory.Unknown,
    }

    @property
    def paging_results(self):
        return self._paging_results

    @property
    def query_url(self):
        return self._query_url

    def start_requests(self):
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
        soup = self.get_soup(response.text, is_content=True)

        for result in soup\
                .find('div', {'id': 'div2child'})\
                .find_all('div', {'class': 'resultdiv'}):
            torrent = items.Torrent()
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
            torrent['magnet'] = (
                'magnet:?xt=urn:btih:{0}&dn'
            ).format(result.find(
                'div', {'class': 'hideinfohash'}
            ).contents[0].strip())

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
