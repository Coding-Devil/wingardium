# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class CudoChatRequest(BaseModel):
    input: str


class CudoChatProperties(dict):
    """Backward-compatible alias for type clarity. Use a dict[str, FieldSchema]."""

    pass


class CudoChatResponse(BaseModel):
    properties: dict[str, FieldSchema]
    response: str


def build_mock_cudo_response() -> CudoChatResponse:
    """Create a mock CudoChatResponse object for quick testing."""
    return CudoChatResponse(
        properties={},
        response="Mock Cudo schema for testing",
    )
