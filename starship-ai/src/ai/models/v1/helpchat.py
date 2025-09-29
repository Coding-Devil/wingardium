#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from typing import Any

from pydantic import BaseModel


class HelpChatRequest(BaseModel):
    question: str


class HelpChatResponse(BaseModel):
    answer: str  # HTML text
    raw: Any | None = None
