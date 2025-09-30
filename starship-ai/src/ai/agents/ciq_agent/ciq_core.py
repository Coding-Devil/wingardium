# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# Core CIQ Agent logic for parameter collection and chat processing
#

from typing import Dict, Optional

import yaml

from .config import BLUEPRINT_PATH, PARAM_DESCRIPTIONS
from .cudo_client import query_cudo_api
from .session_manager import CIQSession, session_manager
from .yaml_parser import load_yaml_blueprint


class CIQAgent:
    """Core CIQ Agent for handling chat interactions and parameter collection."""

    def __init__(self):
        self.session_manager = session_manager

    def process_chat_message(self, user_input: str, session_id: Optional[str] = None) -> Dict:
        """
        Process a chat message and return response with session state.

        Args:
            user_input: User's input message
            session_id: Optional session ID, creates new if None

        Returns:
            Dict containing response, session_id, and session state
        """
        # Get or create session
        session_id, session = self.session_manager.get_or_create_session(session_id)

        # Add user message to history
        session.add_message("user", user_input)

        # Process input and generate response
        response_text = self._generate_response(user_input, session)

        # Add assistant response to history
        session.add_message("assistant", response_text)

        # Update session in manager
        self.session_manager.update_session(session_id, session)
        return {
            "response": response_text,
            "session_id": session_id,
            "progress": session.get_progress(),
            "is_complete": session.is_complete,
            "final_yaml": session.final_yaml
        }

    def _generate_response(self, user_input: str, session: CIQSession) -> str:
        """Generate appropriate response based on user input and session state."""
        if session.is_complete:
            return self._handle_completed_session(user_input, session)

        if not session.current_param:
            return "All parameters have been collected! Generating final YAML..."

        # Classify user intent
        intent = self._classify_intent(user_input, session.current_param)
        if intent == 'param_answer':
            return self._handle_parameter_answer(user_input, session)
        elif intent == 'tech_query':
            return self._handle_technical_query(user_input, session)
        elif intent == 'skip_done':
            return self._handle_skip_parameter(session)
        else:  # general_silly
            return self._handle_general_query(user_input, session)

    def _classify_intent(self, user_input: str, current_param: str) -> str:
        """Classify user input intent using simple heuristics."""
        user_lower = user_input.lower().strip()

        # Check for skip/done patterns
        skip_patterns = ['skip', 'next', 'done', 'later', 'pass']
        if any(pattern in user_lower for pattern in skip_patterns):
            return 'skip_done'

        # Check for technical query patterns
        tech_patterns = ['what is', 'how do', 'explain', 'help', 'configure', 'setup']
        if any(pattern in user_lower for pattern in tech_patterns):
            return 'tech_query'

        # Check if it looks like a parameter value (not a question)
        question_patterns = ['?', 'what', 'how', 'why', 'when', 'where']
        if not any(pattern in user_lower for pattern in question_patterns):
            return 'param_answer'
        return 'general_silly'

    def _handle_parameter_answer(self, user_input: str, session: CIQSession) -> str:
        """Handle when user provides a parameter value."""
        current_param = session.current_param
        session.collect_parameter(current_param, user_input)

        response = "Great! I've recorded that value. "

        if session.missing_params:
            next_param = session.current_param
            response += self._generate_question(next_param)
        else:
            response += "All parameters collected! Generating your deployment YAML..."
            session.final_yaml = self._generate_final_yaml(session)
        return response

    def _handle_technical_query(self, user_input: str, session: CIQSession) -> str:
        """Handle technical questions using CuDo API."""
        current_param = session.current_param

        # Add context to the query
        contextual_query = (
            f"Context: I'm configuring the CMM parameter '{current_param}' "
            f"which is: {PARAM_DESCRIPTIONS.get(current_param, '')}\n\n"
            f"User Question: {user_input}\n\n"
            f"Please provide relevant information about this parameter or "
            f"answer the user's question in the context of CMM deployment "
            f"configuration."
        )
        try:
            cudo_response = query_cudo_api(contextual_query)
            response = (
                f"Here's what I found:\n\n{cudo_response}\n\n"
                f"Now, back to the configuration. "
                f"{self._generate_question(current_param)}"
            )
        except Exception:
            response = (
                f"I couldn't retrieve information right now. "
                f"Let's continue with the configuration. "
                f"{self._generate_question(current_param)}"
            )
        return response

    def _handle_skip_parameter(self, session: CIQSession) -> str:
        """Handle when user wants to skip current parameter."""
        if len(session.missing_params) <= 1:
            return (
                "This is the last parameter we need. "
                "Could you please provide a value for it?"
            )

        # Move to next parameter
        params_list = sorted(session.missing_params)
        current_index = params_list.index(session.current_param)
        session.current_param = params_list[(current_index + 1) % len(params_list)]

        return (
            f"No problem, we can come back to that later. "
            f"{self._generate_question(session.current_param)}"
        )

    def _handle_general_query(self, user_input: str, session: CIQSession) -> str:
        """Handle general queries or off-topic questions."""
        return (
            f"That's an interesting question! My main focus is helping you "
            f"configure CMM deployment parameters. Let's get back to it. "
            f"{self._generate_question(session.current_param)}"
        )

    def _handle_completed_session(self, user_input: str, session: CIQSession) -> str:
        """Handle messages after all parameters are collected."""
        if 'regenerate' in user_input.lower() or 'generate again' in user_input.lower():
            session.final_yaml = self._generate_final_yaml(session)
            return "I've regenerated the YAML configuration for you!"

        return (
            "All parameters have been collected and your YAML is ready! "
            "You can download it or ask me to regenerate it if needed."
        )

    def _generate_question(self, param: str) -> str:
        """Generate a friendly question for a parameter."""
        description = PARAM_DESCRIPTIONS.get(param, "")
        param_display = param.replace("global.", "").replace(".", " ")

        return (
            f"What value would you like to set for **{param_display}**? "
            f"({description})"
        )

    def _generate_final_yaml(self, session: CIQSession) -> str:
        """Generate final YAML configuration from collected parameters."""
        try:
            # Load blueprint
            blueprint_dict = load_yaml_blueprint(str(BLUEPRINT_PATH))
            if not blueprint_dict:
                return "Error: Could not load YAML blueprint."

            # Convert collected values to nested dict structure
            nested_values = self._convert_to_nested_dict(session.collected_values)

            # Merge values into blueprint
            merged_dict = self._deep_merge(blueprint_dict, nested_values)

            # Convert back to YAML string
            return yaml.dump(
                merged_dict,
                default_flow_style=False,
                sort_keys=False,
                indent=2
            )
        except Exception as e:
            return f"Error generating YAML: {str(e)}"

    def _convert_to_nested_dict(self, flat_dict: Dict[str, str]) -> Dict:
        """Convert flat dot-notation dict to nested dict."""
        result = {}
        for key, value in flat_dict.items():
            parts = key.split('.')
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        return result

    def _deep_merge(self, base_dict: Dict, update_dict: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base_dict.copy()
        for key, value in update_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get_session_progress(self, session_id: str) -> Optional[Dict]:
        """Get progress information for a session."""
        session = self.session_manager.get_session(session_id)
        if not session:
            return None

        return session.get_progress()

    def get_parameters_schema(self) -> Dict[str, Dict]:
        """Get the full parameters schema for payload generation."""
        schema = {}
        for param, description in PARAM_DESCRIPTIONS.items():
            # Convert dot notation to field name for API compatibility
            field_name = param.replace("global.", "").replace(".", "_")
            schema[field_name] = {
                "type": "string",
                "x-displayName": description,
                "x-order": 1,
                "original_param": param
            }
        return schema


# Global CIQ agent instance
ciq_agent = CIQAgent()
