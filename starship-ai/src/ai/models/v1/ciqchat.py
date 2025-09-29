#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class CIQChatRequest(BaseModel):
    input: str


class CIQChatProperties(dict):
    """Backward-compatible alias for type clarity. Use a dict[str, FieldSchema]."""

    pass


class CIQChatResponse(BaseModel):
    properties: dict[str, FieldSchema]
    response: str


def build_mock_ciq_response() -> CIQChatResponse:
    """Create a mock CIQChatResponse object for quick testing."""
    return CIQChatResponse(
        properties={},
        response="Mock CIQ schema for testing",
    )
