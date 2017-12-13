===============
Torvend Package
===============

This is the base torvend package (*not including the command line utility*).
The packages that developers should typically interact with are ``client``, ``items``, and ``spiders``.
Other packages are mainly used internally and typically dont need to be modified.


.. automodule:: torvend
    :members:
    :undoc-members:
    :show-inheritance:


torvend\.client
---------------

.. automodule:: torvend.client
    :members:
    :undoc-members:
    :show-inheritance:


torvend\.items
--------------

.. automodule:: torvend.items
    :members:
    :undoc-members:
    :show-inheritance:


torvend\.spiders
----------------

Below are a list of currently included spiders that can be utilized by :class:`~torvend.client.TorvendClient`.
These spiders are just `scrapy <https://scrapy.org>`_ spiders built to yield as many torrent items as possible until a given results threshold is met.

.. important:: These spiders are very dependent on the responses made from search requests by the spider.
   This means that as a spider's targeted site updates their search method (or views), the spider will most likely need to be updated as well.


idope
'''''
.. automodule:: torvend.spiders.idope
    :members:
    :undoc-members:
    :show-inheritance:

thepiratebay
''''''''''''
.. automodule:: torvend.spiders.thepiratebay
    :members:
    :undoc-members:
    :show-inheritance:

torrentz2
'''''''''
.. automodule:: torvend.spiders.torrentz2
    :members:
    :undoc-members:
    :show-inheritance:

1337x
'''''
.. automodule:: torvend.spiders.onethreethreesevenx
    :members:
    :undoc-members:
    :show-inheritance:

limetorrents
''''''''''''
.. automodule:: torvend.spiders.limetorrents
    :members:
    :undoc-members:
    :show-inheritance:
