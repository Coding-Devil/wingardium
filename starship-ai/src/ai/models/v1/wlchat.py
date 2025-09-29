#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class WLChatRequest(BaseModel):
    question: str


class WLChatProperties(dict):
    """Backward-compatible alias for type clarity. Use a dict[str, FieldSchema]."""

    pass


class WLChatResponse(BaseModel):
    properties: dict[str, FieldSchema]
    response: str


# Mock factory for testing
def build_mock_workload_response() -> WLChatResponse:
    return WLChatResponse(
        properties={},
        response="Mock workload response for testing",
    )
