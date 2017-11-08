#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import bs4
import scrapy


class ThePirateBaySpider(scrapy.Spider):

    name = 'thepiratebay.org'
    allowed_domains = [
        'thepiratebay.org',
        'thepiratebay.se',
    ]
    query_url = '/search/{query}/{page}'

    def start_requests(self):
        pass

    def parse(self):
        pass
