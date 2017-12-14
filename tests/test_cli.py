# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import re
import contextlib

import torvend.cli

import click.testing


@contextlib.contextmanager
def cli_manager(command, *args):
    """ A context manager for CLI invoking.
    """

    manager = None
    try:
        manager = click.testing.CliRunner()
        yield manager.invoke(command, args)
    finally:
        del manager


class TestCli(object):
    """ A collection of cli testcases.
    """

    def test_list(self):
        """ Test the list command output.
        """

        (name_regex, domains_regex,) = (
            re.compile(r'^[a-z0-9]+$'),
            re.compile((
                r'^\((?:(?:(?:www\.)?[a-zA-Z0-9]+\.[a-zA-Z]{2,}),?\s?)+\)$'
            )),
        )
        with cli_manager(
            torvend.cli,
            '--quiet', '--no-color', 'list'
        ) as test_invoke:
            assert test_invoke.exit_code == 0
            for spider_entry in test_invoke.output.split('\n')[:-1]:
                (spider_name, spider_domains,) = spider_entry.split(' ', 1)
                assert name_regex.match(spider_name) is not None
                assert domains_regex.match(spider_domains) is not None
