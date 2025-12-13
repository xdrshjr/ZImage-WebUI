"""
LLM API client for generating slide content
"""

import json
import logging
from typing import Dict, Any, Optional
import requests
from src.utils.config import config

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with OpenAI-compatible LLM APIs"""
    
    def __init__(self):
        """Initialize LLM client with configuration"""
        self.api_key = config.llm_api_key
        self.api_url = config.llm_api_url
        self.model = config.llm_model
        self.timeout = config.default_timeout
        self.max_retries = config.max_retries
    
    def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate completion from LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            response_format: Optional response format (e.g., {"type": "json_object"})
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails after retries
        """
        logger.debug("=" * 50)
        logger.debug("LLM API Request Initiated")
        logger.debug(f"Model: {self.model}")
        logger.debug(f"Temperature: {temperature}")
        logger.debug(f"Max Tokens: {max_tokens}")
        logger.debug(f"Response Format: {response_format}")
        logger.debug(f"System Prompt Length: {len(system_prompt) if system_prompt else 0} chars")
        logger.debug(f"User Prompt Length: {len(prompt)} chars")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            logger.debug("System prompt included in request")
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            payload["response_format"] = response_format
            logger.debug(f"Response format constraint applied: {response_format}")
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM API call attempt {attempt + 1}/{self.max_retries}")
                logger.debug(f"API URL: {self.api_url}")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                logger.debug(f"Response status code: {response.status_code}")
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"✓ LLM response received successfully")
                logger.debug(f"Response length: {len(content)} characters")
                logger.debug(f"Response preview: {content[:150]}..." if len(content) > 150 else f"Response: {content}")
                logger.debug("=" * 50)
                
                return content
                
            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(f"LLM API call timeout (attempt {attempt + 1}/{self.max_retries}): Request exceeded {self.timeout}s timeout")
            except requests.exceptions.HTTPError as e:
                last_error = e
                status_code = e.response.status_code if e.response else "unknown"
                logger.warning(f"LLM API HTTP error (attempt {attempt + 1}/{self.max_retries}): Status {status_code} - {str(e)}")
                if e.response and logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Error response body: {e.response.text[:200]}")
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"LLM API request exception (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
            
            if attempt < self.max_retries - 1:
                backoff_time = 2 ** attempt
                logger.info(f"Retrying in {backoff_time} seconds...")
                import time
                time.sleep(backoff_time)  # Exponential backoff
        
        error_msg = f"LLM API call failed after {self.max_retries} attempts: {str(last_error)}"
        logger.error(error_msg)
        logger.debug("=" * 50)
        raise Exception(error_msg)
    
    def generate_json_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate JSON completion from LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Parsed JSON response
            
        Raises:
            Exception: If API call fails or JSON parsing fails
        """
        logger.debug("Requesting JSON-formatted response from LLM")
        system_prompt = (system_prompt or "") + "\n\nYou must respond with valid JSON only."
        
        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        logger.debug("Attempting to parse LLM response as JSON")
        try:
            parsed_response = json.loads(response)
            logger.info(f"✓ JSON response parsed successfully")
            logger.debug(f"JSON keys: {list(parsed_response.keys())}")
            return parsed_response
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parsing failed: {str(e)}")
            logger.debug(f"Response preview: {response[:200]}...")
            
            # Try to extract JSON from markdown code block
            if "```json" in response:
                logger.debug("Attempting to extract JSON from markdown code block")
                try:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                    parsed_response = json.loads(json_str)
                    logger.info(f"✓ Successfully extracted and parsed JSON from markdown code block")
                    logger.debug(f"JSON keys: {list(parsed_response.keys())}")
                    return parsed_response
                except Exception as extract_error:
                    logger.error(f"Failed to extract JSON from markdown: {str(extract_error)}")
            
            error_msg = f"Failed to parse LLM JSON response: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

