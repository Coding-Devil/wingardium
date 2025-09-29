#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from fastapi import APIRouter, HTTPException, status

from ai.agents.bedrock_client import bedrock_invoke
from ai.models.v1.geninfochat import GenInfoChatRequest
from ai.models.v1.geninfopayload import (
    GenInfoPayloadRequest, GenInfoPayloadResponse, default_gen_info_properties)
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ["general-info"]

tag_metadata = {
    "name": "General Info Assistant",
    "description": "APIs for generating general information payload schemas.",
}


@router.post(
    "/geninfo_payload",
    tags=tags,
    operation_id="PostGeneralInfoPayload",
    summary="Generate General Info payload schema",
    description="Returns General Info schema properties based on default metadata.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            "model": GenInfoPayloadResponse,
            "description": "General Info payload schema returned",
        },
    },
)
async def geninfo_payload(req: GenInfoPayloadRequest) -> GenInfoPayloadResponse:
    try:
        properties_obj = default_gen_info_properties()
        return GenInfoPayloadResponse(properties=properties_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Optional alias with hyphen for compatibility with requested path style
@router.post(
    "/geninfo-chat",
    tags=tags,
    operation_id="PostGeneralInfoChat",
    summary="Generate General Info chat endpoint",
    description="Accepts user input and returns a plain text response.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            "model": str,
            "description": "General Info chat text response returned",
        },
    },
)
async def geninfo_payload_hyphen(req: GenInfoChatRequest) -> str:
    try:
        system_prompt = (
            "You are the General Info Assistant. Provide concise, helpful answers "
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
