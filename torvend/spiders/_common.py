#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import re
import abc
import math
import socket

from .. import (meta,)

import bs4
import furl
import scrapy
import requests


class BaseSpider(scrapy.Spider, meta.Loggable, abc.ABC):
    """ The base spider for all spiders.
    """

    def __init__(self, query=None, results=30, *args, **kwargs):
        """ Initializes a spider.

        :param str query: The query the spider should search for
        :param int results: The number of minimum results to yield (not exact)
        :param args: Any additional positional arguments
        :type args: list[....]
        :param kwargs: Any additional named arguments
        :type kwargs: dict[str,....]
        """

        super(BaseSpider, self).__init__(*args, **kwargs)
        (self.query, self.results,) = (query, results,)

    @property
    def active_domains(self):
        """ A list of active domains.

        :getter: Returns a list of active domains
        :setter: Does not allow setting
        :rtype: list[str]
        """

        if not hasattr(self, '_active_domains'):
            self._active_domains = []
            for domain in self.allowed_domains:
                try:
                    socket.gethostbyname(domain)
                    self._active_domains.append(domain)
                except (socket.gaierror,):
                    pass
        return self._active_domains

    @abc.abstractproperty
    def query_scheme(self):
        """ Required property for query scheme.

        :returns: The scheme the query needs
        :rtype: str
        """

        raise NotImplementedError()

    @abc.abstractproperty
    def query_path(self):
        """ Required property for the query path.

        :returns: The path the query needs
        :rtype: str
        """

        raise NotImplementedError()

    @abc.abstractproperty
    def paging_index(self):
        """ Required property for paging indexing.

        :returns: The starting index of pages
        :rtype: int
        """

        raise NotImplementedError()

    @abc.abstractproperty
    def paging_results(self):
        """ Required property for paging results.

        :returns: The number of results per queried page
        :rtype: int
        """

        raise NotImplementedError()

    def start_requests(self):
        """ The scrapy request starters.

        :returns: Yeilds requests for a sequence of pages
        :rtype: list[scrapy.Request]
        """

        for page_index in range(self.paging_index, math.ceil(
            (self.results / self.paging_results)
        ) + self.paging_index):
            yield scrapy.Request(
                self.get_url(self.query, page_index),
                callback=self.parse
            )

    def get_url(self, query, page, **kwargs):
        """ Gets the query url.

        :param str query: The query text
        :param int page: The result page index to query for
        :param kwargs: Any additional named arguments
        :type kwargs: dict[str,....]
        :returns: The property url for making a query
        :rtype: str
        """

        return furl.furl().set(
            scheme=self.query_scheme,
            host=self.active_domains[0]
        ).join(self.query_path.format(
            query=query, page=page
        )).url

    def get_source(self, url):
        """ Gets the source from a given url.

        :param str url: The url to retrieve the source from
        :raises ValueError:
            - when the response status code of the request is not 200
        :returns: The source of a given url
        :rtype: str
        """

        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise ValueError((
                "error requesting source of url '{url}', "
                "received status '{response.status_code}'"
            ).format(**locals()))
        return response.text

    def get_soup(self, content, parser='lxml'):
        """ Returns a BeautifulSoup instance of some content.

        :param str content: The source to use for creating a BeautifulSoup
        :param str parser: The HTML parser to use (default: lxml)
        :returns: A BeautifulSoup instance
        :rtype: bs4.BeautifulSoup
        """

        return bs4.BeautifulSoup(content, parser)

    def parse_infohash(self, magnet_link):
        """ Parses the infohash from a given magnet link.

        :param str magnet_link: The torrents magnet link
        :returns: Returns the infohash
        :rtype: str
        """

        if not hasattr(self, '_infohash_regex'):
            self._infohash_regex = re.compile(
                r'^magnet:\?(?:xt)=[a-z:]+:([a-zA-Z0-9]+)&?.*$'
            )
        return self._infohash_regex.match(magnet_link).groups()[0]

    def parse_datetime(self, text, formats=[]):
        """ Guesses a datetime from some given text.

        :param str text: The text to determine the datetime from
        :param formats: A list of potential datetime formats (default: [])
        :type formats: list[str]
        :returns: The best guessed datetime instance
        :rtype: datetime.datetime
        """

        # NOTE: local import to speed up module loading
        import dateparser

        return dateparser.parse(text, date_formats=formats)

    def parse_size(self, text):
        """ Parses a real byte size from some given text.

        :param str text: The text to determine real byte size from
        :returns: A real byte size
        :rtype: int
        """

        # NOTE: local import to speed up module loading
        import humanfriendly

        return humanfriendly.parse_size(text)

    @abc.abstractmethod
    def parse(self, request):
        """ Required first level page parser.

        :param request: The request instance from ``start_requests``
        :type request: scrapy.Request
        :returns: Yields torrent items
        :rtype: list[items.Torrent]
        """

        raise NotImplementedError()
