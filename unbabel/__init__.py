

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': 'lineno=%(lineno)s funcname=%(funcName)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'unbabel-py': {
            'handlers': ['console'],
            'level':'DEBUG'
        },
    }
}

import logging
logging.basicConfig()
logger = logging.getLogger('unbabel-py.' + __name__)