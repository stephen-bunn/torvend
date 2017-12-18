=======
Torvend
=======
A command line utility for searching for torrents across many popular sharing sites

|

.. image:: https://img.shields.io/pypi/v/torvend.svg
   :target: https://pypi.org/project/torvend/
   :alt: PyPi Status

.. image:: https://img.shields.io/pypi/pyversions/torvend.svg
   :target: https://pypi.org/project/torvend/
   :alt: Supported Versions

.. image:: https://img.shields.io/pypi/status/torvend.svg
   :target: https://pypi.org/project/torvend/
   :alt: Release Status

.. image:: https://img.shields.io/github/last-commit/stephen-bunn/torvend.svg
   :target: https://github.com/stephen-bunn/torvend
   :alt: Last Commit

.. image:: https://img.shields.io/github/license/stephen-bunn/torvend.svg
   :target: https://github.com/stephen-bunn/torvend/blob/master/LICENSE
   :alt: License

.. image:: https://readthedocs.org/projects/torvend/badge/?version=latest
   :target: http://torvend.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/stephen-bunn/torvend.svg?branch=master
   :target: https://travis-ci.org/stephen-bunn/torvend
   :alt: Build Status

.. image:: https://codecov.io/gh/stephen-bunn/torvend/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stephen-bunn/torvend
   :alt: Code Coverage

.. image:: https://requires.io/github/stephen-bunn/torvend/requirements.svg?branch=master
   :target: https://requires.io/github/stephen-bunn/torvend/requirements/?branch=master
   :alt: Requirements Status

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
   :target: https://saythanks.io/to/stephen-bunn
   :alt: Say Thanks

|


Command Line
------------

.. image:: docs/source/_static/usage.gif
   :align: center



Usage
-----

.. code-block:: python

   from torvend.client import (TorvendClient,)

   discovered_torrents = []

   def torrent_callback(item, **kwargs):
      discovered_torrents.append(item)


   client = TorvendClient()
   client.search('my query', torrent_callback)

   print(discovered_torrents)
