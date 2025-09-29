#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel

# from mandatory_conf import MandatoryField
from ai.models.v1.common import FieldSchema


class CIQPayloadRequest(BaseModel):
    input: str


class CIQPayloadResponse(BaseModel):
    properties: dict[str, FieldSchema]


def get_default_ciq_parameters() -> dict[str, FieldSchema]:
    """Create a mock CIQ properties map with default schema metadata."""
    def make(display: str) -> FieldSchema:
        return FieldSchema(x_displayName=display, x_order=1)
    return {
        "alms_host_interface": make("Site Location"),
        "alms_interface": make("Time Zone"),
        "alms_ipv4_cidr": make("NTP Address"),
        "alms_ipv4_gw": make("DNS Address (Primary)"),
        "alms_ipv4_ip": make("DNS Address (Secondary)"),
        "alms_type": make("DNS Address (Secondary)"),
        "dnn1": make("DNS Address (Secondary)"),
        "dnn2": make("DNS Address (Secondary)"),
        "mcc": make("DNS Address (Secondary)"),
        "mnc": make("DNS Address (Secondary)"),
        "network_name": make("DNS Address (Secondary)"),
        "network_short_name": make("DNS Address (Secondary)"),
        "nrf_endpoint_fqdn": make("DNS Address (Secondary)"),
        "nrf_endpoint_port": make("DNS Address (Secondary)"),
        "nssf_endpoint_fqdn": make("DNS Address (Secondary)"),
        "nssf_endpoint_port": make("DNS Address (Secondary)"),
        "primary_dns_ip": make("DNS Address (Secondary)"),
        "sd1": make("DNS Address (Secondary)"),
        "sd2": make("DNS Address (Secondary)"),
        "sd3": make("DNS Address (Secondary)"),
        "ca4mn_passwd": make("DNS Address (Secondary)"),
        "cbamuser_passwd": make("DNS Address (Secondary)"),
        "cgw_passwd": make("DNS Address (Secondary)"),
        "cmm_passwd": make("DNS Address (Secondary)"),
        "cmmsecurity_passwd": make("DNS Address (Secondary)"),
        "dcae_dfc_passwd": make("DNS Address (Secondary)"),
        "diagnostic_passwd": make("DNS Address (Secondary)"),
        "root_passwd": make("DNS Address (Secondary)"),
        "rsp_passwd": make("DNS Address (Secondary)"),
        "sam5620_passwd": make("DNS Address (Secondary)"),
        "trainee_passwd": make("DNS Address (Secondary)"),
        "storageclass": make("DNS Address (Secondary)"),
        "timezone": make("DNS Address (Secondary)"),
    }


def build_mock_ciq_response() -> CIQPayloadResponse:
    """Create a mock CIQPayloadResponse object for quick testing."""
    return CIQPayloadResponse(
        properties=get_default_ciq_parameters(),
    )
