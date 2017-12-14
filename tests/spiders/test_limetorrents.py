# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

from torvend.spiders import (LimeTorrentsSpider,)
from ._common import BaseSpiderTest


class TestLimetorrentsSpider(BaseSpiderTest):

    @property
    def spider_class(self):
        return LimeTorrentsSpider

    @property
    def mock_query(self):
        return 'test'

    @property
    def mock_response(self):
        return 'limetorrents.html'
