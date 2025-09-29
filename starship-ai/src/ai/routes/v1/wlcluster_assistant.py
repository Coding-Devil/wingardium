#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from fastapi import APIRouter, HTTPException, status

from ai.agents.bedrock_client import bedrock_invoke
from ai.models.v1.wlchat import WLChatRequest
from ai.models.v1.wlpayload import WLPayloadRequest, WLPayloadResponse, default_wl_properties
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ["wlcluster"]

tag_metadata = {
    "name": "Workload Cluster Assistant",
    "description": "APIs for Workload Cluster payload schema and chat.",
}


@router.post(
    "/wlcluster-payload",
    tags=tags,
    operation_id="PostWLClusterPayload",
    summary="Generate Workload Cluster payload schema",
    description=(
        "Returns Workload Cluster schema properties based on mandatory "
        "configuration metadata."
    ),
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            "model": WLPayloadResponse,
            "description": "Workload Cluster payload schema returned",
        },
    },
)
async def wlcluster_payload(req: WLPayloadRequest) -> WLPayloadResponse:
    try:
        properties_obj = default_wl_properties()
        return WLPayloadResponse(properties=properties_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/wlcluster-chat",
    tags=tags,
    operation_id="PostWLClusterChat",
    summary="Workload Cluster chat endpoint",
    description="Accepts user input and returns a plain text response.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            "model": str,
            "description": "Workload Cluster chat text response returned",
        },
    },
)
async def wlcluster_chat(req: WLChatRequest) -> str:
    try:
        system_prompt = (
            "You are the Workload Cluster Assistant. Provide concise, helpful answers "
            "about general Nokia telecom."
        )
        response_text = bedrock_invoke(
            system_prompt=system_prompt,
            user_msg=req.question,
            max_tokens=512,
        )
        return response_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
