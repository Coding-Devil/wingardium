#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from fastapi import APIRouter, HTTPException, status

from ai.agents.bedrock_client import bedrock_invoke
from ai.models.v1.infrahubclchat import InfraHubClChatRequest
from ai.models.v1.infrahubclpayload import (
    InfraHubClPayloadRequest, InfraHubClPayloadResponse, default_infra_hubcl_properties)
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ["infra"]

tag_metadata = {
    "name": "Infra Hub Cluster Assistant",
    "description": "APIs for Infra Hub Cluster payload schema and chat.",
}


@router.post(
    "/infra-payload",
    tags=tags,
    operation_id="PostInfraPayload",
    summary="Generate Infra Hub Cluster payload schema",
    description="Returns Infra Hub Cluster schema properties based on default metadata.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            "model": InfraHubClPayloadResponse,
            "description": "Infra Hub Cluster payload schema returned",
        },
    },
)
async def infra_payload(req: InfraHubClPayloadRequest) -> InfraHubClPayloadResponse:
    try:
        properties_obj = default_infra_hubcl_properties()
        return InfraHubClPayloadResponse(properties=properties_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/infra-chat",
    tags=tags,
    operation_id="PostInfraChat",
    summary="Infra Hub Cluster chat endpoint",
    description="Accepts user input and returns a plain text response.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            "model": str,
            "description": "Infra Hub Cluster chat text response returned",
        },
    },
)
async def infra_chat(req: InfraHubClChatRequest) -> str:
    try:
        system_prompt = (
            "You are the Infra Hub Cluster Assistant. Provide concise, helpful answers "
            "about infrastructure and cluster configuration."
        )
        response_text = bedrock_invoke(
            system_prompt=system_prompt,
            user_msg=req.input,
            max_tokens=512,
        )
        return response_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
