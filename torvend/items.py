#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import enum

import scrapy


class TorrentCategory(enum.IntEnum):

    Unknown = 0x0
    Audio = 0x1
    Video = 0x2
    Image = 0x3
    Application = 0x4


class Torrent(scrapy.Item):

    source = scrapy.Field()
    name = scrapy.Field()
    size = scrapy.Field(serializer=int)
    magnet = scrapy.Field()
    categories = scrapy.Field()
    seeders = scrapy.Field(serializer=int)
    leechers = scrapy.Field(serializer=int)
    uploaded = scrapy.Field(serializer=str)
    uploader = scrapy.Field()
