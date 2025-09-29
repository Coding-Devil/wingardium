#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class WLPayloadRequest(BaseModel):
    question: str


class WLPayloadResponse(BaseModel):
    properties: dict[str, FieldSchema]


# Mock factory for testing
def default_wl_properties() -> dict[str, FieldSchema]:
    def make(display: str) -> FieldSchema:
        return FieldSchema(x_displayName=display, x_order=1)
    return {
        "cidrCNF": make("Supernet CIDR for CNF"),
        "oam": make("OAM"),
        "signaling1": make("Signaling 1"),
        "signaling2": make("Signaling 2"),
        "sdlDatabase": make("SDL Database"),
        "smfDsf1": make("SMF DSF 1"),
        "smfDsf2": make("SMF DSF 2"),
        "pgwProvisioning": make("PGW Provisioning"),
        "li": make("Lawful Intercept (LI)"),
    }


def mock_wl_response() -> WLPayloadResponse:
    return WLPayloadResponse(properties=default_wl_properties())
