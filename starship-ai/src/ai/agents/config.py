# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# Configuration constants for the CMM Deployment Assistant.
#
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# File paths
BLUEPRINT_PATH = "golden_config_CMM_yaml.txt"

# API Configuration
CUDO_API_URL = "https://athena-cudo.ati.dyn.tre.nsn-rdnet.net/generator/generator/v2/chat/"

# AWS Bedrock Configuration
BEDROCK_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
BEDROCK_REGION = "us-east-1"
