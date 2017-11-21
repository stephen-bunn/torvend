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


class SkyTorrentsSpider(BaseSpider):

    name = 'skytorrents'
    allowed_domains = [
        'skytorrents.in',
    ]

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

        return 40

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

        return '/search/all/ed/{page}/{query}/?l=en-us'

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
                .find('div', {'class': 'columns'})\
                .find_all('div', {'class': 'column'})[1]\
                .find('table')\
                .find_all('tr')[1:]
        except AttributeError:
            return

        for result in results:
            torrent = items.Torrent(spider=self.name)

            (name_link, magnet_link,) = result.find('td').find_all('a')[:2]
            torrent['name'] = name_link.text.strip()
            torrent['source'] = furl.furl(response.url).set(
                path=name_link.attrs['href'], args={}
            ).url
            torrent['magnet'] = magnet_link.attrs['href']
            torrent['hash'] = self.parse_infohash(torrent['magnet'])

            (size_div, _, uploaded_div, seeders_div, leechers_div,) = \
                result.find_all('td')[1:]

            torrent['size'] = self.parse_size(size_div.text.strip())
            torrent['uploaded'] = self.parse_datetime(
                uploaded_div.text.strip(),
                formats=[
                    '%m %b %Y',
                ]
            )
            torrent['seeders'] = int(seeders_div.text.strip())
            torrent['leechers'] = int(leechers_div.text.strip())

            # NOTE: skytorrents.in does not categorize torrents
            torrent['categories'] = [items.TorrentCategory.Unknown]
            torrent['uploader'] = None

            yield torrent
