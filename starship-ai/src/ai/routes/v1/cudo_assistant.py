#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from fastapi import APIRouter, HTTPException, status

from ai import LOG
from ai.agents.athena_cudo_agent import AthenaCuDoClient
from ai.models.v1.cudochat import CudoChatRequest
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ['CUDO Assistant']
tag_metadata = {
    'name': 'CUDO Assistant',
    'description': 'AI CUDO Assistant APIs.'
}


@router.post(
    "/cudo/chat",
    tags=tags,
    operation_id="CuDoChat",
    summary="CuDochat endpoint",
    description="Accepts user input and returns an AI-generated text response.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            'model': str,
            'description': 'CuDo chat text response returned'
        }
    },
)
async def cudo_chat(req: CudoChatRequest) -> str:
    try:
        # Log incoming input
        LOG.info(f"Received input: {req.input}")

        # Send the actual user input to Athena and extract normalized content
        client = AthenaCuDoClient()
        response = client.send_message(req.input)
        if not response:
            raise HTTPException(status_code=502, detail="Upstream AI service returned no response")

        content = client.extract_content(response)
        LOG.info(f"Extracted content: {content}")

        return content
    except Exception as e:
        LOG.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
