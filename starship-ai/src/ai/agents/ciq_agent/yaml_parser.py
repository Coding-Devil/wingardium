# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# YAML parsing utilities for CIQ parameter extraction.
import re

import streamlit as st
import yaml

from .config import BLUEPRINT_PATH, PARAM_DESCRIPTIONS


def parse_ciq_params_from_yaml(yaml_path):
    """
    Parses the golden YAML and extracts parameters marked with '# CIQ:' comments.

    Returns a dict: {dot_notation_key: description}
    """
    ciq_params = {}
    with open(yaml_path, 'r') as f:
        lines = f.readlines()

    path_stack = []
    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue

        # Check for CIQ comment
        ciq_match = re.search(r'#\s*CIQ:\s*(.*)$', line)
        if ciq_match:
            description = ciq_match.group(1).strip()
            key_match = re.match(r'^(\s*)([\w\.]+):', line)
            if key_match:
                key = key_match.group(2)
                full_key = ".".join(path_stack + [key])
                ciq_params[full_key] = description

        # Update path stack for nesting (2-space indent assumed)
        indent_match = re.match(r'^(\s*)([\w\.]+):', line)
        if indent_match:
            indent = len(indent_match.group(1))
            key = indent_match.group(2)
            level = indent // 2
            path_stack = path_stack[:level]
            path_stack.append(key)

    return ciq_params


@st.cache_data
def load_yaml_blueprint(path):
    """Load and cache the YAML blueprint file."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error(f"Error: The blueprint file '{path}' was not found.")
        return None


def merge_yaml_with_llm(blueprint_str: str, user_values_str: str, bedrock_invoke_func) -> str:
    """Merge user values into the blueprint YAML using direct merge or LLM fallback."""
    try:
        blueprint_dict = yaml.safe_load(blueprint_str)
        user_values_dict = yaml.safe_load(user_values_str)

        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if (
                    key in base_dict and
                    isinstance(base_dict[key], dict) and
                    isinstance(value, dict)
                ):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value

        deep_update(blueprint_dict, user_values_dict)
        return yaml.dump(blueprint_dict, default_flow_style=False, sort_keys=False, indent=2)
    except Exception as e:
        st.warning(f"Direct YAML merge failed ({str(e)}), using AI assistant...")
        system_prompt = (
            "You are a YAML configuration expert. Merge the user-provided values into the "
            "blueprint YAML. The final output must be the complete, valid YAML, preserving "
            "the original structure, comments, and formatting of the blueprint. Return ONLY "
            "the final, merged YAML content inside a YAML code block."
        )
        user_msg = (
            f"**Blueprint YAML:**\n```yaml\n{blueprint_str}\n```\n"
            f"**User Values to Merge:**\n```yaml\n{user_values_str}\n```"
        )
        response = bedrock_invoke_func(system_prompt, user_msg, max_tokens=4096)
        match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
        return match.group(1) if match else response


# Initialize CIQ schema
try:
    CIQ_SCHEMA = parse_ciq_params_from_yaml(BLUEPRINT_PATH)
    USER_PARAMS = sorted(CIQ_SCHEMA.keys())
except Exception:
    # Fallback to config-based parameters if YAML parsing fails
    CIQ_SCHEMA = PARAM_DESCRIPTIONS
    USER_PARAMS = sorted(PARAM_DESCRIPTIONS.keys())
