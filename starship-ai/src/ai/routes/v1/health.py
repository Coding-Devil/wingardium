#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from fastapi import APIRouter, status

from ai.models.v1.health import HealthResponse
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ['health']

tag_metadata = {'name': 'health',
                'description': 'Health check APIs.'}


@router.get("/health",
            tags=tags,
            operation_id="GetHealthCheck",
            summary='Health check api',
            description='Validates that the service is up and running.',
            responses={**COMMON_ERRORS,
                        status.HTTP_200_OK: {
                            'model': HealthResponse,
                            'description': 'A list of rack units for the given rack id'}})
async def health_check():
    return {"status": "ok"}
