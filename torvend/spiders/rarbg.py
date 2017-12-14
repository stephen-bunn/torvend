# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import re

from .. import (items,)
from ._common import (BaseSpider,)

import furl
import scrapy


class RarbgSpider(BaseSpider):
    # FIXME: this spider is currently WIP (throttling issues)

    name = 'rarbg'
    allowed_domains = [
        'rarbg.to',
    ]

    # NOTE: rarbg.to is known to ban ips for more than 10 requests per minute
    custom_settings = {
        'download_delay': 60,
        'concurrent_requests_per_domain': 10,
        'randomize_download_delay': False,
        'autothrottle_enabled': True,
        'autothrottle_start_delay': 5,
        'autothrottle_target_concurrency': 10,
    }

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
        '4': items.TorrentCategory.Adult,
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

        return 25

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

        return 'torrents.php?search={query}&page={page}&order=seeders&by=DESC'

    def _parse_torrent(self, response):
        """ Handle parsing torrent info.

        :param response: The response instance from ``start_requests``
        :type response: scrapy.Request
        :returns: Yields torrent items
        :rtype: list[items.Torrent]
        """

        torrent = response.meta['torrent']
        soup = self.get_soup(response.text)
        result = soup\
            .find('div', {'class': 'content-rounded'})\
            .find('table', {'class': 'lista-rounded'})\
            .find('table', {'class': 'lista'})

        torrent['magnet'] = result\
            .find('td', {'class': 'lista'})\
            .find('a', {'href': re.compile(r'^magnet:.*')})\
            .attrs['href']
        torrent['hash'] = self.parse_infohash(torrent['magnet'])
        torrent['categories'] = [items.TorrentCategory.Unknown]

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
                .find('table', {'class': 'lista2t'})\
                .find_all('tr', {'class': 'lista2'})
        except AttributeError:
            return

        for result in results:
            torrent = items.Torrent(spider=self.name)
            (
                category_div, name_div, uploaded_div, size_div,
                seeders_div, leechers_div, _, uploader_div
            ) = result.find_all('td')
            torrent['name'] = name_div.text.strip()
            torrent['source'] = furl.furl(response.url).set(
                path=name_div.find('a').attrs['href'], args={}
            ).url

            torrent['uploaded'] = self.parse_datetime(
                uploaded_div.text.strip(),
                formats=[
                    '%Y-%m-%d %H:%M:%S',
                ]
            )
            torrent['size'] = self.parse_size(size_div.text.strip())

            torrent['seeders'] = int(seeders_div.text.strip())
            torrent['leechers'] = int(leechers_div.text.strip())
            torrent['uploader'] = uploader_div.text.strip()

            torrent_request = scrapy.Request(
                torrent['source'],
                callback=self._parse_torrent
            )
            torrent_request.meta['torrent'] = torrent
            yield torrent_request
