#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema, make


class GenInfoPayloadRequest(BaseModel):
    question: str


MAPPING_NAMES = {
    "site": {
        "display": "Site Location",
        "value": ""
    },
    "timeZone": {
        "display": "Time Zone",
        "value": ""
    },
    "ipNTP": {
        "display": "NTP Address",
        "value": ""
    },
    "ipDNS1": {
        "display": "DNS Address (Primary)",
        "value": ""
    },
    "ipDNS2": {
        "display": "DNS Address (Secondary)",
        "value": ""
    },
    "mcc": {
        "display": "MCC",
        "value": ""
    },
    "mnc": {
        "display": "MNC",
        "value": ""
    },
    "plmn": {
        "display": "PLMN",
        "value": ""
    },
    "apn": {
        "display": "APN/DNN",
        "value": ""
    },
}


def default_gen_info_properties(values: dict[str, str] = {}) -> dict[str, FieldSchema]:
    """Create a default General Info properties map with schema metadata."""
    return {
        x: make(MAPPING_NAMES[x]["display"], values.get(x, "")) for x in MAPPING_NAMES
    }


class GenInfoPayloadResponse(BaseModel):
    properties: dict[str, FieldSchema]


# --- Mock helpers for testing/dev usage ---
def mock_gen_info_response() -> GenInfoPayloadResponse:
    """Create a mock GenInfoPayloadResponse object for quick testing."""
    return GenInfoPayloadResponse(
        properties=default_gen_info_properties(),
    )
