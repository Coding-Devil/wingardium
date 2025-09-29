# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# AWS Bedrock client and related functions.
#
import json

import boto3
import streamlit as st
from botocore.exceptions import ClientError

from .config import BEDROCK_MODEL, BEDROCK_REGION


@st.cache_resource
def get_bedrock_client():
    """Get cached AWS Bedrock client."""
    try:
        return boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
    except Exception as e:
        st.error(
            f"Error configuring AWS Bedrock: {e}. "
            "Please ensure your AWS credentials are configured correctly."
        )
        st.stop()


def bedrock_invoke(system_prompt: str, user_msg: str, max_tokens: int = 512) -> str:
    """
    Invoke AWS Bedrock with the given prompts.

    Args:
        system_prompt: System prompt for the AI
        user_msg: User message
        max_tokens: Maximum tokens to generate

    Returns:
        AI response text
    """
    client = get_bedrock_client()
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_msg}],
        "temperature": 0.1
    })
    try:
        resp = client.invoke_model(body=body, modelId=BEDROCK_MODEL)
        return json.loads(resp['body'].read())['content'][0]['text']
    except ClientError as e:
        st.error(f"Bedrock API error: {e}")
        return "Error: Unable to get response from AI model."
