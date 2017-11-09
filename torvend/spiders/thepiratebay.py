#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import re

from .. import (items,)
from ._common import (BaseSpider,)

import furl


class ThePirateBaySpider(BaseSpider):
    """ The spider for thepiratebay.org.
    """

    name = 'thepiratebay'
    allowed_domains = [
        'thepiratebay.org',
        'thepiratebay.se',
    ]

    _paging_results = 30
    _query_url = 'https://{self.allowed_domains[0]}/search/{query}/{page}'
    _category_map = {
        '100': items.TorrentCategory.Audio,
        '200': items.TorrentCategory.Video,
        '300': items.TorrentCategory.Application,
        '400': items.TorrentCategory.Game,
        '500': items.TorrentCategory.Adult,
        '503': items.TorrentCategory.Image,
        '600': items.TorrentCategory.Unknown,
        '601': items.TorrentCategory.Book,
        '603': items.TorrentCategory.Image,
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
        """ Required first level page parser.

        :param request: The request instance from ``start_requests``
        :type request: scrapy.Request
        :returns: Yields torrent items
        :rtype: list[items.Torrent]
        """

        soup = self.get_soup(response.text)
        try:
            results = soup\
                .find('table', {'id': 'searchResult'})\
                .find_all('tr')[1:]
        except AttributeError:
            return

        for result in results:
            torrent = items.Torrent(spider=self.name)
            torrent['categories'] = [
                self._category_map.get(
                    furl.furl(category.attrs['href']).path.segments[-1],
                    items.TorrentCategory.Unknown
                ) for category in result.find(
                    'td', {'class': 'vertTh'}
                ).find_all('a')
            ]
            torrent['magnet'] = result.find(
                'a', {'href': re.compile('^magnet\:.*')}
            )['href']
            torrent['hash'] = re.match(
                r'.*magnet:\?xt=urn:(?:btih)+:([a-zA-Z0-9]+).*',
                torrent['magnet']
            ).groups()[0]
            (torrent['seeders'], torrent['leechers'],) = tuple([
                int(column.contents[0])
                for column in result.find_all('td', {'align': 'right'})
            ])

            result_links = result.find('a', {'class': 'detLink'})
            if 'href' in result_links.attrs:
                source_url = furl.furl(self._query_url.format(
                    query=self.query, page=0,
                    **locals()
                ))
                source_url.path = result_links.attrs['href']
                source_url.args = {}
                torrent['source'] = source_url.url

            torrent['name'] = result_links.contents[0].strip()

            result_desc = result.find('font', {'class': 'detDesc'})
            (time_content, size_content,) = \
                result_desc.contents[0].split(',')[:2]
            torrent['uploaded'] = self.parse_datetime(
                time_content.split(' ')[-1],
                formats=[
                    '%m-%d %Y',
                    '%m-%d %H:%M',
                    '%H:%M',
                    'Y-day %H:%M'
                ]
            )
            torrent['size'] = self.parse_size(
                size_content.split(' ')[-1]
            )

            try:
                torrent['uploader'] = result_desc.find(
                    'a', {'href': re.compile('^/user/.*')}
                ).contents[0]
            except AttributeError:
                pass

            yield torrent
