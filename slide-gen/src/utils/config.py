"""
Configuration management using environment variables
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration loader and manager"""
    
    def __init__(self):
        """Initialize configuration from .env file"""
        # Load .env file from project root
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(env_path)
        
        # LLM Configuration
        self.llm_api_key: str = os.getenv("LLM_API_KEY", "")
        self.llm_api_url: str = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
        self.llm_model: str = os.getenv("LLM_MODEL", "gpt-4")
        
        # Image Generation Configuration
        self.image_api_key: str = os.getenv("IMAGE_API_KEY", "")
        self.image_api_url: str = os.getenv("IMAGE_API_URL", "")
        self.image_model: str = os.getenv("IMAGE_MODEL", "stable-diffusion-xl")
        
        # Generation Settings
        self.default_timeout: int = int(os.getenv("DEFAULT_TIMEOUT", "60"))
        self.max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
        
        # Output paths
        self.output_dir = Path(__file__).parent.parent.parent / "output"
        self.html_dir = self.output_dir / "html"
        self.images_dir = self.output_dir / "images"
        self.slide_images_dir = self.output_dir / "slide_images"
        
        # Create output directories
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Create necessary output directories"""
        for directory in [self.html_dir, self.images_dir, self.slide_images_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not self.llm_api_key:
            return False, "LLM_API_KEY is required in .env file"
        
        if not self.image_api_key:
            return False, "IMAGE_API_KEY is required in .env file"
        
        if not self.image_api_url:
            return False, "IMAGE_API_URL is required in .env file"
        
        return True, None


# Global config instance
config = Config()

