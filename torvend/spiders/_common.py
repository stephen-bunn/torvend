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

    def __init__(self, query=None, results=30, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        (self.query, self.results,) = (query, results,)

    @abc.abstractproperty
    def paging_results(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def query_url(self):
        raise NotImplementedError()

    def start_requests(self):
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
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise ValueError((
                "error requesting source of url '{url}', "
                "received status '{response.status_code}'"
            ).format(**locals()))
        return response.text

    def get_soup(self, url, parser='lxml', is_content=False):
        return bs4.BeautifulSoup(
            (self.get_source(url) if not is_content else url),
            parser
        )

    def parse_datetime(self, text, formats=[]):
        return dateparser.parse(text, date_formats=formats)

    def parse_size(self, text):
        return humanfriendly.parse_size(text)

    @abc.abstractmethod
    def parse(self, request):
        raise NotImplementedError()
