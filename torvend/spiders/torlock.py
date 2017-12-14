# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import re

from .. import (items,)
from ._common import (BaseSpider,)

import furl
import scrapy


class TorlockSpider(BaseSpider):

    name = 'torlock'
    allowed_domains = [
        'torlock.com',
    ]

    _category_map = {
        'movies': items.TorrentCategory.Video,
        'television': items.TorrentCategory.Video,
        'music': items.TorrentCategory.Audio,
        'anime': items.TorrentCategory.Video,
        'software': items.TorrentCategory.Application,
        'games': items.TorrentCategory.Game,
        'ebooks': items.TorrentCategory.Book,
        'audiobook': items.TorrentCategory.Audio,
        'images': items.TorrentCategory.Image,
        'adult': items.TorrentCategory.Adult,
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

        return 75

    @property
    def query_scheme(self):
        """ Required property for query scheme.

        :returns: The scheme the query needs
        :rtype: str
        """

        return 'https'

    @property
    def query_path(self):
        """ Required property for the query path.

        :returns: The path the query needs
        :rtype: str
        """

        return '/all/torrents/{query}/{page}.html'

    def _parse_torrent(self, response):
        """ Handle parsing torrent info.

        :param response: The response instance from ``start_requests``
        :type response: scrapy.Request
        :returns: Yields torrent items
        :rtype: list[items.Torrent]
        """

        torrent = response.meta['torrent']
        soup = self.get_soup(response.text)

        torrent['magnet'] = soup\
            .find('article')\
            .find('table')\
            .find('a', {'href': re.compile(r'^magnet:.*')}).attrs['href']

        result = soup\
            .find_all('div', {'class': 'well'})[1]\
            .find('div', {'class': 'row'})\
            .find_all('div')[1]

        (category_div, infohash_div,) = result\
            .find_all('dl', {'class': 'dl-horizontal'})[1:3]
        torrent['hash'] = infohash_div.find('dd').contents[0].lower().strip()
        torrent['categories'] = [
            self._category_map.get(
                category_div.find('dd').find('a').contents[0].strip().lower(),
                items.TorrentCategory.Unknown
            )
        ]

        torrent['uploader'] = None
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
                .find('div', {'class': 'panel-default'})\
                .find('table')\
                .find_all('tr')[1:]
        except AttributeError:
            return

        for result in results:
            torrent = items.Torrent(spider=self.name)
            name_link = result.find('td').find('div').find('a')

            torrent['name'] = name_link.text.strip()
            torrent['source'] = furl.furl(response.url).set(
                path=name_link.attrs['href'], args={}
            ).url

            torrent['uploaded'] = self.parse_datetime(
                result.find('td', {'class': 'td'}).contents[0].strip(),
                formats=[
                    '%m/%d/%Y'
                ]
            )
            torrent['size'] = self.parse_size(
                result.find('td', {'class': 'ts'}).contents[0].strip()
            )
            torrent['seeders'] = int(result.find(
                'td', {'class': 'tul'}
            ).contents[0].strip())
            torrent['leechers'] = int(result.find(
                'td', {'class': 'tdl'}
            ).contents[0].strip())

            torrent_request = scrapy.Request(
                torrent['source'],
                callback=self._parse_torrent
            )
            torrent_request.meta['torrent'] = torrent
            yield torrent_request
