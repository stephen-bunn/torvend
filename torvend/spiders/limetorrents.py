#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import re

from .. import (items,)
from ._common import (BaseSpider,)

import furl
import scrapy


class LimeTorrentsSpider(BaseSpider):

    name = 'limetorrents'
    allowed_domains = [
        'www.limetorrents.cc',
    ]

    _category_map = {
        'movies': items.TorrentCategory.Video,
        'tv shows': items.TorrentCategory.Video,
        'music': items.TorrentCategory.Audio,
        'applications': items.TorrentCategory.Application,
        'games': items.TorrentCategory.Game,
        'anime': items.TorrentCategory.Video,
        'other': items.TorrentCategory.Unknown,
    }

    @property
    def paging_index(self):
        """ Required property for paging indexing.

        :returns: The starting index of pages
        :rtype: int
        """

        return 1

    @property
    def paging_results(self):
        """ Required property for paging results.

        :returns: The number of results per queried page
        :rtype: int
        """

        return 36

    @property
    def query_scheme(self):
        """ Required property for query scheme.

        :returns: The scheme the query needs
        :rtype: str
        """

        return 'http'

    @property
    def query_path(self):
        """ Required property for the query path.

        :returns: The path the query needs
        :rtype: str
        """

        return '/search/all/{query}/seeds/{page}/'

    def _parse_torrent(self, response):
        """ Handle parsing torrent info.

        :param response: The response instance from ``start_requests``
        :type response: scrapy.Request
        :returns: Yields torrent items
        :rtype: list[items.Torrent]
        """

        torrent = response.meta['torrent']
        soup = self.get_soup(response.text)
        result = soup.find('div', {'class': 'torrentinfo'})

        result_table = result.find('table')
        torrent['hash'] = result_table\
            .find('tr')\
            .find_all('td')[-1].contents[0]

        torrent['magnet'] = result\
            .find('a', {'href': re.compile(r'^magnet:.*')}).attrs['href']

        torrent['categories'] = [
            self._category_map.get(
                result_table.find_all('tr')[1].find_all(
                    'td'
                )[-1].find('a').contents[0].strip().lower(),
                items.TorrentCategory.Unknown
            )
        ]

        # handle missing torrent fields
        (torrent['uploaded'], torrent['uploader'],) = (None, None,)
        yield torrent

    def parse(self, response):
        """ Required first level page parser.

        :param response: The response instance from ``start_requests``
        :type response: scrapy.Request
        :returns: Yields additional scrapy requets
        :rtype: list[scrapy.Request]
        """

        soup = self.get_soup(response.text)

        try:
            results = soup\
                .find('table', {'class': 'table2'})\
                .find_all('tr')[1:]
        except AttributeError:
            return

        for result in results:
            torrent = items.Torrent(spider=self.name)

            name_link = result.find(
                'div', {'class': 'tt-name'}
            ).find_all('a')[-1]
            torrent['name'] = name_link.contents[0].strip()
            torrent['source'] = furl.furl(response.url).set(
                path=name_link.attrs['href'], args={}
            ).url

            torrent['size'] = self.parse_size(result.find_all(
                'td', {'class': 'tdnormal'}
            )[-1].contents[0].strip())

            torrent['seeders'] = int(result.find(
                'td', {'class': 'tdseed'}
            ).contents[0].strip().replace(',', ''))
            torrent['leechers'] = int(result.find(
                'td', {'class': 'tdleech'}
            ).contents[0].strip().replace(',', ''))

            torrent_request = scrapy.Request(
                torrent['source'],
                callback=self._parse_torrent
            )
            torrent_request.meta['torrent'] = torrent
            yield torrent_request
