"""
Robust CuDo API Client with comprehensive error handling and retry mechanisms.
Handles 500 internal server errors and other common API issues.
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CudoErrorType(Enum):
    """Enumeration of CuDo API error types"""
    NETWORK_ERROR = "network_error"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "auth_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class CudoResponse:
    """Structured response from CuDo API"""
    success: bool
    content: Optional[str] = None
    error_message: Optional[str] = None
    error_type: Optional[CudoErrorType] = None
    status_code: Optional[int] = None
    raw_response: Optional[Dict[str, Any]] = None


class CudoAPIClient:
    """
    Robust CuDo API client with retry mechanisms and comprehensive error handling.
    """
    
    def __init__(
        self,
        base_url: str = "https://athena-cudo.ati.dyn.tre.nsn-rdnet.net/generator/generator/v2/chat/",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: int = 30,
        user_id: str = "4201337",
        chat_id: str = "cmm_assistant"
    ):
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.user_id = user_id
        self.chat_id = chat_id
        
        # Default headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CMM-Assistant/1.0"
        }
        
        # Default athena options
        self.default_athena_options = {
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "indexes": ["cudo_cloud_mobility_manager_25_7_agora_index"],
            "llm_server": "tgi",
            "db_choice": "opensearch",
            "use_dense": True,
            "use_sparse": False
        }
    
    def _classify_error(self, response: requests.Response, exception: Optional[Exception] = None) -> CudoErrorType:
        """Classify the type of error based on response or exception"""
        if exception:
            if isinstance(exception, requests.exceptions.Timeout):
                return CudoErrorType.TIMEOUT_ERROR
            elif isinstance(exception, requests.exceptions.ConnectionError):
                return CudoErrorType.NETWORK_ERROR
            elif isinstance(exception, requests.exceptions.RequestException):
                return CudoErrorType.NETWORK_ERROR
            else:
                return CudoErrorType.UNKNOWN_ERROR
        
        if response:
            if response.status_code == 401 or response.status_code == 403:
                return CudoErrorType.AUTHENTICATION_ERROR
            elif response.status_code == 429:
                return CudoErrorType.RATE_LIMIT_ERROR
            elif 400 <= response.status_code < 500:
                return CudoErrorType.CLIENT_ERROR
            elif 500 <= response.status_code < 600:
                return CudoErrorType.SERVER_ERROR
        
        return CudoErrorType.UNKNOWN_ERROR
    
    def _should_retry(self, error_type: CudoErrorType, attempt: int) -> bool:
        """Determine if we should retry based on error type and attempt number"""
        if attempt >= self.max_retries:
            return False
        
        # Retry on server errors, network errors, and timeouts
        retry_on = {
            CudoErrorType.SERVER_ERROR,
            CudoErrorType.NETWORK_ERROR,
            CudoErrorType.TIMEOUT_ERROR,
            CudoErrorType.RATE_LIMIT_ERROR
        }
        
        return error_type in retry_on
    
    def _calculate_retry_delay(self, attempt: int, error_type: CudoErrorType) -> float:
        """Calculate retry delay with exponential backoff"""
        base_delay = self.retry_delay
        
        # Longer delay for rate limiting
        if error_type == CudoErrorType.RATE_LIMIT_ERROR:
            base_delay *= 5
        
        # Exponential backoff: delay = base_delay * (2 ^ attempt)
        return base_delay * (2 ** attempt)
    
    def _build_payload(
        self,
        query: str,
        model: str = "meta-llama/Llama-3.3-70B-Instruct",
        max_tokens: int = 500,
        stream: bool = False,
        custom_athena_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build the API payload"""
        athena_options = self.default_athena_options.copy()
        if custom_athena_options:
            athena_options.update(custom_athena_options)
        
        return {
            "model": model,
            "messages": [{"role": "user", "content": query}],
            "max_tokens": max_tokens,
            "stream": stream,
            "athena_options": athena_options
        }
    
    def _parse_response(self, response_data: Union[Dict, list]) -> str:
        """Parse the API response and extract content"""
        try:
            # Handle list response (as in your original code)
            if isinstance(response_data, list) and len(response_data) > 0:
                first_item = response_data[0]
                if 'choices' in first_item and len(first_item['choices']) > 0:
                    choice = first_item['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        return choice['message']['content']
            
            # Handle direct dict response
            elif isinstance(response_data, dict):
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    choice = response_data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        return choice['message']['content']
                
                # Handle other possible response formats
                if 'content' in response_data:
                    return response_data['content']
                if 'text' in response_data:
                    return response_data['text']
            
            # If we can't parse the expected format, return a descriptive error
            logger.warning(f"Unexpected response format: {response_data}")
            return "I received a response from CuDo, but it was in an unexpected format. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Error parsing CuDo response: {e}")
            return f"Error parsing the response from CuDo: {str(e)}"
    
    def query(
        self,
        query: str,
        model: str = "meta-llama/Llama-3.3-70B-Instruct",
        max_tokens: int = 500,
        custom_athena_options: Optional[Dict[str, Any]] = None
    ) -> CudoResponse:
        """
        Query the CuDo API with robust error handling and retry logic.
        
        Args:
            query: The question/query to send to CuDo
            model: The LLM model to use
            max_tokens: Maximum tokens in response
            custom_athena_options: Custom athena options to override defaults
            
        Returns:
            CudoResponse object with success status and content/error information
        """
        payload = self._build_payload(query, model, max_tokens, False, custom_athena_options)
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"CuDo API attempt {attempt + 1}/{self.max_retries + 1} for query: {query[:50]}...")
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    data=json.dumps(payload),
                    verify=False,
                    timeout=self.timeout
                )
                
                # Log response details for debugging
                logger.info(f"CuDo API response status: {response.status_code}")
                
                # Handle successful response
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        content = self._parse_response(response_data)
                        
                        return CudoResponse(
                            success=True,
                            content=content,
                            status_code=response.status_code,
                            raw_response=response_data
                        )
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        return CudoResponse(
                            success=False,
                            error_message=f"Invalid JSON response from CuDo API: {str(e)}",
                            error_type=CudoErrorType.SERVER_ERROR,
                            status_code=response.status_code
                        )
                
                # Handle error responses
                error_type = self._classify_error(response)
                error_message = f"CuDo API returned status {response.status_code}"
                
                # Try to get error details from response
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_message += f": {error_data['error']}"
                    elif 'message' in error_data:
                        error_message += f": {error_data['message']}"
                except:
                    # If we can't parse error response, use the text
                    if response.text:
                        error_message += f": {response.text[:200]}"
                
                logger.warning(f"CuDo API error: {error_message}")
                
                # Check if we should retry
                if self._should_retry(error_type, attempt):
                    delay = self._calculate_retry_delay(attempt, error_type)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    return CudoResponse(
                        success=False,
                        error_message=error_message,
                        error_type=error_type,
                        status_code=response.status_code
                    )
                    
            except requests.exceptions.Timeout:
                error_type = CudoErrorType.TIMEOUT_ERROR
                error_message = f"CuDo API request timed out after {self.timeout} seconds"
                logger.warning(error_message)
                
            except requests.exceptions.ConnectionError as e:
                error_type = CudoErrorType.NETWORK_ERROR
                error_message = f"Failed to connect to CuDo API: {str(e)}"
                logger.warning(error_message)
                
            except requests.exceptions.RequestException as e:
                error_type = CudoErrorType.NETWORK_ERROR
                error_message = f"CuDo API request failed: {str(e)}"
                logger.warning(error_message)
                
            except Exception as e:
                error_type = CudoErrorType.UNKNOWN_ERROR
                error_message = f"Unexpected error during CuDo API call: {str(e)}"
                logger.error(error_message)
            
            # Check if we should retry for exceptions
            if self._should_retry(error_type, attempt):
                delay = self._calculate_retry_delay(attempt, error_type)
                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                break
        
        # If we've exhausted all retries
        return CudoResponse(
            success=False,
            error_message=error_message,
            error_type=error_type
        )
    
    def query_simple(self, query: str) -> str:
        """
        Simple query method that returns just the content string.
        This maintains compatibility with existing code.
        
        Args:
            query: The question to ask CuDo
            
        Returns:
            String response from CuDo or error message
        """
        response = self.query(query)
        
        if response.success:
            return response.content
        else:
            # Return user-friendly error messages
            if response.error_type == CudoErrorType.NETWORK_ERROR:
                return "I'm having trouble connecting to the CuDo knowledge base. Please check your internet connection and try again."
            elif response.error_type == CudoErrorType.SERVER_ERROR:
                return "The CuDo knowledge base is currently experiencing issues (server error). Please try again in a few moments."
            elif response.error_type == CudoErrorType.TIMEOUT_ERROR:
                return "The CuDo knowledge base is taking too long to respond. Please try a simpler question or try again later."
            elif response.error_type == CudoErrorType.AUTHENTICATION_ERROR:
                return "There's an authentication issue with the CuDo knowledge base. Please contact your administrator."
            elif response.error_type == CudoErrorType.RATE_LIMIT_ERROR:
                return "Too many requests to CuDo. Please wait a moment before asking another question."
            else:
                return f"I encountered an issue while querying the CuDo knowledge base: {response.error_message}"


# Create a default client instance for easy use
default_cudo_client = CudoAPIClient()


def query_cudo_api(query: str) -> str:
    """
    Backward-compatible function that uses the robust CuDo client.
    This can be used as a drop-in replacement for the original function.
    """
    return default_cudo_client.query_simple(query)


# Example usage and testing
if __name__ == "__main__":
    # Test the CuDo client
    client = CudoAPIClient()
    
    test_queries = [
        "What are the deployment parameters of CMM?",
        "How do I configure the NRF endpoint?",
        "What is the purpose of the ALMS container?"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        result = client.query(query)
        
        if result.success:
            print(f"✅ Success: {result.content[:100]}...")
        else:
            print(f"❌ Error ({result.error_type}): {result.error_message}")
