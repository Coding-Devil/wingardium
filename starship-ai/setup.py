#  Copyright (c) 2022 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import os

import setuptools
import yaml

# Get the component name (to keep it consistent with builds)
with open('project-config.yml') as _f:
    _config = yaml.load(_f, Loader=yaml.SafeLoader)
    _component = _config['component']
    _version = _config['version']['released']

# If we're running in our CI environment, use sub_version
_version = os.environ.get('sub_version', _version)

setuptools.setup(
    name=_component,
    version=_version,
)
