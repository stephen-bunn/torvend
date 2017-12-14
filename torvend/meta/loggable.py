# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

from .. import (const,)


class Loggable(object):
    """ A metaclass which allows subclasses to utlize the ``log`` property.
    """

    @property
    def log(self):
        """ A scoped logger instance.

        :getter: Returns a scoped logger instance
        :setter: Does not allow setting
        :rtype: logging.Logger
        """

        if not hasattr(self, '_log'):
            self._log = const.base_logger.get_logger(self.__class__.__name__)
        return self._log
