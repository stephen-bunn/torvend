#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import enum

import scrapy


class TorrentCategory(enum.Enum):
    """ A enumeration of generic torrent categorizations.
    """

    Unknown = 'unknown'
    Audio = 'audio'
    Video = 'video'
    Image = 'image'
    Application = 'application'
    Game = 'game'
    Book = 'book'
    Adult = 'adult'


class Torrent(scrapy.Item):
    """ A torrent item.

    :ivar spider: The spider name which discovered the torrent
    :ivar source: The source url of the torrent
    :ivar name: The name of the torrent
    :ivar size: The size in bytes of the torrent
    :ivar magnet: The magnet link of the torrent
    :ivar categories: A list of applicable ``TorrentCategory``
    :ivar seeders: The number of seeders
    :ivar leechers: The number of leechers
    :ivar uploaded: The datetime the torrent was uploaded
    :ivar uploader: The name of the uploader
    """

    def __repr__(self):
        """ Returns a string representation of an object instance.

        :returns: A string representation of an object instance
        :rtype: str
        """

        return (
            '<{self.__class__.__name__} [{self[categories][0]}] '
            '({self[spider]}) "{self[name]}">'
        ).format(**locals())

    spider = scrapy.Field()
    source = scrapy.Field()
    name = scrapy.Field()
    size = scrapy.Field(serializer=int)
    magnet = scrapy.Field()
    categories = scrapy.Field(serializer=lambda x: [_.value for _ in x])
    seeders = scrapy.Field(serializer=int)
    leechers = scrapy.Field(serializer=int)
    uploaded = scrapy.Field(serializer=str)
    uploader = scrapy.Field()
