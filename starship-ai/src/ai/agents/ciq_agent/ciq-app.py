# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# CMM Deployment Assistant - Main Application Entry Point
#
# This is the main Streamlit application that orchestrates the CMM deployment
# configuration process using modular components.
#
import streamlit as st
from streamlit_ui import (
    handle_yaml_generation, initialize_session_state, render_chat_panel, render_progress_panel,
    setup_page_config)


def main():
    # Main application function.
    # Set up page configuration and styling
    setup_page_config()

    # Initialize session state
    initialize_session_state()

    # Create main layout with two columns
    col1, col2 = st.columns([1, 1])

    # Left Column: Progress and Parameters
    with col1:
        render_progress_panel()

    # Right Column: Chat Interface
    with col2:
        render_chat_panel()

    # Handle YAML generation when all parameters are collected
    handle_yaml_generation()


if __name__ == "__main__":
    main()
