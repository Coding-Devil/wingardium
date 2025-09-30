#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from typing import Optional

from pydantic import BaseModel

from ai.models.v1.common import FieldSchema


class CIQChatRequest(BaseModel):
    input: str
    session_id: Optional[str] = None


class CIQChatProperties(dict):
    """Backward-compatible alias for type clarity. Use a dict[str, FieldSchema]."""

    pass


class CIQChatResponse(BaseModel):
    response: str
    session_id: str
    progress: dict
    is_complete: bool = False
    final_yaml: Optional[str] = None
    properties: Optional[dict[str, FieldSchema]] = None


def build_mock_ciq_response() -> CIQChatResponse:
    """Create a mock CIQChatResponse object for quick testing."""
    return CIQChatResponse(
        response="Mock CIQ chat response for testing",
        session_id="test-session-123",
        progress={"total_params": 10, "collected_count": 3, "progress_percentage": 30},
        is_complete=False,
        properties={}
    )
