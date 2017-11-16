#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# GNU GPLv3 <https://www.gnu.org/licenses/gpl-3.0.txt>

import re

from .. import (items,)
from ._common import (BaseSpider,)

import furl
import scrapy


class OneThreeThreeSevenXSpider(BaseSpider):
    """ The spider for 1337x.to.
    """

    name = '1337x'
    allowed_domains = [
        '1337x.to',
    ]

    _category_map = {
        'movies': items.TorrentCategory.Video,
        'documentaries': items.TorrentCategory.Video,
        'music': items.TorrentCategory.Audio,
        'apps': items.TorrentCategory.Application,
        'games': items.TorrentCategory.Game,
        'xxx': items.TorrentCategory.Adult,
        'tv': items.TorrentCategory.Video,
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

        return 20

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

        return '/search/{query}/{page}/'

    def _parse_torrent(self, response):
        """ Handle parsing torrent info.

        :param response: The response instance from ``start_requests``
        :type response: scrapy.Request
        :returns: Yields torrent items
        :rtype: list[items.Torrent]
        """

        torrent = response.meta['torrent']
        soup = self.get_soup(response.text)

        result = soup.find('div', {'class': 'box-info-detail'})
        torrent['categories'] = [
            self._category_map.get(
                result.find(
                    'div', {'class': 'torrent-category-detail'}
                ).find('ul', {'class': 'list'}).find('li').find(
                    'span'
                ).contents[0].strip().lower(),
                items.TorrentCategory.Unknown
            )
        ]
        torrent['magnet'] = result.find(
            'a', {'href': re.compile(r'^magnet:.*')}
        ).attrs['href']
        torrent['hash'] = result.find(
            'div', {'class': 'infohash-box'}
        ).find('span').contents[0].strip().lower()

        yield torrent

    def parse(self, response):
        """ Required first level page parser.

        :param response: The response instance from ``start_requests``
        :type response: scrapy.Request
        :returns: Yields additional scrapy requests
        :rtype: list[scrapy.Request]
        """

        soup = self.get_soup(response.text)
        try:
            results = soup\
                .find('div', {'class': 'inner-table'})\
                .find('table')\
                .find('tbody')\
                .find_all('tr')
        except AttributeError:
            return

        for result in results:
            torrent = items.Torrent(spider=self.name)

            name_link = result\
                .find('td', {'class': 'name'})\
                .find('a', {'href': re.compile(r'^/torrent/(?:\d+)/.*')})
            torrent['name'] = name_link.contents[0].strip()
            torrent['source'] = furl.furl(response.url).set(
                path=name_link.attrs['href'], args={}
            ).url

            torrent['seeders'] = int(result.find(
                'td', {'class': 'seeds'}
            ).contents[0].strip())
            torrent['leechers'] = int(result.find(
                'td', {'class': 'leeches'}
            ).contents[0].strip())
            torrent['uploaded'] = self.parse_datetime(result.find(
                'td', {'class': 'coll-date'}
            ).contents[0].strip())
            torrent['size'] = self.parse_size(result.find(
                'td', {'class': 'size'}
            ).contents[0].strip())
            torrent['uploader'] = result.find(
                'td', {'class': 'coll-5'}
            ).find('a').contents[0].strip()

            # handle additional request
            torrent_request = scrapy.Request(
                torrent['source'],
                callback=self._parse_torrent
            )
            torrent_request.meta['torrent'] = torrent
            yield torrent_request
