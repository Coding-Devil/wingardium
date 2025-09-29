#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class GenInfoPayloadRequest(BaseModel):
    question: str


def default_gen_info_properties() -> dict[str, FieldSchema]:
    """Create a default General Info properties map with schema metadata."""
    def make(display: str) -> FieldSchema:
        return FieldSchema(x_displayName=display, x_order=1)
    return {
        "site": make("Site Location"),
        "timeZone": make("Time Zone"),
        "ipNTP": make("NTP Address"),
        "ipDNS1": make("DNS Address (Primary)"),
        "ipDNS2": make("DNS Address (Secondary)"),
        "mcc": make("MCC"),
        "mnc": make("MNC"),
        "plmn": make("PLMN"),
        "apn": make("APN/DNN"),
    }


class GenInfoPayloadResponse(BaseModel):
    properties: dict[str, FieldSchema]


# --- Mock helpers for testing/dev usage ---
def mock_gen_info_response() -> GenInfoPayloadResponse:
    """Create a mock GenInfoPayloadResponse object for quick testing."""
    return GenInfoPayloadResponse(
        properties=default_gen_info_properties(),
    )
