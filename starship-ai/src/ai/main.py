#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from __future__ import annotations

import argparse

import yaml
from fastapi.openapi.utils import get_openapi

from ai import LOG, __version__
from ai.app import App
from ai.config import CONFIG
# from sm.db.docdb import init_doc_dbs
from ai.routes.v1 import __api_version__


def create_parser():
    """
    Parse command line arguments and set defaults.

    Note: callers may safely assume that everything other than version and help will have default
    values specified.  That means they do not need to apply any additional defaults.
    """
    _p = argparse.ArgumentParser()
    _p.add_argument('--port',
                    default=5050,
                    help="Port to run the server on (default: %(default)s)"
                    )
    _p.add_argument('--log_level',
                    default='INFO',
                    help="Standard Python log level to emit message for (default: %(default)s)"
                    )
    _p.add_argument('--version',
                    action='version',
                    version=f"%(prog)s {__version__}"
                    )
    _p.add_argument('--dev',
                    default=False,
                    action='store_true',
                    help="Run server in dev mode (default: %(default)s)")
    _p.add_argument('--config_file',
                    default='../../starship.yaml',
                    help="Config file (default: %(default)s)")
    _p.add_argument('--dump_schema',
                    default=False,
                    action='store_true',
                    help=("Print the schema to ./openapi_{api version}.yaml and exit "
                          "(default: %(default)s)")
                    )
    _p.add_argument('--intent-list-api-url',
                    help='Override the intent list API URL'
                    )
    _p.add_argument('--intent-list-version',
                    help='Override the intent list API version'
                    )
    _p.add_argument('--intent-list-timeout',
                    help='Override the intent list API timeout in seconds'
                    )

    return _p


def main():  # pragma: nocover
    # The sequence of events here is:
    # 1) Process any command line args.  These will set defaults as well.
    # 2) Update the global config with settings from the config file.
    # 3) Create the app from the config and apply any command line options (they override the
    #    config file).
    # 4) Initialize the app.
    # 5) Process any "... and exit" options, e.g. dumping the schema.  Note that version and help
    #    are handled in parse_args().
    # 6) Do any DB initialization that may be required.
    # 7) Run the app.  We expect the app to only exit when the server has been told to stop
    #    (or on some catastrophic error that we/it doesn't handle).
    _args = vars(create_parser().parse_args())
    LOG.info('Starting server initialization')
    CONFIG.config_file = _args['config_file']
    CONFIG.update_from_file()
    app = App(config=CONFIG)
    app.override(args=_args)
    app.init()
    if _args['dump_schema']:
        with open(f'openapi_{__api_version__}.yaml', 'w') as f:
            _spec = get_openapi(title=app.app.title,
                                version=app.app.version,
                                openapi_version=app.app.openapi_version,
                                description=app.app.description,
                                routes=app.app.routes,
                                tags=CONFIG.tags,
                                contact=CONFIG.contact_info,
                                license_info=CONFIG.license_info,
                                servers=CONFIG.servers,
                                )
            _spec['info']['contact']['url'] = CONFIG.contact_url
            _spec['info']['license']['url'] = CONFIG.license_url
            _spec['servers'][0]['url'] = CONFIG.url
            yaml.dump(_spec, f)
        return 0
    # init_doc_dbs(app=app)
    app.run()


if __name__ == '__main__':  # pragma: nocover
    exit(main())
