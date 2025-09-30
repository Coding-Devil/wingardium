#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema, make


class WLPayloadRequest(BaseModel):
    question: str


class WLPayloadResponse(BaseModel):
    properties: dict[str, FieldSchema]


MAPPING_NAMES = {
    "cidrCNF": {
        "display": "Supernet CIDR for CNF",
        "value": ""
    },
    "oam": {
        "display": "OAM",
        "value": ""
    },
    "signaling1": {
        "display": "Signaling 1",
        "value": ""
    },
    "signaling2": {
        "display": "Signaling 2",
        "value": ""
    },
    "sdlDatabase": {
        "display": "SDL Database",
        "value": ""
    },
    "smfDsf1": {
        "display": "SMF DSF 1",
        "value": ""
    },
    "smfDsf2": {
        "display": "SMF DSF 2",
        "value": ""
    },
    "pgwProvisioning": {
        "display": "PGW Provisioning",
        "value": ""
    },
    "li": {
        "display": "Lawful Intercept (LI)",
        "value": ""
    }
}


# Mock factory for testing
def default_wl_properties(values: dict[str, str] = {}) -> dict[str, FieldSchema]:
    return {
        x: make(MAPPING_NAMES[x]["display"], values.get(x, "")) for x in MAPPING_NAMES
    }


def mock_wl_response() -> WLPayloadResponse:
    return WLPayloadResponse(properties=default_wl_properties())
