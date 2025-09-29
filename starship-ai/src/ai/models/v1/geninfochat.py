#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class GenInfoChatRequest(BaseModel):
    question: str


class GenInfoProperties(dict):
    pass


class GenInfoChatResponse(BaseModel):
    properties: dict[str, FieldSchema]
    response: str


def mock_gen_info_response() -> GenInfoChatResponse:
    """Create a mock GenInfoChatResponse object for quick testing."""
    return GenInfoChatResponse(
        properties={},
        response="Mock general info schema for testing",
    )
