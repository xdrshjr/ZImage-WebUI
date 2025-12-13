"""
Image prompt refinement using LLM
"""

import logging
from src.llm.client import LLMClient
from src.llm.prompts import PromptTemplates

logger = logging.getLogger(__name__)


class ImagePromptRefiner:
    """Refines image generation prompts using LLM"""
    
    def __init__(self):
        """Initialize prompt refiner"""
        self.llm_client = LLMClient()
    
    def refine_prompt(self, raw_prompt: str, style: str, slide_number: int) -> str:
        """
        Refine image prompt with artistic and technical details
        
        Args:
            raw_prompt: Original image prompt
            style: Presentation style
            slide_number: Current slide number
            
        Returns:
            Refined prompt string
        """
        logger.info(f"Refining image prompt for slide {slide_number}")
        logger.debug(f"Raw prompt: {raw_prompt}")
        
        try:
            system_prompt, user_prompt = PromptTemplates.image_prompt_refinement(
                raw_prompt=raw_prompt,
                style=style,
                slide_number=slide_number
            )
            
            refined_prompt = self.llm_client.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=500
            )
            
            refined_prompt = refined_prompt.strip()
            logger.debug(f"Refined prompt: {refined_prompt}")
            return refined_prompt
            
        except Exception as e:
            logger.error(f"Prompt refinement failed: {str(e)}")
            # Fallback to original prompt with basic enhancements
            logger.info("Using fallback prompt enhancement")
            return f"{raw_prompt}, high quality, detailed, professional"

