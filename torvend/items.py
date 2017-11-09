#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import enum

import scrapy


class TorrentCategory(enum.Enum):

    Unknown = 'unknown'
    Audio = 'audio'
    Video = 'video'
    Image = 'image'
    Application = 'application'
    Game = 'game'
    Book = 'book'
    Porn = 'porn'


class Torrent(scrapy.Item):

    def __repr__(self):
        return (
            '<{self.__class__.__name__} [{self[categories][0]}] '
            '({self[source]}) "{self[name]}">'
        ).format(**locals())

    source = scrapy.Field()
    name = scrapy.Field()
    size = scrapy.Field(serializer=int)
    magnet = scrapy.Field()
    categories = scrapy.Field(serializer=lambda x: [_.value for _ in x])
    seeders = scrapy.Field(serializer=int)
    leechers = scrapy.Field(serializer=int)
    uploaded = scrapy.Field(serializer=str)
    uploader = scrapy.Field()
