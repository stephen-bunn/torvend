# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

from torvend.spiders import (IDopeSpider,)
from ._common import BaseSpiderTest


class TestIDopeSpider(BaseSpiderTest):

    @property
    def spider_class(self):
        return IDopeSpider

    @property
    def mock_query(self):
        return 'test'

    @property
    def mock_response(self):
        return 'idope.html'
