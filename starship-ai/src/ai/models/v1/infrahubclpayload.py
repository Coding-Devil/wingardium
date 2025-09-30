#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

from ai.models.v1.common import FieldSchema, make


class InfraHubClPayloadRequest(BaseModel):
    question: str


MAPPING_NAMES = {
    "clusterName": {
        "display": "Cluster Name",
        "value": ""
    },
    "domain": {
        "display": "Cluster Domain",
        "value": ""
    },
    "vlanId": {
        "display": "VLAN ID",
        "value": ""
    },
    "storageVlanId": {
        "display": "Storage VLAN ID",
        "value": ""
    },
    "machineNetwork": {
        "display": "Machine Network",
        "value": ""
    },
    "machineNetworkGW": {
        "display": "Machine Network Gateway",
        "value": ""
    },
    "clusterNetwork": {
        "display": "Cluster Network",
        "value": ""
    },
    "serviceNetwork": {
        "display": "Service Network",
        "value": ""
    },
    "apiVIP": {
        "display": "API VIP",
        "value": ""
    },
    "ingressVIP": {
        "display": "Ingress VIP",
        "value": ""
    },
    "masterPassword": {
        "display": "Master Password",
        "value": ""
    },
    "sshPublicKey": {
        "display": "SSH Public Key",
        "value": ""
    },
    "cidrNCP": {
        "display": "Supernet CIDR for NCP",
        "value": ""
    },
}


def default_infra_hubcl_properties(values: dict[str, str] = {}) -> dict[str, FieldSchema]:
    """Create a default Infra Hub Cluster properties map with schema metadata."""
    # Iterate over all keys in MAPPING_NAMES and create a FieldSchema for each. The values
    # come from the values parameter. If the values parameter is empty, the values are set to
    # set from the default values in MAPPING_NAMES.
    return {
        x: make(MAPPING_NAMES[x]["display"], values.get(x, "")) for x in MAPPING_NAMES
    }


class InfraHubClPayloadResponse(BaseModel):

    properties: dict[str, FieldSchema]


def mock_infra_hubcl_response() -> InfraHubClPayloadResponse:
    return InfraHubClPayloadResponse(
        properties=default_infra_hubcl_properties(),
    )
