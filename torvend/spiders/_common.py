#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import abc
import math

from .. import (meta,)

import bs4
import scrapy
import requests
import dateparser
import humanfriendly


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

    @abc.abstractproperty
    def paging_results(self):
        """ Required property for paging results.

        :returns: The number of results per queried page
        :rtype: int
        """

        raise NotImplementedError()

    @abc.abstractproperty
    def query_url(self):
        """ Required property for query url template.

        .. note:: Usually requires the existence of the ``query`` and ``page``
            format parameters

        :returns: The query format string
        :rtype: str
        """

        raise NotImplementedError()

    def start_requests(self):
        """ The scrapy request starters.

        :returns: Yeilds requests for a sequence of pages
        :rtype: list[scrapy.Request]
        """

        for page_index in range(math.ceil(
            (self.results / self.paging_results)
        )):
            yield scrapy.Request(
                self.query_url.format(
                    query=self.query, page=page_index,
                    **locals()
                ),
                callback=self.parse
            )

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

    def parse_datetime(self, text, formats=[]):
        """ Guesses a datetime from some given text.

        :param str text: The text to determine the datetime from
        :param formats: A list of potential datetime formats (default: [])
        :type formats: list[str]
        :returns: The best guessed datetime instance
        :rtype: datetime.datetime
        """

        return dateparser.parse(text, date_formats=formats)

    def parse_size(self, text):
        """ Parses a real byte size from some given text.

        :param str text: The text to determine real byte size from
        :returns: A real byte size
        :rtype: int
        """

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
