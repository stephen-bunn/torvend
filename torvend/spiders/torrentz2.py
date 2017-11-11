#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

from .. import (items,)
from ._common import (BaseSpider,)

import furl


class Torrentz2Spider(BaseSpider):
    """ The spider for torrentz2.eu.
    """

    name = 'torrentz2'
    allowed_domains = [
        'torrentz2.eu',
    ]

    _category_map = {
        'audio': items.TorrentCategory.Audio,
        'video': items.TorrentCategory.Video,
        'application': items.TorrentCategory.Application,
        'ebook': items.TorrentCategory.Book,
        'adult': items.TorrentCategory.Adult,
        'images': items.TorrentCategory.Image,
        'game': items.TorrentCategory.Game,
    }

    @property
    def paging_index(self):
        """ Required property for paging indexing.

        :returns: The starting index of pages
        :rtype: int
        """

        return 0

    @property
    def paging_results(self):
        """ Required property for paging results.

        :returns: The number of results per queried page
        :rtype: int
        """

        return 50

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

        return '/search/?f={query}&p={page}'

    def parse(self, response):
        """ Required first level page parser.

        :param response: The response instance from ``start_requests``
        :type response: scrapy.Request
        :returns: Yields torrent items
        :rtype: list[items.Torrent]
        """

        soup = self.get_soup(response.text)
        try:
            results = soup\
                .find('div', {'class': 'results'})\
                .find_all('dl')
        except AttributeError:
            return

        for result in results:
            torrent = items.Torrent(spider=self.name)

            result_links = result.find('a')
            torrent['name'] = result_links.contents[0].strip()

            info_hash = furl.furl(
                result_links.attrs['href']
            ).path.segments[-1]
            torrent['hash'] = info_hash
            torrent['magnet'] = (
                'magnet:?xt=urn:btih:{info_hash}&dn'
            ).format(**locals())

            torrent['source'] = furl.furl(response.url).set(
                path=info_hash, args={}
            ).url

            result_desc = result.find('dt')
            if len(result_desc.contents[-1]) > 1 and \
                    result_desc.contents[-1].lstrip().startswith('»'):
                torrent['categories'] = [
                    self._category_map.get(
                        keyword.lower(),
                        items.TorrentCategory.Unknown
                    )
                    for keyword in result_desc.contents[-1].split(' ')[2:]
                ]
            (_, uploaded, size, seeders, leechers,) = tuple([
                column.contents[0]
                for column in result.find('dd').find_all('span')
            ])

            torrent['uploaded'] = self.parse_datetime((
                '{uploaded} ago'
            ).format(**locals()))
            torrent['size'] = self.parse_size(size)
            (torrent['seeders'], torrent['leechers'],) = (
                int(seeders.replace(',', '')),
                int(leechers.replace(',', '')),
            )

            yield torrent
