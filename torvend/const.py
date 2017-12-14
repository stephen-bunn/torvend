# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import os
import sys
import logging
import tempfile
import traceback

from . import (__version__,)

import pygogo


class _const(object):
    """ Modules constant's namespace.
    """

    def __init__(self):
        """ Initializes module constants.
        """

        self.__bootstrap()

    @property
    def module_name(self):
        """ The name of the module.

        :getter: Returns the name of the module
        :setter: Does not allow setting
        :rtype: str
        """

        return __version__.__name__

    @property
    def module_version(self):
        """ The version of the module.

        :getter: Returns the version of the module
        :setter: Does not allow setting
        :rtype: str
        """

        return __version__.__version__

    @property
    def module_author(self):
        """ The author of the module.

        :getter: Returns the author of the module
        :setter: Does not allow setting
        :rtype: str
        """

        return __version__.__author__

    @property
    def base_dir(self):
        """ The base directory path of the module.

        :returns: The base directory path of the module
        :rtype: str
        """

        if not hasattr(self, '_base_dir'):
            self._base_dir = os.path.dirname(os.path.abspath(__file__))
        return self._base_dir

    @property
    def parent_dir(self):
        """ The parent directory path of the module.

        :returns: The parent directory path of the module
        :rtype: str
        """

        if not hasattr(self, '_parent_dir'):
            self._parent_dir = os.path.dirname(self.base_dir)
        return self._parent_dir

    @property
    def log_dir(self):
        """ The log directory path of the module.

        :returns: The log directory path of the module
        :rtype: str
        """

        if not hasattr(self, '_log_dir'):
            self._log_dir = os.path.join(
                tempfile.gettempdir(),
                self.module_name
            )
        return self._log_dir

    @property
    def base_logger(self):
        """ The base module logger vendor.

        :returns: The base module logger vendor
        :rtype: pygogo.Gogo
        """

        if not hasattr(self, '_base_logger'):
            self._base_logger = pygogo.Gogo(
                self.module_name,
                low_hdlr=logging.handlers.TimedRotatingFileHandler(
                    filename=os.path.join(
                        self.log_dir,
                        ('{self.module_name}.log').format(**locals())
                    ),
                    when='midnight'
                ),
                low_formatter=pygogo.formatters.structured_formatter,
                high_level='info',
                high_formatter=pygogo.formatters.fixed_formatter
            )
        return self._base_logger

    @property
    def log(self):
        """ The base module logger.

        :returns: The base module logger
        :rtype: logging.Logger
        """

        if not hasattr(self, '_log'):
            self._log = self.base_logger.logger
        return self._log

    @property
    def verbose(self):
        """ The verbose flag for base logging.

        :getter: Returns the verbose flag
        :setter: Sets the verbose flag for base loggin
        :rtype: bool
        """

        if not hasattr(self, '_verbose'):
            self._verbose = False
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        """ Sets verboseness of logging.

        :param bool verbose: True if verboseness is enabled
        :raises AssertionError:
            - when verbose is not a boolean value
        :rtype: None
        """

        assert isinstance(verbose, bool), (
            "verbose expects a boolean value, received {verbose}"
        ).format(**locals())
        if verbose:
            self.base_logger.levels['high'] = 'DEBUG'
        else:
            self.base_logger.levels['high'] = 'WARNING'
        self._verbose = verbose

    def __exception_handler(self, exception_type, value, exception_traceback):
        """ A custom exception handler for logging to base loggers.

        :param Exception exception_type: The raised exception type
        :param str value: The message of the exception
        :param traceback exception_traceback: The traceback of the exception
        :returns: None
        """

        self.log.exception((
            '{exception_type.__name__}: {value}'
        ).format(**locals()), extra={'exception': {
            'type': exception_type.__name__,
            'value': value,
            'traceback': traceback.format_exception(
                exception_type, value, exception_traceback
            )
        }})
        sys.__excepthook__(exception_type, value, exception_traceback)

    def __bootstrap(self):
        """ Bootstraps the module namespace.

        :returns: None
        """

        sys.excepthook = self.__exception_handler
        for required_dir in (self.log_dir,):
            if not os.path.isdir(required_dir):
                os.makedirs(required_dir)


sys.modules[__name__] = _const()
