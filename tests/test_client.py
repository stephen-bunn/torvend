#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import inspect
import contextlib

import torvend.spiders
from torvend.client import (Client,)

import pytest


@contextlib.contextmanager
def client_manager(*args, **kwargs):
    """ A context manager for client initialization.
    """

    client = Client(*args, **kwargs)
    try:
        yield client
    finally:
        del client


class TestClient(object):
    """ A colleciton of client testcases.
    """

    def test_default_initialization(self):
        """ Tests default initialization of client.
        """

        with client_manager() as test_client:

            assert isinstance(test_client.settings, dict)
            assert test_client.settings == {}

            assert isinstance(test_client.ignored, list)
            assert test_client.ignored == []

            assert isinstance(test_client.allowed, list)
            assert test_client.allowed == []

            assert isinstance(test_client.verbose, bool)
            assert test_client.verbose is False

    def test_settings_initialization(self):
        """ Tests settings initialization of client.
        """

        client_settings = {'BOT_NAME': 'test-bot'}

        with client_manager(settings=client_settings) as test_client:
            assert isinstance(test_client.settings, dict)
            assert test_client.settings == client_settings

        with pytest.raises(AssertionError):
            for invalid_value in (True, '', 0, [],):
                with client_manager(settings=invalid_value):
                    pass

    def test_ignored_initialization(self):
        """ Tests ignored initialization of client.
        """

        client_ignored = [torvend.spiders.ThePirateBaySpider]
        with client_manager(ignored=client_ignored) as test_client:

            assert isinstance(test_client.ignored, list)
            assert test_client.ignored == client_ignored

            test_client.allowed = client_ignored
            assert isinstance(test_client.ignored, list)
            assert test_client.ignored == []

        with pytest.raises(AssertionError):
            for invalid_value in (['ThePirateBaySpider'], True, '', 0, {},):
                with client_manager(ignored=invalid_value):
                    pass

    def test_allowed_initialization(self):
        """ Tests allowed initialization of client.
        """

        client_allowed = [torvend.spiders.ThePirateBaySpider]
        with client_manager(allowed=client_allowed) as test_client:

            assert isinstance(test_client.allowed, list)
            assert test_client.allowed == client_allowed

            test_client.ignored = client_allowed
            assert isinstance(test_client.allowed, list)
            assert test_client.allowed == []

        with pytest.raises(AssertionError):
            for invalid_value in (['ThePirateBaySpider'], True, '', 0, {},):
                with client_manager(allowed=invalid_value):
                    pass

    def test_verbose_initialization(self):
        """ Tests verbose initialization of client.
        """

        with client_manager(verbose=True) as test_client:

            assert isinstance(test_client.verbose, bool)
            assert test_client.verbose is True

            test_client.verbose = False
            assert test_client.verbose is False

        with pytest.raises(AssertionError):
            for invalid_value in ('', 0, [], {},):
                with client_manager(verbose=invalid_value):
                    pass

    def test_failing_initialization(self):
        """ Test failing initialization use cases.
        """

        client_allowed = [torvend.spiders.ThePirateBaySpider]
        client_ignored = [torvend.spiders.Torrentz2Spider]

        invalid_pairs = [
            (client_allowed, client_ignored,),
            ('ThePirateBaySpider', 'Torrentz2Spider',)
        ]
        with pytest.raises(ValueError):
            for (invalid_allowed, invalid_ignored,) in invalid_pairs:
                with client_manager(
                    allowed=invalid_allowed,
                    ignored=invalid_ignored
                ):
                    pass

    def test_get_spiders(self):
        """ Test the ``get_spiders`` method.
        """

        def is_spider(spider_class):
            """ Handles basic checks if a class is a valid spider class.
            """

            assert inspect.isclass(spider_class)
            assert issubclass(spider_class, torvend.spiders._common.BaseSpider)

        # test will all available spiders
        with client_manager() as test_client:
            assert inspect.isgeneratorfunction(test_client.get_spiders)
            for client_spider in test_client.get_spiders():
                is_spider(client_spider)

        # test with only allowed spiders
        client_allowed = [torvend.spiders.ThePirateBaySpider]
        with client_manager(allowed=client_allowed) as test_client:
            assert inspect.isgeneratorfunction(test_client.get_spiders)
            for client_spider in test_client.get_spiders():
                is_spider(client_spider)
                assert client_spider in client_allowed

        # test with only ignored spiders
        client_ignored = [torvend.spiders.ThePirateBaySpider]
        with client_manager(ignored=client_ignored) as test_client:
            assert inspect.isgeneratorfunction(test_client.get_spiders)
            for client_spider in test_client.get_spiders():
                is_spider(client_spider)
                assert client_spider not in client_ignored
