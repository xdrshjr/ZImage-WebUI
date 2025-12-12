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
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM API call attempt {attempt + 1}/{self.max_retries}")
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.debug(f"LLM response received: {len(content)} characters")
                return content
                
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"LLM API call failed (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        error_msg = f"LLM API call failed after {self.max_retries} attempts: {str(last_error)}"
        logger.error(error_msg)
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
        system_prompt = (system_prompt or "") + "\n\nYou must respond with valid JSON only."
        
        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response[:200]}...")
            # Try to extract JSON from markdown code block
            if "```json" in response:
                try:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                except:
                    pass
            raise Exception(f"Failed to parse LLM JSON response: {str(e)}")

