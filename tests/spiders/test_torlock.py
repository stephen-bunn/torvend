#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

from torvend.spiders import (TorlockSpider,)
from ._common import BaseSpiderTest


class TestTorlockSpider(BaseSpiderTest):

    @property
    def spider_class(self):
        return TorlockSpider

    @property
    def mock_query(self):
        return 'test'

    @property
    def mock_response(self):
        return 'torlock.html'
