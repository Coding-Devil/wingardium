#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import json

from fastapi import APIRouter, HTTPException, status

from ai.agents.bedrock_client import bedrock_invoke
from ai.models.v1.infrahubclchat import InfraHubClChatRequest
from ai.models.v1.infrahubclpayload import (
    InfraHubClPayloadRequest, InfraHubClPayloadResponse, default_infra_hubcl_properties)
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ["Infra Hub Cluster Assistant"]

tag_metadata = {
    "name": "Infra Hub Cluster Assistant",
    "description": "APIs for Infra Hub Cluster payload schema and chat.",
}

INFRA_HUB_VALUES_STATE = {
    "clusterName": "",
    "domain": "",
    "vlanId": "",
    "storageVlanId": "",
    "machineNetwork": "",
    "machineNetworkGW": "",
    "clusterNetwork": "",
    "serviceNetwork": "",
    "apiVIP": "",
    "ingressVIP": "",
    "masterPassword": "",
    "sshPublicKey": "",
    "cidrNCP": "",
}


@router.post(
    "/hub-cluster/payload",
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
        properties_obj = default_infra_hubcl_properties(INFRA_HUB_VALUES_STATE)
        return InfraHubClPayloadResponse(properties=properties_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/hub-cluster/chat",
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
            f"""
    You are a useful Assistant.
    The user input might include the value for one or more of the following properties:
    {INFRA_HUB_VALUES_STATE}

    Your job is to return the same structure.
    The value of all parameters should be kept the same except the one that the user has changed.
    Return only with the JSON object with no extra text.
            """
        )

        response_text = bedrock_invoke(
            system_prompt=system_prompt,
            user_msg=req.input,
            max_tokens=512,
        )

        data_json = json.loads(response_text)
        print(f"Data JSON: {data_json}")
        for key in data_json:
            INFRA_HUB_VALUES_STATE[key] = data_json[key]

        return response_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
