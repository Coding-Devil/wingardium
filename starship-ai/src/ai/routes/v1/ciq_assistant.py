#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from fastapi import APIRouter, HTTPException, status

from ai.models.v1.ciqchat import CIQChatRequest
from ai.models.v1.ciqpayload import CIQPayloadRequest, CIQPayloadResponse
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ['ciq']

tag_metadata = {
    'name': 'CIQ Assistant',
    'description': 'AI CIQ Assistant APIs.'
}


@router.post(
    "/ciq_payload",
    tags=tags,
    operation_id="PostCIQPayload",
    summary="Generate CIQ payload schema",
    description="Returns CIQ schema properties based on mandatory configuration metadata.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            'model': CIQPayloadResponse,
            'description': 'CIQ payload schema returned'
        }
    },
)
async def ciq_payload(req: CIQPayloadRequest) -> CIQPayloadResponse:
    try:
        # Attempt to derive properties from mandatory configuration
        try:
            from mandatory_conf import MANDATORY_FIELDS
            mandatory_fields = list(MANDATORY_FIELDS)
        except Exception:
            mandatory_fields = []

        def path_to_field_name(path: str) -> str:
            # Strip leading global_.
            if path.startswith("global_."):
                remainder = path[len("global_."):]
            else:
                remainder = path
            # Special handling for groups
            if remainder.startswith("alms."):
                name = "alms_" + remainder[len("alms."):].replace(".", "_")
            elif remainder.startswith("provisioning."):
                name = remainder[len("provisioning."):].replace(".", "_")
            elif remainder.startswith("secrets.users."):
                name = remainder[len("secrets.users."):].replace(".", "_")
            else:
                name = remainder.replace(".", "_")
            return name

        properties_obj = {}
        for mf in mandatory_fields:
            field_name = path_to_field_name(mf.path)
            properties_obj[field_name] = {
                "type": "string",
                "x-displayName": getattr(mf, "label", None) or field_name,
                "x-order": 1,
            }

        return CIQPayloadResponse(properties=properties_obj, response="CIQ schema returned")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/ciq_chat",
    tags=tags,
    operation_id="PostCIQChat",
    summary="CIQ chat endpoint",
    description="Accepts user input and returns an AI-generated text response.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            'model': str,
            'description': 'CIQ chat text response returned'
        }
    },
)
async def ciq_chat(req: CIQChatRequest) -> str:
    try:
        # Placeholder for AI-generated content; currently echoing input
        return f"Received input: {req.input}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
