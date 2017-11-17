===============
Getting Started
===============

This module is my attempt at creating a utility for searching multiple web-based torrent trackers quickly.
Essentially it allows the user to specify a search query and yields standardized torrent objects from multiple different web-based torrent trackers asynchronously.

This is accomplished by leveraging the `scrapy <https://scrapy.org>`_ package to perform advanced web-scraping in parallel.

.. _getting_started-installation:

Installation
------------
Since Torvend is not yet on `PyPi <https://pypi.org/>`_, the only way to install it is by running the following commands:

.. code-block:: bash

   pip install --user pipenv --upgrade
   git clone https://github.com/stephen-bunn/torvend.git
   cd torvend
   pipenv install --three
   pipenv run setup.py sdist
   pip install dist/torvend-0.0.0.tar.gz # version number may be different


This will install the Torvend package as well as give you access to the embeded command line utility!


.. _getting_started-command-line:

Command Line
------------
Using Torvend from the command line is quick and easy.
The command line tool should be able to be accessed by simply executing ``torvend`` in a shell.

*If for some reason your shell can't find torvend, make sure that your Python scripts directory is on your $PATH.*


.. image:: ./_static/usage.gif
   :align: center


.. code-block:: text

   $ torvend
   Usage: torvend [OPTIONS] COMMAND [ARGS]...

   $ torvend --help
   Usage: torvend [OPTIONS] COMMAND [ARGS]...

     ▄▄▄▄▄      ▄▄▄   ▌ ▐·▄▄▄ . ▐ ▄ ·▄▄▄▄
     •██  ▪     ▀▄ █·▪█·█▌▀▄.▀·•█▌▐███▪ ██
      ▐█.▪ ▄█▀▄ ▐▀▀▄ ▐█▐█•▐▀▀▪▄▐█▐▐▌▐█· ▐█▌
      ▐█▌·▐█▌.▐▌▐█•█▌ ███ ▐█▄▄▌██▐█▌██. ██
      ▀▀▀  ▀█▄▀▪.▀  ▀. ▀   ▀▀▀ ▀▀ █▪▀▀▀▀▀•

     A set of torrent vendor scrapers (by Stephen Bunn).

   Options:
     --no-color     Disable pretty colors
     -q, --quiet    Disable spinners
     -v, --verbose  Enable verbose logging
     --version      Show the version and exit.
     -h, --help     Show this message and exit.

   Commands:
     list    Lists available spiders
     search  Searches for torrents


You can also checkout the :doc:`./command-line` reference documentation.


.. _getting_started-listing-available-spiders:

Listing Spiders
'''''''''''''''
You can list the available spiders by executing the ``list`` command.
This will iteratively output a spiders name followed by the supported domains of that spider.

.. code-block:: text

   $ torvend list
   thepiratebay (thepiratebay.org, thepiratebay.se)
   ...


These spider names are the names you can use in the ``search`` command to allow or ignore certain spiders.


.. _getting_started-searching-for-torrents:

Searching for Torrents
''''''''''''''''''''''
You can search for torrents using the spiders through the ``search`` command.
The most simple method of searching for torrents is to simply specify a query to the command.

This will first search and display several torrents (sorted by most seeders) and prompt you to select which torrent's magnet link you want copy.

.. code-block:: text

   $ torvend search "my query"
    0 ➜ 1234123412341234123412341234@thepiratebay My Query Torrent (1234, 1)
   ...
   [select torrent]: 0
   copying magnet for My Query Torrent to clipboard ... ✔


This will copy the discovered magnet link to your clipboard, ready to paste into your preferred client.

If instead you want to pipe the magnet of the highest seeded torrent to ``stdout``, you can run this:

.. code-block:: text

   $ torvend search -b "my query"
   magnet:xtn...


This is useful for piping magnet links into other command line applications.
For example, imagine you want to stream a *public domain* video to your desktop.
This can be done using `webtorrent <https://github.com/webtorrent/webtorrent>`_ and `mpv <https://mpv.io>`_ by running this:

.. code-block:: text

   $ torvend -q search -b "a video" | webtorrent --mpv
   ...


.. _getting_started-customization:

Customization
~~~~~~~~~~~~~
You can refine your torrent search by using the ``--allowed`` and ``--ignored`` options accepted by the ``search`` command.
These options allow you to specify a list of spiders (*delimited by commas*) to either utilize or not utilize.

.. code-block:: text

   $ torvend search --allowed thepiratebay,1337x "my query"
   ...
   $ torvend search --ignored limetorrents "my query"
   ...


.. note:: Using both the ``--allowed`` and ``--ignored`` flags in the same command is **not** permitted.
   This is because it doesn't make any sense to allow a certain subset of spiders to execute and ignore the others (*because the allowed subset implicitly ensures this*).

---

You can also refine the number of torrent suggestions displayed to you by using the ``--results`` option.
This will limit you to a maximum number of torrent suggestions amoung all of the torrents scraped by the spiders.

.. code-block:: text

   $ torvend search --results 10 "my query"
   ... <=10 results ...


---

The format results are displayed to you can also be customized by using the ``--format`` option.
This option takes a string containing format parameters for the :class:`~torvend.items.Torrent` item fields.

For example, if I wanted to only display the name, seeders, and leechers of discovered torrents, I would run this:

.. code-block:: text

   $ torvend search --format "{name} ({seeders}, {leechers})" "my query"
    0 ➜ My Query Torrent (1234, 1)
   ...


You can also customize the color of specific fields by using the ``fore``, ``back``, and ``style`` objects in your format.

.. code-block:: text

   $ torvend search --format "{style.BOLD}{name}{style.RESET} ({fore.GREEN}{seeders}{style.RESET}, {leechers})" "my query"
    0 ➜ My Query Torrent (1234, 1)
   ...


For more information on what colors and styles are available `click here <https://github.com/dslackw/colored>`__.
