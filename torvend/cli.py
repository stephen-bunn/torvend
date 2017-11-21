#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import os
import sys
import inspect
import platform
import webbrowser
import subprocess
import contextlib

from . import (__version__, const,)

import click
import yaspin
import yaspin.spinners
import pyperclip
from colored import (fore, back, style,)

COLORED = {'fore': fore, 'back': back, 'style': style}
CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)


def _open_magnet(ctx, link):
    """ Opens a magnet link in the default application.

    :param click.Context ctx: The calling clicks current context
    :param str link: The magnet link to open
    :rtype: None
    """

    system = platform.system().lower()
    if system == 'darwin':
        webbrowser.open(link)
    elif system == 'linux':
        subprocess.Popen(['xdg-open', link]).wait()
    else:
        os.startfile(link)


def _build_spinner(ctx, text):
    """ Builds a spinner context manager.

    :param click.Context ctx: The calling clicks current context
    :param str text: The text to display in the spinner
    :returns: A spinner context manager
    """

    if ctx.obj.get('quiet', False):
        # NOTE: ExitStack is essentially a null context manager
        return contextlib.ExitStack()

    return yaspin.yaspin(
        spinner=getattr(
            yaspin.spinners.Spinners,
            ctx.params.get('spinner', 'dots12')
        ),
        text=text
    )


def _list_spiders(ctx):
    """ List available spiders.

    :param click.Context ctx: The calling clicks current context
    """

    with _build_spinner(ctx, (
        '{style.BOLD} getting {fore.MAGENTA}'
        'torvend{style.RESET}{style.BOLD} spiders '
        '{style.RESET} ...'
    ).format(**COLORED, **locals())):
        from . import (spiders,)

    for (_, spider_class,) in inspect.getmembers(
        spiders,
        predicate=inspect.isclass
    ):
        spider_name = spider_class.name.lower()
        domains = ', '.join(spider_class.allowed_domains)
        print((
            '{fore.CYAN}{style.BOLD}{spider_name}{style.RESET} ({domains})'
        ).format(**COLORED, **locals()))


def _build_client(ctx, allowed, ignored):
    """ Builds a client instance given context.

    :param click.Context ctx: The calling clicks current context
    :returns: A valid client instance
    :rtype: Client
    """

    def parse_spiders(spider_sequence, delimiter=','):
        return list(filter(None, [
            spider.strip().lower()
            for spider in spider_sequence.split(delimiter)
        ]))

    # NOTE: local import to speed up cli tool
    from . import (spiders,)
    from .client import (Client,)

    (allowed, ignored,) = (
        parse_spiders(allowed),
        parse_spiders(ignored),
    )
    (allowed_spiders, ignored_spiders,) = ([], [],)

    for (_, spider_class,) in inspect.getmembers(
        spiders,
        predicate=inspect.isclass
    ):
        spider_name = spider_class.name.lower()

        if spider_name in allowed:
            allowed_spiders.append(spider_class)
        if spider_name in ignored:
            ignored_spiders.append(spider_class)

    if len(allowed_spiders) > 0 and len(ignored_spiders) > 0:
        print((
            '{fore.RED}usage of both {style.BOLD}allowed{style.RESET}'
            '{fore.RED} and {style.BOLD}ignored{style.RESET}{fore.RED} '
            'is not permitted, defaulting to {style.BOLD}allowed{style.RESET}'
        ).format(**COLORED))
        ignored_spiders = []

    return Client(
        allowed=allowed_spiders,
        ignored=ignored_spiders,
        verbose=ctx.obj.get('verbose', False)
    )


def _sort_torrents(ctx, torrent_list, sort_type):
    """ Sorts torrents by a specific sort pattern.

    :param click.Context ctx: The calling clicks current context
    :param torrent_list: A list of torrent items to sort
    :type torrent_list: List[torvend.items.Torrent]
    :param str sort_type: The type of sort to perform
    :returns: A sorted torrent item list
    :rtype: List[torvend.items.Torrent]
    """

    if sort_type == 'seeders':
        return sorted(torrent_list, key=lambda t: t['seeders'], reverse=True)


def _search_torrents(ctx, client, query):
    """ Start the torrent search with a given client.

    :param click.Context ctx: The calling clicks current context
    :param Client client: The client to use for searching
    :param str query: The query to search for
    :returns: Yields torrent items as discovered
    :rtype: List[torvend.items.Torrent]
    """

    result_count = ctx.params.get('results', 25)
    discovered = set()

    def _torrent_callback(item, **kwargs):
        discovered.add(item)

    with _build_spinner(ctx, (
        '{style.BOLD} searching for '
        '{fore.GREEN}{query}{style.RESET} ...'
    ).format(**COLORED, **locals())):
        client.search(query, _torrent_callback, results=result_count)

    for torrent in _sort_torrents(
        ctx, list(discovered),
        ctx.params.get('sort', 'seeders')
    ):
        yield torrent


