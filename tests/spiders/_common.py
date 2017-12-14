# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import os
import abc
import contextlib

import scrapy.http


class BaseSpiderTest(abc.ABC):

    @property
    def response_dir(self):
        if not hasattr(self, '_response_dir'):
            self._response_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'responses'
            )
        return self._response_dir

    @abc.abstractproperty
    def spider_class(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def mock_query(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def mock_response(self):
        raise NotImplementedError()

    @contextlib.contextmanager
    def spider_manager(self):
        manager = None
        try:
            manager = self.spider_class()
            yield manager
        finally:
            del manager

    def get_response(self):
        response_path = os.path.join(self.response_dir, self.mock_response)
        if not os.path.isfile(response_path):
            raise FileNotFoundError((
                "response '{response_path}' not found"
            ).format(**locals()))
        with self.spider_manager() as spider:
            request_url = spider.get_url(
                self.mock_query,
                spider.paging_index
            )
            with open(response_path, 'r') as fp:
                return scrapy.http.TextResponse(
                    url=request_url,
                    request=scrapy.http.Request(url=request_url),
                    body=fp.read(),
                    encoding='utf-8'
                )

    def test_name(self):
        assert hasattr(self.spider_class, 'name')
        assert isinstance(self.spider_class.name, str)
        assert len(self.spider_class.name) > 0

    def test_allowed_domains(self):
        assert hasattr(self.spider_class, 'allowed_domains')
        assert isinstance(self.spider_class.allowed_domains, list)
        assert len(self.spider_class.allowed_domains) > 0
        assert all(
            isinstance(entry, str)
            for entry in self.spider_class.allowed_domains
        )

    def test_paging_index(self):
        with self.spider_manager() as test_spider:
            assert hasattr(test_spider, 'paging_index')
            assert isinstance(test_spider.paging_index, int)

    def test_paging_results(self):
        with self.spider_manager() as test_spider:
            assert hasattr(test_spider, 'paging_results')
            assert isinstance(test_spider.paging_results, int)
            assert test_spider.paging_results > 0

    def test_query_scheme(self):
        with self.spider_manager() as test_spider:
            assert hasattr(test_spider, 'query_scheme')
            assert isinstance(test_spider.query_scheme, str)
            assert test_spider.query_scheme.lower() in ('http', 'https',)

    def test_query_path(self):
        with self.spider_manager() as test_spider:
            assert hasattr(test_spider, 'query_path')
            assert isinstance(test_spider.query_path, str)
            assert '{query}' in test_spider.query_path
            assert '{page}' in test_spider.query_path
