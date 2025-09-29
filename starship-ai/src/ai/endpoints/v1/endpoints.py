#  Copyright (c) 2022 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from typing import List, Union

from ai.endpoints.v1 import EndpointTypes


class EndPoint(object):
    def __init__(self, config: dict):
        self.endpoint_type = EndpointTypes(config['type'])
        self.url = config['url']
        self.name = config['name']
        self.read_timeout = config['read_timeout']
        self.connect_timeout = config['connect_timeout']

        self.default_headers = {}
        if 'headers' in config:
            for k, v in config['headers'].items():
                self.default_headers[k] = v
        self.headers = self.default_headers.copy()

    def __str__(self) -> str:
        if self.headers != {}:
            return str({'name': self.name,
                        'url': self.url,
                        'type': self.endpoint_type.value,
                        'connect_timeout': self.connect_timeout,
                        'read_timeout': self.read_timeout,
                        'headers': self.headers})
        else:
            return str({'name': self.name,
                        'url': self.url,
                        'type': self.endpoint_type.value,
                        'connect_timeout': self.connect_timeout,
                        'read_timeout': self.read_timeout})

    def update_headers(self, key: str, value: Union[str, int]):
        self.headers[key] = value

    def reset_headers(self):
        self.headers = self.default_headers


class EndPoints(object):
    def __init__(self):
        self.endpoint = {}

    def __getitem__(self, item):
        return self.endpoint[item]

    def __len__(self):
        return len(self.endpoint)

    def __contains__(self, ep: EndPoint):
        return ep in self.endpoint

    def items(self):
        return self.endpoint.items()

    def by_type(self, ep_type: EndpointTypes) -> List[EndPoint]:
        return [info for name, info in self.endpoint.items() if info.endpoint_type == ep_type]

    def add_endpoint(self, name: str, config: dict):
        self.endpoint[name] = EndPoint(config)