def _render_torrents(ctx, torrent_iterator, format):
    """ Handles rendering torrents given a format.

    :param click.Context ctx: The calling clicks current context
    :param torrent_iterator: The iterator of torrents
    :type torrent_iterator: list[torvend.items.Torrent]
    :param str format: The string format to render torrents as
    """

    show_duplicates = ctx.params.get('show_duplicates', False)
    result_count = ctx.params.get('results', 25)

    (seen, count,) = (set(), 0,)
    while count < result_count:
        try:
            torrent = next(torrent_iterator)
            if torrent['hash'] not in seen:
                rendered = format.format(**COLORED, **torrent)
                if not show_duplicates:
                    seen.add(torrent['hash'])

                yield (torrent, rendered,)
                count += 1
        except StopIteration:
            break

    if count <= 0:
        print((
            '{style.BOLD}{fore.WHITE}sorry, no results{style.RESET}'
        ).format(**COLORED))
        return


def _select_torrent(ctx, render_iterator):
    """ Prompts the user for selection of a rendered torrent.

    :param click.Context ctx: The calling clicks current context
    :param render_iterator: An iterator which yields a torrent, str pair
    :type render_iterator: List[torvend.items.Torrent, str]
    """

    result_count = ctx.params.get('results', 25)
    result_spacing = len(str(result_count))
    displayed = []

    for (idx, (torrent, rendered,)) in enumerate(render_iterator):
        print((
            '{idx:>{result_spacing}} ➜ '
        ).format(**locals()) + rendered)
        displayed.append(torrent)

    while True:
        try:
            selected_idx = input((
                '{fore.WHITE}{style.BOLD}[select torrent]:{style.RESET} '
            ).format(**COLORED)).strip()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
        if selected_idx.isdigit():
            selected_idx = int(selected_idx)
            if selected_idx >= 0 and selected_idx < result_count:
                return displayed[selected_idx]
            else:
                print((
                    '{fore.RED}{style.BOLD}{selected_idx}{style.RESET}'
                    '{fore.RED} is out of range{style.RESET}'
                ).format(**COLORED, **locals()))
        else:
            print((
                '{fore.RED}{style.BOLD}{selected_idx}{style.RESET}'
                '{fore.RED} is not a valid digit{style.RESET}'
            ).format(**COLORED, **locals()))


def _validate_spinner(ctx, param, value):
    """ Callback handler for ``yaspin`` spinner names.

    :param click.Context ctx: The calling clicks current context
    :param str param: The parameter name
    :param str value: The given value of the parameter
    :raises click.BadParameter:
        - when the spinner value is not a valid spinner name
    :returns: The spinner value
    :rtype: str
    """

    spinner_names = list(yaspin.spinners.Spinners._asdict().keys())
    if value not in spinner_names:
        raise click.BadParameter((
            "spinner '{value}' does not exist, {spinner_names}"
        ).format(**locals()))
    return value


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option(
    '--color/--no-color',
    default=True, help='Enable pretty colors', show_default=True
)
@click.option(
    '-q', '--quiet',
    is_flag=True, default=False, help='Disable spinners'
)
@click.option(
    '-v', '--verbose',
    is_flag=True, default=False, help='Enable verbose logging'
)
@click.version_option(
    prog_name=__version__.__name__,
    version=__version__.__version__
)
@click.pass_context
def cli(
    ctx,
    color=None, quiet=None, verbose=None
):
    """\b
    ▄▄▄▄▄      ▄▄▄   ▌ ▐·▄▄▄ . ▐ ▄ ·▄▄▄▄
    •██  ▪     ▀▄ █·▪█·█▌▀▄.▀·•█▌▐███▪ ██
     ▐█.▪ ▄█▀▄ ▐▀▀▄ ▐█▐█•▐▀▀▪▄▐█▐▐▌▐█· ▐█▌
     ▐█▌·▐█▌.▐▌▐█•█▌ ███ ▐█▄▄▌██▐█▌██. ██
     ▀▀▀  ▀█▄▀▪.▀  ▀. ▀   ▀▀▀ ▀▀ █▪▀▀▀▀▀•

    A set of torrent vendor scrapers (by Stephen Bunn).
    """

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_usage())

    if not color:
        # handle nulling of color values in colored instance (maybe dangerous)
        for (colored_type, instance,) in COLORED.items():
            for color_name in instance.__dict__.keys():
                if color_name.isupper():
                    setattr(instance, color_name, '')

    ctx.obj = ctx.params


@click.command(
    'list',
    short_help='Lists available spiders',
    context_settings={
        'ignore_unknown_options': True
    }
)
@click.pass_context
def cli_list(ctx):
    """ List available spiders.

    \b
    torvend list
    """

    _list_spiders(ctx)


