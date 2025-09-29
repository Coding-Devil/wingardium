# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# Streamlit UI components and layout functions.
#
import pandas as pd
import streamlit as st
import yaml

from ai.agents.bedrock_client import bedrock_invoke

from .ai_helpers import generate_question, query_cudo_with_spinner, supervisor_classify
from .config import BLUEPRINT_PATH
from .yaml_parser import USER_PARAMS, load_yaml_blueprint


def setup_page_config():
    """Set up Streamlit page configuration and custom CSS."""
    st.set_page_config(page_title="CMM Deployment Assistant", layout="wide")
    st.title(" CMM Deployment Assistant")
    css = (
        "<style>\n"
        ".stChatMessage:has(div[data-testid=\"chat-avatar-assistant\"]) "
        "div[data-testid=\"stMarkdownContainer\"] p {\n"
        "    color: #2E8B57;\n"
        "}\n"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'collected_values' not in st.session_state:
        st.session_state.collected_values = {}
    if 'missing_params' not in st.session_state:
        st.session_state.missing_params = set(USER_PARAMS)
    if 'current_param' not in st.session_state:
        st.session_state.current_param = USER_PARAMS[0] if USER_PARAMS else None
    if 'initial_message' not in st.session_state:
        st.session_state.history.append({
            "role": "assistant",
            "content": (
                "Hi! I'm your CMM Deployment Assistant. I'll guide you through filling the "
                "key config parameters step by step. Let's begin!"
            )
        })
        st.session_state.initial_message = True
    if 'final_yaml' not in st.session_state:
        st.session_state.final_yaml = ""


def render_progress_panel():
    """Render the left panel with progress and parameter table."""
    st.header("Configuration Progress")
    progress_value = (len(USER_PARAMS) - len(st.session_state.missing_params)) / len(USER_PARAMS)
    st.progress(
        progress_value,
        text=(
            f"{len(USER_PARAMS) - len(st.session_state.missing_params)} / "
            f"{len(USER_PARAMS)} filled"
        ),
    )

    st.subheader("Parameters")
    table_data = []
    for param in USER_PARAMS:
        value = st.session_state.collected_values.get(param, "Pending...")
        status = "✅" if param in st.session_state.collected_values else "📝"
        short_param = (
            param.replace("global.provisioning.", "")
            .replace("global.containers.", "")
            .replace("global.", "")
        )
        table_data.append({"Status": status, "Parameter": short_param, "Value": value})

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.session_state.final_yaml:
        st.subheader("Final Deployment YAML")
        st.download_button(
            label="Download YAML",
            data=st.session_state.final_yaml,
            file_name="deployment_config.yaml",
            mime="text/yaml"
        )
        st.code(st.session_state.final_yaml, language='yaml', line_numbers=True)


def render_chat_panel():
    """Render the right panel with chat interface."""
    st.header("Chat with your Assistant")

    # Display chat history
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if user_input := st.chat_input("Your response..."):
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        if st.session_state.current_param:
            with st.chat_message("assistant"):
                response_text = process_user_input(user_input)
                st.markdown(response_text)
                st.session_state.history.append({"role": "assistant", "content": response_text})
                st.rerun()


def process_user_input(user_input: str) -> str:
    """
    Process user input and return appropriate response.

    Args:
        user_input: User's input text

    Returns:
        Response text for the assistant
    """
    with st.spinner("Thinking..."):
        intent = supervisor_classify(user_input, st.session_state.current_param)
        response_text = ""

        if intent == 'param_answer':
            st.session_state.collected_values[st.session_state.current_param] = user_input
            st.session_state.missing_params.discard(st.session_state.current_param)
            response_text = "Great, I've noted that down. "

            if st.session_state.missing_params:
                st.session_state.current_param = sorted(st.session_state.missing_params)[0]
                response_text += generate_question(st.session_state.current_param)
            else:
                st.session_state.current_param = None
                response_text += (
                    "All parameters have been collected! I will now generate the final "
                    "YAML file."
                )

        elif intent == 'tech_query':
            cudo_response = query_cudo_with_spinner(user_input, st.session_state.current_param)
            response_text = (
                "Here's what I found:\n> "
                f"{cudo_response}\nNow, back to the config. "
                f"{generate_question(st.session_state.current_param)}"
            )

        elif intent == 'skip_done':
            response_text = "No problem, we can circle back to that. "
            params_list = sorted(st.session_state.missing_params)
            current_index = params_list.index(st.session_state.current_param)
            st.session_state.current_param = params_list[(current_index + 1) % len(params_list)]
            response_text += generate_question(st.session_state.current_param)

        else:  # general_silly
            response_text = (
                "That's an interesting question! My main goal is to help with this CMM "
                "configuration. Let's get back to it. "
            )
            response_text += generate_question(st.session_state.current_param)

    return response_text


def handle_yaml_generation():
    """Handle final YAML generation when all parameters are collected."""
    if not st.session_state.missing_params and not st.session_state.final_yaml:
        with st.chat_message("assistant"):
            with st.spinner(
                "Generating final YAML from blueprint... "
                "This may take a moment."
            ):
                blueprint_dict = load_yaml_blueprint(BLUEPRINT_PATH)
                if blueprint_dict:
                    from .yaml_parser import merge_yaml_with_llm
                    blueprint_str = yaml.dump(blueprint_dict, sort_keys=False)
                    user_values_str = yaml.dump(
                        st.session_state.collected_values, sort_keys=False
                    )
                    st.session_state.final_yaml = merge_yaml_with_llm(
                        blueprint_str, user_values_str, bedrock_invoke
                    )
                    st.success(
                        "YAML generation complete! You can view and download it on the "
                        "left."
                    )
                    st.rerun()
