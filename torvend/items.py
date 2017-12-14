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
    """ An item that describes a torrent.

    .. note:: The attributes of these `scrapy <https://scrapy.org>`_ items can
        only be retrieved by indexing the object like a dictionary.
        The same is true for setting the attributes of the object.

        .. code-block:: python

            torrent_name = torrent_instance['name']
            torrent_instance['name'] = new_torrent_name


    :param str spider: The spider name which discovered the torrent
    :param str source: The source url of the torrent
    :param str name: The name of the torrent
    :param int size: The size in bytes of the torrent
    :param str hash: The infohash of the torrent
    :param str magnet:  The magnet link of the torrent
    :param categories: A list of applicable categories
    :type categories: list[torvend.items.TorrentCategory]
    :param int seeders: The number of seeder
    :param int leechers: The number of leechers
    :param datetime.datetime uploaded: The datetime to torrent was uploaded
    :param str uploader: The username of the uploader
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
    hash = scrapy.Field()
    magnet = scrapy.Field()
    # FIXME: find a better way to handle this than a lambda
    categories = scrapy.Field(serializer=lambda x: [_.value for _ in x])
    seeders = scrapy.Field(serializer=int)
    leechers = scrapy.Field(serializer=int)
    uploaded = scrapy.Field(serializer=str)
    uploader = scrapy.Field()
