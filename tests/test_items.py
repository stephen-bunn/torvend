# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import contextlib

from torvend.items import (TorrentCategory, Torrent,)

import pytest


@contextlib.contextmanager
def torrent_manager(*args, **kwargs):
    """ A context manager for torrent initialization.
    """

    torrent = Torrent(*args, **kwargs)
    try:
        yield torrent
    finally:
        del torrent


class TestItems(object):
    """ A collection of item testcases.
    """

    def test_repr(self):
        """ Tests ``__repr__`` method.
        """

        with pytest.raises(KeyError):
            with torrent_manager() as test_torrent:
                test_torrent.__repr__()

        with torrent_manager(
            categories=[TorrentCategory.Unknown],
            name='Test Torrent',
            spider='tests'
        ) as test_torrent:
            assert isinstance(test_torrent.__repr__(), str)
