# This file configures Gunicorn's logging to be silent.
# Our custom Loguru setup in main.py will handle all logging.

import logging

class StubbedGunicornLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        self.propagate = False
        super().__init__(*args, **kwargs)

    def info(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass

    def critical(self, *args, **kwargs):
        pass

logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': True, # Disable root loggers
    'loggers': {
        'gunicorn.error': {
            'level': 'CRITICAL',
            'handlers': [],
            'propagate': False,
        },
        'gunicorn.access': {
            'level': 'CRITICAL',
            'handlers': [],
            'propagate': False,
        }
    }
}
