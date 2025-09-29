#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class InfraHubClPayloadRequest(BaseModel):
    question: str


def default_infra_hubcl_properties() -> dict[str, FieldSchema]:
    """Create a default Infra Hub Cluster properties map with schema metadata."""
    def make(display: str) -> FieldSchema:
        return FieldSchema(x_displayName=display, x_order=1)
    return {
        "cidrNCP": make("Supernet CIDR for NCP"),
    }


class InfraHubClPayloadResponse(BaseModel):
    properties: dict[str, FieldSchema]


def mock_infra_hubcl_response() -> InfraHubClPayloadResponse:
    return InfraHubClPayloadResponse(
        properties=default_infra_hubcl_properties(),
    )
