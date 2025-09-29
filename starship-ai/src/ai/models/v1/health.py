#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel


# Model for login requests
class HealthResponse(BaseModel):
    status: str
