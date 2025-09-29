#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from typing import Any, Dict, List, Union

import yaml

from ai import LOG
from ai.endpoints.v1.endpoints import EndPoints
from ai.exceptions import ConfigError

DEFAULT_INTENT_API_URL = "https://ccma.int.net.nokia.com/api/v1/intents"


class NWaCConfig(object):
    """
    The NWaCConfig object encapsulates the various configuration options for the NWaC backend.

    It expects to read most config values from a config file.  The config file attributes
    in the default section and the object's attributes are expected to match - if you change a
    name here/there you must also update it there/here.
    """

    def __init__(self, config_file: str = '../../starship.yaml'):
        self.config_file = config_file

        self.description = None
        self.title = None
        self.contact_name = None
        self.contact_email = None
        self.contact_url = None
        self.license_name = None
        self.license_url = None
        self.public_url = None

        self.host = None
        self.port = None
        self.log_level = ""
        self.project_id = ""
        self.app_credentials = ""
        self.endpoints = EndPoints()
        self.dev = False
        self.dbs = {}
        self.tags = []

        self.intent_list_api_url = DEFAULT_INTENT_API_URL
        self.intent_list_version = "v1"
        self.intent_list_timeout = 5

        self._initialized = False

    def update_from_file(self):
        with open(self.config_file) as _f:
            _c = yaml.load(_f, Loader=yaml.SafeLoader)

        # Process mandatory settings.
        try:
            _default = _c['default']
        except KeyError:
            raise ConfigError(self.config_file, 'default') from None

        for i in _default.keys():
            if hasattr(self, i):
                setattr(self, i, _default[i])
            else:
                # Unknown key in default section: fail fast to surface config issues
                raise ConfigError(self.config_file, i)  # pragma: nocover

        # Process endpoint settings.
        endpoints_section = _c.get('endpoints')
        if endpoints_section is None:
            # Backward compatibility for potential v2 key changes
            endpoints_section = _c.get('services') or _c.get('endpoints_v2')

        if not endpoints_section:
            LOG.warning(
                "Config has no 'endpoints' section (or recognized alternative). "
                "Skipping endpoint setup."
            )
        else:
            for i in endpoints_section:
                try:
                    _name = i['name']
                except KeyError:  # pragma: nocover
                    raise ConfigError(self.config_file, 'name') from None
                try:
                    self.endpoints.add_endpoint(_name, i)
                except KeyError as _e:  # pragma: nocover
                    raise ConfigError(self.config_file, _e.args) from None

        self._initialized = True

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def license_info(self) -> dict:
        return {'name': self.license_name,
                'url': self.license_url}

    @property
    def contact_info(self) -> dict:
        return {'name': self.contact_name,
                'url': self.contact_url,
                'email': self.contact_email}

    @property
    def url(self) -> str:
        return self.public_url

    @property
    def servers(self) -> List[Dict[str, Union[str, Any]]]:
        return [{'url': self.url,
                 'description': 'Starship AI'}]


CONFIG = NWaCConfig()


# Function to fetch configuration values dynamically
def get_config_value(key):
    """Retrieve a config value dynamically after the config has been loaded."""
    value = getattr(CONFIG, key, None)
    if value is None:
        LOG.warning(f"{key} is not set in the config file.")
    return value