@click.command(
    'search',
    short_help='Searches for torrents',
    context_settings={
        'ignore_unknown_options': True
    }
)
@click.argument('query')
@click.option(
    '--allowed',
    type=str, default='',
    help='List of allowed spiders (no spaces; delimiter ",")'
)
@click.option(
    '--ignored',
    type=str, default='',
    help='List of ignored spiders (no spaces; delimiter ",")'
)
@click.option(
    '--spinner',
    type=str, default='dots12', help='Customize spinner type',
    show_default=True, callback=_validate_spinner
)
@click.option(
    '--fancy',
    is_flag=True, default=False, help='Display fancy title'
)
@click.option(
    '--copy',
    is_flag=True, default=False,
    help='Copies the selected torrent to clipboard', show_default=True
)
@click.option(
    '--duplicates',
    is_flag=True, default=False,
    help='Allow duplicate torrents to be displayed',
    show_default=True
)
@click.option(
    '-r', '--results',
    type=int, default=25, help='Number results to render'
)
@click.option(
    '-f', '--format',
    type=str, default=(
        '{fore.BLUE}{hash}{style.RESET}{fore.CYAN}{style.BOLD}@{spider}'
        '{style.RESET} {fore.WHITE}{style.BOLD}{name}{style.RESET} '
        '({style.BOLD}{fore.GREEN}{seeders}{style.RESET}, '
        '{fore.RED}{leechers}{style.RESET})'
    ),
    help='Customize torrent render'
)
@click.option(
    '-j', '--json', 'to_json',
    is_flag=True, default=False,
    help='Write results to stdout as json (disable selection)'
)
@click.option(
    '-s', '--sort',
    type=click.Choice(['seeders']), default='seeders',
    help='Customize torrent sorting', show_default=True
)
@click.option(
    '-b', '--select-best',
    is_flag=True, default=False,
    help='Automatically write best magnet to stdout',
)
@click.pass_context
def cli_search(
    ctx,
    allowed=None, ignored=None, spinner=None, fancy=None,
    copy=None, duplicates=None,
    results=None, format=None, to_json=None, sort=None,
    select_best=None,
    query=None
):
    """ Search for torrents:

    \b
    torvend search "query"
    """

    if fancy:
        click.echo(__version__.__fancy__)
    try:
        # build search client
        client = None
        with _build_spinner(ctx, (
            '{style.BOLD} building {fore.MAGENTA}'
            'torvend{style.RESET}{style.BOLD} client '
            '{style.RESET} ...'
        ).format(**COLORED, **locals())):
            client = _build_client(ctx, allowed, ignored)

        # render discovered torrents (lazy)
        render_iterator = _render_torrents(
            ctx,
            _search_torrents(ctx, client, query),
            format,
        )

        if select_best:
            sys.stdout.write(next(render_iterator)[0]['magnet'])
        elif to_json:
            # NOTE: local import to speed up cli response
            from scrapy.exporters import JsonItemExporter
            torrent_exporter = JsonItemExporter(
                sys.stdout.buffer,
                encoding='utf-8'
            )
            for (torrent, _,) in render_iterator:
                torrent_exporter.export_item(torrent)
        else:
            selected_torrent = _select_torrent(ctx, render_iterator)
            if copy:
                print((
                    'copying magnet for '
                    '{fore.GREEN}{style.BOLD}{selected_torrent[name]}'
                    '{style.RESET} from {fore.CYAN}{style.BOLD}'
                    '{selected_torrent[spider]}{style.RESET} '
                    'to clipboard ... '
                ).format(**COLORED, **locals()), end='')
                pyperclip.copy(selected_torrent['magnet'])
                print((
                    '{fore.GREEN}{style.BOLD}✔{style.RESET}'
                ).format(**COLORED))
            else:
                print((
                    'opening magnet for '
                    '{fore.GREEN}{style.BOLD}{selected_torrent[name]}'
                    '{style.RESET} from {fore.CYAN}{style.BOLD}'
                    '{selected_torrent[spider]}{style.RESET} ... '
                ).format(**COLORED, **locals()), end='')
                _open_magnet(ctx, selected_torrent['magnet'])
                print((
                    '{fore.GREEN}{style.BOLD}✔{style.RESET}'
                ).format(**COLORED))

    except (KeyboardInterrupt, EOFError):
        pass
    except Exception as exc:
        print((
            '{fore.RED}{style.BOLD}ERROR{style.RESET}{fore.RED}: '
            'view log ({const.log_dir}{sep}{const.module_name}.log)'
            '{style.RESET}'
        ).format(sep=os.sep, const=const, **COLORED,))
        sys.exit(0)


# add click commands to cli group
cli.add_command(cli_search)
cli.add_command(cli_list)


if __name__ == '__main__':
    cli()
