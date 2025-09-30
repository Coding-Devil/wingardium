#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import json

from fastapi import APIRouter, HTTPException, status

from ai.agents.bedrock_client import bedrock_invoke
from ai.models.v1.wlchat import WLChatRequest
from ai.models.v1.wlpayload import WLPayloadRequest, WLPayloadResponse, default_wl_properties
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ["Workload Cluster Assistant"]

tag_metadata = {
    "name": "Workload Cluster Assistant",
    "description": "APIs for Workload Cluster payload schema and chat.",
}

WLCL_VALUES_STATE = {
    "cidrCNF": "",
    "oam": "",
    "signaling1": "",
    "signaling2": "",
    "sdlDatabase": "",
    "smfDsf1": "",
    "smfDsf2": "",
    "pgwProvisioning": "",
    "li": "",
}


@router.post(
    "/workload-cluster/payload",
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
        properties_obj = default_wl_properties(WLCL_VALUES_STATE)
        return WLPayloadResponse(properties=properties_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/workload-cluster/chat",
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
            f"""
    You are a useful Assistant.
    The user input might include the value for one or more of the following properties:
    {WLCL_VALUES_STATE}

    Your job is to return the same structure.
    The value of all parameters should be kept the same,
    except the one that the user has changed.
    Return only with the JSON object with no extra text.
            """
        )

        response_text = bedrock_invoke(
            system_prompt=system_prompt,
            user_msg=req.question,
            max_tokens=512,
        )

        data_json = json.loads(response_text)
        print(f"Data JSON: {data_json}")
        for key in data_json:
            WLCL_VALUES_STATE[key] = data_json[key]

        return response_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
