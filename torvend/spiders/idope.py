# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

from .. import (items,)
from ._common import (BaseSpider,)

import furl


class IDopeSpider(BaseSpider):
    """ The spider for idope.se.
    """

    name = 'idope'
    allowed_domains = [
        'idope.se',
    ]

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

        return 10

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

        return '/torrent-list/{query}/?p={page}'

    def parse(self, response):
        """ Required first level page parser.

        :param response: The response instance from ``start_requests``
        :type response: scrapy.Request
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

            torrent['source'] = furl.furl(response.url).set(
                path=result.find('a').attrs['href'],
                args={}
            ).url
            torrent['categories'] = [
                self._category_map.get(
                    result.find(
                        'div', {'class': 'resultdivbottoncategory'}
                    ).contents[0].strip().lower(),
                    items.TorrentCategory.Unknown
                )
            ]
            info_hash = result.find(
                'div', {'class': 'hideinfohash'}
            ).contents[0].strip()
            torrent['hash'] = info_hash.lower()
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
