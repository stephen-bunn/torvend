# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

from torvend.spiders import (OneThreeThreeSevenXSpider,)
from ._common import BaseSpiderTest


class TestOneThreeThreeSevenXSpider(BaseSpiderTest):

    @property
    def spider_class(self):
        return OneThreeThreeSevenXSpider

    @property
    def mock_query(self):
        return 'test'

    @property
    def mock_response(self):
        return '1337x.html'
