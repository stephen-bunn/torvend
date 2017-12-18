=====
Usage
=====

Using Torvend in your own applications is *really* simple and straightforward.
I've removed most of the complexity by provided a :class:`~torvend.client.TorvendClient` object which performs the torrent searching task optimally right out of the box.


.. _usage-basic-initialization:

Basic Initialization
''''''''''''''''''''
The most simple form of initializing a client can be done like this:

.. code-block:: python

   from torvend.client import TorvendClient

   my_client = TorvendClient()


.. note:: The only subpackage exposed by the :mod:`torvend` package is the command line package ``cli``.
   This means that you will have to specify the fully qualified name to import the :class:`~torvend.client.TorvendClient` object.

   .. code-block:: python

      # INCORRECT
      import torvend
      my_client = torvend.client.TorvendClient()

      # CORRECT
      import torvend.client
      my_client = torvend.client.TorvendClient()

      # CORRECT
      from torvend.client import TorvendClient
      my_client = TorvendClient()


.. _usage-advanced-initialization:

Advanced Initialization
'''''''''''''''''''''''
There are serveral available options that can be specified when initializing a new :class:`~torvend.client.TorvendClient`.


.. _usage-specifying-spiders:

Specifying Spiders
~~~~~~~~~~~~~~~~~~
The most useful of these options are the ``allowed`` and ``ignored`` lists.
These lists allow you to specify the spiders to utilize or to not utilize when performing the search.

For example, if I wanted to only search torrents using the only the spiders :class:`~torvend.spiders.thepiratebay.ThePirateBaySpider` and :class:`~torvend.spiders.torrentz2.Torrentz2Spider`, I could include this class in the ``allowed`` list when initializing the client.

.. code-block:: python

   from torvend.spiders import (ThePirateBaySpider, Torrentz2Spider)

   my_client = TorvendClient(allowed=[ThePirateBaySpider, Torrentz2Spider])


However, if I only wanted to **not** receive torrents from :class:`~torvend.spiders.limetorrents.LimeTorrentsSpider`, I could specify that spider in the ``ignored`` list.

.. code-block:: python

   from torvend.spiders import (LimeTorrentsSpider,)

   my_client = TorvendClient(ignored=[LimeTorrentsSpider])


.. important:: The use of both the ``allowed`` and ``ignored`` fields in the same initialization is not permitted.
   This is because it makes no sense to allow **only** some spiders to run and ignore others (**the allowed list already ignores them**).


.. _usage-customize-scrapy:

Customize Scrapy
~~~~~~~~~~~~~~~~
You can also customize the `scrapy <https://scrapy.org>`_ settings by passing in the ``settings`` dictionary with updated settings.
For example, if I wanted to use a different name for the scrapy bot, I could pass in my new bot name in the settings dictionary.

.. code-block:: python

   my_client = TorvendClient(settings={'BOT_NAME': 'my-bot'})


If you need a reference for available scrapy settings, `click here <https://doc.scrapy.org/en/latest/topics/settings.html#built-in-settings-reference>`_.


.. _usage-verbose-logging:

Verbose Logging
~~~~~~~~~~~~~~~
You can enable verbose logging by simply passing the ``verbose`` flag to the :class:`~torvend.client.TorvendClient` initialization.

.. code-block:: python

   my_client = TorvendClient(verbose=True)


.. _usage-starting-spiders:

Starting Spiders
''''''''''''''''
You can start up the search process through the :class:`~torvend.client.TorvendClient` by starting the spiders.
Lucky for you, I've compressed the logic into the :func:`~torvend.client.TorvendClient.search` method.

Because this web-scraper is asynchronous, you need to not only supply a query to the search method, but also a callback function.


.. code-block:: python

   def torrent_callback(item, **kwargs):
      print(('received torrent {item}').format(item=item))


   my_client = TorvendClient()
   my_client.search('my query', torrent_callback)


.. important:: This callback **must** specify the positional argument ``item`` and the ``**kwargs`` dictionary.
   Note that **the positional argument must be named "item"** due to how scrapy handles it's signals.
