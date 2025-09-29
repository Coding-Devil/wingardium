#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import base64
import json
from typing import Any, Dict, Optional

import requests


class AthenaCuDoClient:
    """Client for interacting with the Athena CuDo API."""

    def __init__(
        self,
        base_url: str = "https://athena-cudo.ati.dyn.tre.nsn-rdnet.net",
        username: str = "poc-mvp-installer",
        password: str = "k0sk!Puisto16",
    ):
        self.base_url = base_url
        self.endpoint = f"{base_url}/generator/generator/v2/chat/"
        self.username = username
        self.password = password

        # Create basic auth header
        auth_string = f"{username}:{password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_b64}'
        }

    def create_payload(
        self,
        message: str,
        model: str = "meta-llama/Llama-3.3-70B-Instruct",
        user_id: str = "4201337",
        chat_id: str = "666",
        max_tokens: int = 8008,
        temperature: float = 0.1,
        system_prompt: str = "",
        indexes: list = None
    ) -> Dict[str, Any]:
        """Create the API request payload."""
        if indexes is None:
            indexes = ["cudo_cloud_mobility_manager_25_7_agora_index"]

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "logit_bias": None,
            "stop": ["<|unk|>", "<|eot_id|>", "<|im_end|>"],
            "stream": False,
            "athena_options": {
                "user_id": user_id,
                "chat_id": chat_id,
                "indexes": indexes,
                "llm_server": "tgi",
                "system_prompt": system_prompt,
                "db_choice": "opensearch",
                "debug": False,
                "use_dense": True,
                "use_sparse": False
            }
        }

        return payload

    def send_message(self, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Send a message to the Athena CuDo API."""
        try:
            payload = self.create_payload(message, **kwargs)
            print(f"Customer Message: {message}")

            # Method 3: Try without authentication (maybe it's not required?)
            response = requests.post(
                self.endpoint,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(
                    f"✅ Response received without auth (Status: {response.status_code})"
                )
                structure = (
                    list(result.keys())
                    if isinstance(result, dict)
                    else 'Not a dict'
                )
                print(f"🔍 Response structure: {type(result)} - {structure}")
                return result

            # If all methods fail, raise the last error
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            # Unified handling for HTTPError, ConnectionError, Timeout, etc.
            status = getattr(getattr(e, 'response', None), 'status_code', None)
            if status:
                print(f"❌ HTTP Error {status}: {e}")
                if status == 403:
                    print(
                        "   Authentication failed (403). "
                        "Check username/password or access permissions."
                    )
                    print(f"   Username used: {self.username}")
                elif status == 401:
                    print(
                        "   Authentication required (401). "
                        "Credentials may be missing or invalid."
                    )
                try:
                    detail = e.response.text
                    if detail:
                        snippet = detail[:500]
                        print(f"   Server response: {snippet}")
                except Exception:
                    pass
            else:
                print(f"❌ Request failed: {e}")
            return None
        except (json.JSONDecodeError, ValueError) as e:
            # JSON decoding error
            print(f"❌ Failed to parse JSON response: {e}")
            return None

    def extract_content(self, response_data: Dict[str, Any]) -> str:
        """Extract content from API response, handling different formats."""
        if not response_data:
            return "No response data"

        # Try different possible response structures
        try:
            # Handle list responses (if response_data is a list)
            if isinstance(response_data, list):
                if len(response_data) > 0:
                    # If it's a list of dicts, try to extract from first item
                    if isinstance(response_data[0], dict):
                        return self.extract_content(response_data[0])
                    else:
                        return str(response_data[0])
                else:
                    return "Empty response list"

            # OpenAI-style format
            if 'choices' in response_data and response_data['choices']:
                choices = response_data['choices']
                if isinstance(choices, list) and len(choices) > 0:
                    choice = choices[0]
                    if isinstance(choice, dict) and 'message' in choice:
                        return choice['message']['content']
                    elif isinstance(choice, dict) and 'text' in choice:
                        return choice['text']

            # Direct content field
            if 'content' in response_data:
                return response_data['content']

            # Message field
            if 'message' in response_data:
                is_dict = isinstance(response_data['message'], dict)
                has_content = 'content' in response_data['message'] if is_dict else False
                if is_dict and has_content:
                    return response_data['message']['content']
                elif isinstance(response_data['message'], str):
                    return response_data['message']

            # Response field
            if 'response' in response_data:
                return response_data['response']

            # Text field
            if 'text' in response_data:
                return response_data['text']

            # Answer field (common in some APIs)
            if 'answer' in response_data:
                return response_data['answer']

            # Data field
            if 'data' in response_data:
                return self.extract_content(response_data['data'])

            # If none of the above, return the whole response as string
            return str(response_data)

        except (KeyError, IndexError, TypeError) as e:
            return f"Error extracting content: {e}\nRaw response: {response_data}"

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format the API response for display."""
        if not response_data:
            return "No response received from Athena API"

        content = self.extract_content(response_data)

        # Add some formatting for better display
        formatted = f"**Nokia/Telecom Information:**\n\n{content}"

        # Add metadata if available
        try:
            if 'usage' in response_data:
                usage = response_data['usage']
                if 'total_tokens' in usage:
                    formatted += f"\n\n*Tokens used: {usage['total_tokens']}*"
        except Exception:
            pass

        return formatted
