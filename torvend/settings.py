#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>


# NOTE: the name of the scrapy bot
BOT_NAME = 'torvend'

# NOTE: obey robots.txt rules
ROBOTSTXT_OBEY = True

# NOTE: Paths to scapy spider modules
SPIDER_MODULES = [
    'torvend.spiders',
]
# NOTE: Path where new spiders should be created
NEWSPIDER_MODULE = 'torvend.spiders'

# NOTE: crawl responsibly by identifying yourself on the user-agent
# USER_AGENT = (
#     '{BOT_NAME} (+http://www.github.com/stephen-bunn/torvend)'
# ).format(**locals())

# NOTE: configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# NOTE: configure a delay for requests for the same website (default: 0)
# DOWNLOAD_DELAY = 3

# NOTE: the download delay setting will honor only one of the following:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# NOTE: disable cookies (enabled by default)
# COOKIES_ENABLED = False

# NOTE: disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# NOTE: override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Accept': (
#         'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
#     ),
#     'Accept-Language': 'en',
# }

# NOTE: enable or disable spider middlewares
# SPIDER_MIDDLEWARES = {
#    'torvend.middlewares.MyCustomSpiderMiddleware': 543,
# }

# NOTE: enable or disable downloader middlewares
# DOWNLOADER_MIDDLEWARES = {
#    'torvend.middlewares.MyCustomDownloaderMiddleware': 543,
# }

# NOTE: enable or disable extensions
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# NOTE: configure item pipelines
# ITEM_PIPELINES = {
#    'torvend.pipelines.SomePipeline': 300,
# }

# NOTE: enable and configure the AutoThrottle extension (disabled by default)
# AUTOTHROTTLE_ENABLED = True
# NOTE: the initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# NOTE: the maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# NOTE: the average number of requests Scrapy should be sending in parallel
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# NOTE: enable showing throttling stats for every response received
# AUTOTHROTTLE_DEBUG = False

# NOTE: enable and configure HTTP caching (disabled by default)
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
