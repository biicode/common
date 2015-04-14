"""Module with biicode custom decorators."""
from biicode.common.settings.osinfo import OSInfo


def os_constraint(os_name):
    """Wraps a method checking if client runs in give operating system.
       Class should have WorkspacePaths and UserIO as attributes."""
    def decorator(func):
        def _os_constraint(self, *args, **kargs):
            os_info = OSInfo.capture()

            if os_info.family == os_name:
                func(self, *args, **kargs)
            else:
                self.user_io.out.error('You need to use a {} OS'.format(os_name))

        _os_constraint.__doc__ = func.__doc__
        return _os_constraint
    return decorator
