# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# AI helper functions for the CMM Deployment Assistant.
#
import streamlit as st

from ai.agents.bedrock_client import bedrock_invoke

from .cudo_client import query_cudo_api
from .yaml_parser import PARAM_DESCRIPTIONS


@st.cache_data
def query_cudo_with_spinner(query: str, current_param: str = None) -> str:
    """
    Query CuDo API with contextual information and spinner.

        query: User query
        current_param: Current parameter being configured

    Returns:
        CuDo API response
    """
    contextual_query = query
    if current_param:
        param_description = PARAM_DESCRIPTIONS.get(current_param, "")
        contextual_query = (
            "Context: I'm currently configuring the CMM parameter "
            f"'{current_param}' which is: {param_description}\n"
            f"User Question: {query}\n"
            "Please provide relevant information about this parameter or answer the "
            "user's question in the context of CMM deployment configuration."
        )

    with st.spinner("Searching CuDo documentation..."):
        return query_cudo_api(contextual_query)


def supervisor_classify(user_input: str, current_param: str) -> str:
    """
    Classify user input using AI supervisor.

    Args:
        user_input: User's input text
        current_param: Current parameter being asked about

    Returns:
        Classification category
    """
    system_prompt = (
        "You are a supervisor AI that classifies user input for a CMM deployment chatbot. "
        "Classify the input into one of these categories: 'param_answer', 'tech_query', "
        "'general_silly', 'skip_done'. Return ONLY the category name."
    )
    user_msg = (
        "The user is currently being asked for the value of the parameter: "
        f"'{current_param}'.\nUser input: \"{user_input}\""
    )
    response = bedrock_invoke(system_prompt, user_msg, max_tokens=20)
    return response.strip().lower()


def generate_question(param: str) -> str:
    """
    Generate a friendly question for a parameter using AI.

    Args:
        param: Parameter name

    Returns:
        Generated question text
    """
    system_prompt = (
        "You are a friendly CMM Deployment Assistant. Generate a friendly, one-sentence "
        "question to ask the user for a parameter value, using the provided description "
        "for context."
    )
    user_msg = (
        f"Parameter: '{param}'\nDescription: \"{PARAM_DESCRIPTIONS.get(param, '')}\""
    )
    return bedrock_invoke(system_prompt, user_msg, max_tokens=100).strip()
