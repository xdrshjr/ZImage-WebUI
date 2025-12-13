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
        logger.debug(f"Style: {style}")
        logger.debug(f"Raw prompt length: {len(raw_prompt)} chars")
        if logger.isEnabledFor(logging.DEBUG):
            prompt_preview = raw_prompt[:100] + "..." if len(raw_prompt) > 100 else raw_prompt
            logger.debug(f"Raw prompt: {prompt_preview}")
        
        try:
            logger.debug("Preparing LLM prompts for image prompt refinement")
            system_prompt, user_prompt = PromptTemplates.image_prompt_refinement(
                raw_prompt=raw_prompt,
                style=style,
                slide_number=slide_number
            )
            
            logger.debug("Requesting LLM to enhance image prompt with professional details")
            refined_prompt = self.llm_client.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=500
            )
            
            refined_prompt = refined_prompt.strip()
            logger.info(f"✓ Image prompt refined successfully")
            logger.debug(f"Refined prompt length: {len(refined_prompt)} chars")
            if logger.isEnabledFor(logging.DEBUG):
                refined_preview = refined_prompt[:120] + "..." if len(refined_prompt) > 120 else refined_prompt
                logger.debug(f"Refined prompt: {refined_preview}")
            
            return refined_prompt
            
        except Exception as e:
            logger.error(f"Prompt refinement failed: {str(e)}", exc_info=True)
            # Fallback to original prompt with basic enhancements
            logger.warning("Using fallback prompt enhancement (adding basic quality modifiers)")
            fallback = f"{raw_prompt}, high quality, detailed, professional, 4K, sharp focus"
            logger.debug(f"Fallback prompt: {fallback}")
            return fallback

