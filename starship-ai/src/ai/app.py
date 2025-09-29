#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import logging
import os

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uvicorn.config import Config
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from ai import LOG, __version__
from ai.config import NWaCConfig
from ai.exceptions import InitializationError
from ai.models.v1.common import ParseError, ParseErrors
from ai.routes.v1 import PREFIX, ROUTE_LIST, TAG_METADATA


class App(object):
    """
    The App object encapsulates both the Fast API and Uvicorn components.

    Fast API is used as our REST framework.  Uvicorn is uses as our ASGI container.
    """

    def __init__(self, config: NWaCConfig = None):
        self.nwac_config = config

        self.app = None
        self.uvicorn_config = None

        self._has_been_set = False

    def override(self, args: dict):
        """
        Override settings based on command line args.

        NOTES:
            If this is called before update_from_file, then this method will do nothing.
            If the value of a given key is None, then that key will be skipped.  This allows
            you to pass in the result if vars(argparse.parse_args()) without having to prune
            any keys representing args that the user simply didn't supply.
        :param args: args to use for override.  Generally, this should be from something like
                     vars(argparse.parse_args())
        """
        if self.nwac_config is None or not self.nwac_config.initialized:
            LOG.warning("attempted to apply overrides before config was done")
        for i in args.keys():
            if hasattr(self.nwac_config, i):
                if args[i] is not None:
                    if getattr(self.nwac_config, i) != args[i]:
                        LOG.info(f"overriding {i} to {args[i]}")
                        setattr(self.nwac_config, i, args[i])
            else:
                LOG.info(f"did not apply override for {i} - not a config attribute")

    def init(self):
        """
        Initialize the Application.

        This will:
          * creates the Fast API application
          * configures the Fast API application
          * adds the routes (which are expected to have been defined via fastapi.APIRouter).
          * create the uvicorn config
          * put the Google credentials into the environment
          * create a custom exception handler for pydantic exceptions (so we can return something
            a bit more user friendly)
        :return:
        """
        if not self.nwac_config.initialized:
            LOG.error("cannot initialize app before configuring it")
            raise InitializationError

        if self.nwac_config.dev:
            self.nwac_config.log_level = 'DEBUG'

        self.nwac_config.tags = TAG_METADATA
        self.app = FastAPI(contact=self.nwac_config.contact_info,
                           description=self.nwac_config.description,
                           docs_url=f"{PREFIX}/docs",
                           license_info=self.nwac_config.license_info,
                           openapi_tags=self.nwac_config.tags,
                           openapi_url=f"{PREFIX}/openapi.json",
                           redoc_url=f"{PREFIX}/redoc",
                           title=self.nwac_config.title,
                           version=__version__,
                           )

        # Middlewares
        self.app.add_middleware(CorrelationIdMiddleware)
        self.app.add_middleware(ProxyHeadersMiddleware)
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins for testing, restrict in production
            allow_credentials=True,
            allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
            allow_headers=["*"],  # Allow all headers
        )
        # Add the available routes to our app, mounted under the prefix.
        for route in ROUTE_LIST:
            self.app.include_router(route, prefix=PREFIX)

        # Configure uvicorn via its Config class, applying any overrides from the NWaC config
        # that may have come in from the command line.
        self.uvicorn_config = Config(app=self.app)
        if self.nwac_config.port is not None:
            self.uvicorn_config.port = int(self.nwac_config.port)
        if self.nwac_config.host is not None:
            self.uvicorn_config.host = self.nwac_config.host
        self.uvicorn_config.use_colors = False
        self.uvicorn_config.log_level = self.nwac_config.log_level.lower()
        # GOOGLE_APPLICATION_CREDENTIALS controls how the Google Python APIs authenticate (e.g., it
        # points to a private key associated with the service account that we're using to talk to
        # firestore).
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS',
                                                                 self.nwac_config.app_credentials)
        LOG.info(f"GOOGLE_APPLICATION_CREDENTIALS: {self.nwac_config.app_credentials}")
        for name, details in self.nwac_config.endpoints.items():
            LOG.info(f"registered \'{name}\' as {details.endpoint_type.value} "
                     f"pointing to {details.url}")

        # We want to make validation errors a lot clearer for external developers.  To do that,
        # we need tp create a custom exception handler for request validation errors (they're
        # thrown by pydantic and handled by Fast API) and register it.
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc):
            err = str(exc).splitlines()
            # THIS IS FRAGILE.
            # These errors seem to come in clumps of 2 lines per error with a leading line
            # describing the number of errors found.
            # Assume that's just always true :(.  Specific assumptions are noted below.
            #
            # We can have 1 or more errors, depending on how messed up the request body actually
            # was.  Report them all here.
            # The encode().decode() stuff is to get the newlines to show as \n in our json output.
            err_count = err[0].split(' ')[0]  # line normally reads "N {some text...}"
            LOG.debug(f"{err_count} validation error(s) processing path {request.url.path} - "
                      f"raw message: {str(exc).encode('unicode_escape').decode()}")
            err = err[1:]  # the actual errors start on the next line
            error_messages = ParseErrors(error='failed to validate request body',
                                         count=err_count,
                                         messages=[])

            for i in range(0, int(err_count)):
                # The remaining lines should be in pairs.  The first line of the pair should be the
                # path and the second should be the actual problem with that path.  For example, if
                # the body is supposed to have an attribute foo that matches a regex, then the line
                # pair we get should look like:
                # body -> foo
                #   foo does not match regex <some regex>
                #
                # The actual details of the problem aren't relevant - we'll simply emit it - but
                # the path needs some processing.  Specifically, the path could be (depending
                # on how we construct our pydantic models): body -> foo -> __root__.  In this
                # case, root would be due to defining a custom type (e.g., IMSI which is a string
                # matching a specific regex).  We need to nuke the -> __root__ part as it conveys
                # no useful info to the API consumer - they don't know (and don't need to know)
                # the details of how we chose to implement our models.
                err_path = err[i * 2].strip()
                err_msg = err[i * 2 + 1].strip()
                if err_path.endswith('-> __root__'):  # pragma: nocover
                    err_path = err_path[0:err_path.index('-> __root__')].strip()
                parse_error = ParseError(path=err_path,
                                         message=err_msg)

                LOG.debug(f"error {i + 1}: {str(parse_error)}")
                error_messages.messages.append(parse_error)
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content=error_messages.dict()
                                )

    def run(self):
        """Run the REST server."""
        if self.nwac_config.log_level == 'DEBUG':
            self.uvicorn_config.debug = True
        server = uvicorn.Server(self.uvicorn_config)
        # Set these now (others were set above, in init())
        LOG.warning(f"setting log levels set to {self.nwac_config.log_level}")
        _loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for log in _loggers:
            log.setLevel(self.nwac_config.log_level)
            LOG.info(f"log level for {log.name} is "
                     f"{logging.getLevelName(log.getEffectiveLevel())}")
        _log = logging.getLogger()  # Root logger isn't in the above list, so do it now
        _log.setLevel(self.nwac_config.log_level)
        LOG.info(f"log level for ROOT logger is {logging.getLevelName(_log.getEffectiveLevel())}")
        server.run()
