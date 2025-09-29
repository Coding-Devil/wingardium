#  Copyright (c) 2022 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import logging
from logging.config import dictConfig

# noinspection PyUnresolvedReferences
import asgi_correlation_id  # noqa: F401
from uvicorn.config import LOGGING_CONFIG

__version__ = '1.0.0'

API_PREFIX = '/starship_ai'

# Set the logging config ASAP so later initialization doesn't create default stuff we don't want.
# We're altering the uvicorn logging config here as well as adding our own nwac logging config.
# We're using a json format since these will need to be programmatically parsed later.

DateFmt = "%Y-%m-%d %H:%M:%S %Z"
# The correlation_id is used via middleware for FastAPI and ensures that all log messages for
# a given request can be grouped together by a unique ID.
LOGGING_CONFIG['filters'] = {
    'correlation_id': {
        '()': 'asgi_correlation_id.CorrelationIdFilter',
        'uuid_length': 32,
    },
}

# Unless otherwise specified, all loggers will use this.
LOGGING_CONFIG['formatters']['default'] = {
    '()': 'uvicorn.logging.DefaultFormatter',
    'fmt': "{\"time\": \"%(asctime)s\", "
           "\"lvl\": \"%(levelname)s\", "
           "\"correlation_id\": \"%(correlation_id)s\", "
           "\"from\": \"%(name)s\", "
           "\"msg\": \"%(message)s\"}",
    'datefmt': DateFmt,
}
# Uvicorn's log format for requests
LOGGING_CONFIG['formatters']['access'] = {
    '()': 'uvicorn.logging.AccessFormatter',
    'fmt': "{\"time\": \"%(asctime)s\", "
           "\"lvl\": \"%(levelname)s\", "
           "\"correlation_id\": \"%(correlation_id)s\", "
           "\"from\": \"%(name)s\", "
           "\"src\": \"%(client_addr)s\", "
           "\"req\": \"%(request_line)s\", "
           "\"status\": \"%(status_code)s\"}",
    'datefmt': DateFmt,
}
# Our log format
LOGGING_CONFIG['formatters']['nwac'] = {
    'format': "{\"time\": \"%(asctime)s\", "
              "\"lvl\": \"%(levelname)s\", "
              "\"correlation_id\": \"%(correlation_id)s\", "
              "\"from\": \"%(name)s.%(module)s.%(funcName)s\", "
              "\"msg\": \"%(message)s\"}",
    'datefmt': DateFmt,
}
# Force all logs to use stdout and add the correlation ID filter to them.
LOGGING_CONFIG['handlers']['default']['stream'] = 'ext://sys.stdout'
LOGGING_CONFIG['handlers']['default']['filters'] = ['correlation_id']
LOGGING_CONFIG['handlers']['nwac'] = {'stream': 'ext://sys.stdout',
                                      'class': 'logging.StreamHandler',
                                      'formatter': 'nwac',
                                      'filters': ['correlation_id'],
                                      }
LOGGING_CONFIG['handlers']['access']['stream'] = 'ext://sys.stdout'
LOGGING_CONFIG['handlers']['access']['filters'] = ['correlation_id']

# Our logger and the uvicorn logger already emit directly - don't propagate from those or
# we'll get duplicate messages.  Everything else should propagate and will be picked up by
# the root logger (represented by '').
LOGGING_CONFIG['loggers']['nwac'] = {'handlers': ['nwac'],
                                     'level': 'INFO',
                                     'propagate': False,
                                     }
LOGGING_CONFIG['loggers']['uvicorn']['propagate'] = False
LOGGING_CONFIG['loggers'][''] = {'handlers': ['default'],
                                 }

dictConfig(LOGGING_CONFIG)

LOG = logging.getLogger('nwac')
