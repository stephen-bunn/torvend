#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import sys
import inspect

from . import (__version__,)

import click
import yaspin
import yaspin.spinners
import pyperclip
from colored import (fore, back, style,)

COLORED = {'fore': fore, 'back': back, 'style': style}
CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)


def _list_spiders(ctx):
    """ List available spiders.

    :param click.Context ctx: The calling clicks current context
    """

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
        verbose=ctx.parent.params.get('verbose', False)
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

    discovered = set()

    def _torrent_callback(item, **kwargs):
        discovered.add(item)

    if not ctx.parent.params.get('quiet', False):
        with yaspin.yaspin(
            spinner=getattr(
                yaspin.spinners.Spinners,
                ctx.params.get('spinner', 'dots12')
            ),
            text=(
                '{style.BOLD} searching for '
                '{fore.GREEN}{query}{style.RESET} ...'
            ).format(**COLORED, **locals())
        ):
            client.search(query, _torrent_callback)
    else:
        client.search(query, _torrent_callback)

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

    enable_duplicates = ctx.params.get('show_duplicates', False)
    enable_selection = not ctx.params.get('select_best', False)
    result_count = ctx.params.get('results', 25)
    result_spacing = len(str(result_count))

    (displayed, seen, count,) = ([], set(), 0,)
    while count < result_count:
        try:
            torrent = next(torrent_iterator)
            if torrent['hash'] not in seen:
                rendered = format.format(**COLORED, **torrent)
                if enable_selection:
                    rendered = (
                        ('{count:>{result_spacing}} ➜ ').format(**locals()) +
                        rendered
                    )
                if not enable_duplicates:
                    seen.add(torrent['hash'])

                if enable_selection:
                    print(rendered)
                count += 1
                displayed.append(torrent)
        except StopIteration:
            break

    if len(displayed) <= 0:
        print((
            '{style.BOLD}{fore.WHITE}no results{style.RESET}'
        ).format(**COLORED))
        return

    if enable_selection:
        try:
            while True:
                selected_idx = input((
                    '{fore.WHITE}{style.BOLD}[select torrent]:{style.RESET} '
                ).format(**COLORED)).strip()
                if selected_idx.isdigit():
                    selected_idx = int(selected_idx)
                    if selected_idx >= 0 and selected_idx < result_count:
                        selected_torrent = displayed[selected_idx]
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
                        break
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
        except (KeyboardInterrupt, EOFError):
            pass
    else:
        sys.stdout.write(displayed[0]['magnet'])


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
    '--no-color',
    is_flag=True, default=False, help='Disable pretty colors'
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
    no_color=None, quiet=None, verbose=None
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

    if no_color:
        # handle nulling of color values in colored instance (maybe dangerous)
        for (colored_type, instance,) in COLORED.items():
            for color_name in instance.__dict__.keys():
                if color_name.isupper():
                    setattr(instance, color_name, '')


@click.command('list', short_help='Lists available spiders')
@click.pass_context
def cli_list(ctx):
    """ List available spiders.

    \b
    torvend list
    """

    _list_spiders(ctx)


@click.command('search', short_help='Searches torrents')
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
    '--show-duplicates',
    is_flag=True, default=False,
    help='Allow duplicate torrents to be displayed'
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
    help='customize torrent render'
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
    allowed=None, ignored=None, spinner=None, fancy=None, show_duplicates=None,
    results=None, format=None, sort=None,
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
        if not ctx.parent.params.get('quiet', False):
            with yaspin.yaspin(
                spinner=getattr(
                    yaspin.spinners.Spinners,
                    ctx.params.get('spinner', 'dots12')
                ),
                text=(
                    '{style.BOLD} building {fore.MAGENTA}'
                    'torvend{style.RESET}{style.BOLD} client '
                    '{style.RESET} ...'
                ).format(**COLORED, **locals())
            ):
                client = _build_client(ctx, allowed, ignored)
        else:
                client = _build_client(ctx, allowed, ignored)

        # render discovered torrents (lazy)
        _render_torrents(
            ctx,
            _search_torrents(ctx, client, query),
            format,
        )
    except (KeyboardInterrupt, EOFError):
        pass


cli.add_command(cli_search)
cli.add_command(cli_list)


if __name__ == '__main__':
    cli()
