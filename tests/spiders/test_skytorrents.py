#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

from torvend.spiders import (SkyTorrentsSpider,)
from ._common import BaseSpiderTest


class TestSkytorrentsSpider(BaseSpiderTest):

    @property
    def spider_class(self):
        return SkyTorrentsSpider

    @property
    def mock_query(self):
        return 'test'

    @property
    def mock_response(self):
        return 'skytorrents.html'
