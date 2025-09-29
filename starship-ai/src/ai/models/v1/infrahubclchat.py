#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class InfraHubClChatRequest(BaseModel):
    input: str


class InfraHubClProperties(dict):
    pass


class InfraHubClChatResponse(BaseModel):
    properties: dict[str, FieldSchema]
    response: str


# Optional mock helper

def mock_infra_hubcl_response() -> InfraHubClChatResponse:

    return InfraHubClChatResponse(
        properties={},
        response="Mock infra hubcluster schema for testing",
    )
