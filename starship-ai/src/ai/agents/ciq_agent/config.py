# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# Configuration settings for CIQ Agent
#

from pathlib import Path

# Get the directory where this config file is located
CIQ_AGENT_DIR = Path(__file__).parent

# Path to the golden config YAML blueprint
BLUEPRINT_PATH = CIQ_AGENT_DIR / "golden_config_CMM_yaml.txt"

# CIQ Parameter descriptions mapping
PARAM_DESCRIPTIONS = {
    "global.alms.host_interface": "ALMS host network interface configuration",
    "global.alms.interface": "ALMS interface type and settings",
    "global.alms.ipv4_cidr": "ALMS IPv4 CIDR network configuration",
    "global.alms.ipv4_gw": "ALMS IPv4 gateway address",
    "global.alms.ipv4_ip": "ALMS IPv4 IP address",
    "global.alms.type": "ALMS container type configuration",
    "global.provisioning.dnn1": "Data Network Name 1 for 5G provisioning",
    "global.provisioning.dnn2": "Data Network Name 2 for 5G provisioning",
    "global.provisioning.mcc": "Mobile Country Code for network identification",
    "global.provisioning.mnc": "Mobile Network Code for network identification",
    "global.provisioning.network_name": "Full network name for display",
    "global.provisioning.network_short_name": "Short network name for display",
    "global.provisioning.nrf_endpoint_fqdn": "Network Repository Function endpoint FQDN",
    "global.provisioning.nrf_endpoint_port": "Network Repository Function endpoint port",
    "global.provisioning.nssf_endpoint_fqdn": "Network Slice Selection Function endpoint FQDN",
    "global.provisioning.nssf_endpoint_port": "Network Slice Selection Function endpoint port",
    "global.provisioning.primary_dns_ip": "Primary DNS server IP address",
    "global.provisioning.sd1": "Slice Differentiator 1 for network slicing",
    "global.provisioning.sd2": "Slice Differentiator 2 for network slicing",
    "global.provisioning.sd3": "Slice Differentiator 3 for network slicing",
    "global.secrets.users.ca4mn_passwd": "CA4MN user password for authentication",
    "global.secrets.users.cbamuser_passwd": "CBAM user password for authentication",
    "global.secrets.users.cgw_passwd": "CGW user password for authentication",
    "global.secrets.users.cmm_passwd": "CMM user password for authentication",
    "global.secrets.users.cmmsecurity_passwd": "CMM security user password",
    "global.secrets.users.dcae_dfc_passwd": "DCAE DFC user password for authentication",
    "global.secrets.users.diagnostic_passwd": "Diagnostic user password for system access",
    "global.secrets.users.root_passwd": "Root user password for system administration",
    "global.secrets.users.rsp_passwd": "RSP user password for authentication",
    "global.secrets.users.sam5620_passwd": "SAM5620 user password for authentication",
    "global.secrets.users.trainee_passwd": "Trainee user password for limited access",
    "global.containers.storageclass": "Kubernetes storage class for persistent volumes",
    "global.containers.timezone": "System timezone configuration for containers"
}

# Default CIQ session configuration
DEFAULT_SESSION_CONFIG = {
    "max_session_duration": 3600,  # 1 hour in seconds
    "session_cleanup_interval": 300,  # 5 minutes in seconds
    "max_concurrent_sessions": 100
}

# CuDo API configuration
CUDO_CONFIG = {
    "base_url": "https://athena-cudo.ati.dyn.tre.nsn-rdnet.net/generator/generator/v2/chat/",
    "user_id": "4201337",
    "chat_id": "ciq_assistant",
    "max_retries": 3,
    "timeout": 30
}
