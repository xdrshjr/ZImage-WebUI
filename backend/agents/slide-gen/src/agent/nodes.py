"""
LangGraph workflow nodes for slide generation
"""

import logging
from pathlib import Path
from typing import Dict, Any
from src.llm.client import LLMClient
from src.llm.prompts import PromptTemplates
from src.image.generator import ImageGenerator
from src.image.refiner import ImagePromptRefiner
from src.renderer.html_renderer import HTMLRenderer
from src.utils.validators import InputValidator
from src.utils.template_validator import TemplateValidator
from src.utils.config import config

logger = logging.getLogger(__name__)


class SlideGenerationNodes:
    """Collection of node functions for LangGraph workflow"""
    
    def __init__(self):
        """Initialize node dependencies"""
        self.llm_client = LLMClient()
        self.image_generator = ImageGenerator()
        self.image_refiner = ImagePromptRefiner()
        self.html_renderer = HTMLRenderer()
    
    def generate_outline_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node: Generate presentation outline
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with outline
        """
        logger.info("=" * 60)
        logger.info(f"PHASE 1: Generating outline for {state['num_slides']} slides")
        logger.info("=" * 60)
        
        try:
            system_prompt, user_prompt = PromptTemplates.outline_generation_prompt(
                base_text=state['base_text'],
                num_slides=state['num_slides'],
                style=state['style'],
                content_richness=state['content_richness'],
                aspect_ratio=state['aspect_ratio']
            )
            
            response = self.llm_client.generate_json_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            outline = response.get('outline', [])
            
            if len(outline) != state['num_slides']:
                logger.warning(
                    f"Outline length mismatch: expected {state['num_slides']}, got {len(outline)}"
                )
            
            logger.info(f"✓ Outline generated: {len(outline)} slides")
            for entry in outline:
                logger.info(f"  Slide {entry['slide_number']}: {entry['title']}")
            
            return {
                **state,
                'outline': outline,
                'current_slide_index': 0
            }
            
        except Exception as e:
            error_msg = f"Outline generation failed: {str(e)}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
    
    def generate_slide_layout_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node: Generate layout and content for current slide
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with slide layout
        """
        current_idx = state['current_slide_index']
        
        if current_idx >= len(state['outline']):
            logger.info("All slides processed")
            return state
        
        slide_outline = state['outline'][current_idx]
        slide_number = slide_outline['slide_number']
        
        logger.info("=" * 60)
        logger.info(f"PHASE 2: Slide {slide_number}/{state['num_slides']}")
        logger.info(f"Title: {slide_outline['title']}")
        logger.info("=" * 60)
        
        try:
            logger.info(f"→ Step 2.1: Generating layout and content")
            logger.debug(f"Requesting LLM to select appropriate template based on content and slide position")
            
            system_prompt, user_prompt = PromptTemplates.layout_generation_prompt(
                slide_outline=slide_outline,
                style=state['style'],
                content_richness=state['content_richness'],
                aspect_ratio=state['aspect_ratio'],
                slide_number=slide_number,
                total_slides=state['num_slides']
            )
            
            logger.debug(f"LLM prompt emphasizes template variety and position-based selection")
            
            response = self.llm_client.generate_json_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract template selection from LLM response
            llm_selected_template = response.get('template_type', 'title_and_content')
            logger.debug(f"LLM initially selected template: '{llm_selected_template}'")
            
            # Get list of previously used templates for validation
            previous_templates = [slide.get('template_type', '') for slide in state.get('slides', [])]
            
            # Validate and potentially correct template selection
            validated_template = TemplateValidator.validate_and_enforce_template(
                selected_template=llm_selected_template,
                slide_number=slide_number,
                total_slides=state['num_slides'],
                previous_templates=previous_templates,
                slide_title=slide_outline['title']
            )
            
            slide_data = {
                'slide_number': slide_number,
                'template_type': validated_template,
                'layout': response.get('layout', {}),
                'html_path': None,
                'image_path': None
            }
            
            logger.info(f"✓ Layout generated successfully")
            logger.info(f"  Final template: '{validated_template}'")
            logger.info(f"  Content blocks: {len(slide_data['layout'].get('content_blocks', []))}")
            
            # Add slide to state
            state['slides'].append(slide_data)
            
            return state
            
        except Exception as e:
            error_msg = f"Layout generation failed for slide {slide_number}: {str(e)}"
            logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
    
    def generate_images_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node: Generate images for current slide
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with generated images
        """
        current_idx = state['current_slide_index']
        
        if current_idx >= len(state['slides']):
            return state
        
        slide_data = state['slides'][current_idx]
        slide_number = slide_data['slide_number']
        content_blocks = slide_data['layout'].get('content_blocks', [])
        
        # Find image placeholders
        image_blocks = [
            (i, block) for i, block in enumerate(content_blocks)
            if block.get('type') == 'image_placeholder'
        ]
        
        if not image_blocks:
            logger.info(f"  No images needed for slide {slide_number}")
            return state
        
        logger.info(f"→ Step 2.2 & 2.3: Generating {len(image_blocks)} image(s)")
        
        for block_idx, block in image_blocks:
            try:
                raw_prompt = block.get('image_prompt', 'placeholder image')
                position = block.get('position', {})
                width = position.get('width', 800)
                height = position.get('height', 600)
                
                # Refine prompt
                logger.info(f"  Image {block_idx + 1}: Refining prompt...")
                refined_prompt = self.image_refiner.refine_prompt(
                    raw_prompt=raw_prompt,
                    style=state['style'],
                    slide_number=slide_number
                )
                
                # Generate image
                image_filename = f"slide_{slide_number}_img_{block_idx + 1}.png"
                image_path = config.images_dir / image_filename
                
                logger.info(f"  Image {block_idx + 1}: Generating {width}x{height}...")
                success, error = self.image_generator.generate_image(
                    prompt=refined_prompt,
                    width=width,
                    height=height,
                    output_path=image_path
                )
                
                if success:
                    logger.info(f"  ✓ Image {block_idx + 1} generated")
                else:
                    logger.warning(f"  ⚠ Image {block_idx + 1} failed, using placeholder")
                    if error:
                        state['errors'].append(error)
                
                # Update block with image path
                content_blocks[block_idx]['image_path'] = str(image_path)
                
            except Exception as e:
                error_msg = f"Image generation error (slide {slide_number}, block {block_idx}): {str(e)}"
                logger.error(f"  ✗ {error_msg}")
                state['errors'].append(error_msg)
        
        return state
    
    def render_slide_html_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node: Render slide to HTML
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with HTML path
        """
        current_idx = state['current_slide_index']
        
        if current_idx >= len(state['slides']):
            return state
        
        slide_data = state['slides'][current_idx]
        slide_number = slide_data['slide_number']
        
        logger.info(f"→ Step 2.4: Rendering HTML")
        
        try:
            html_path = self.html_renderer.render_slide(
                slide_data=slide_data,
                style=state['style'],
                aspect_ratio=state['aspect_ratio']
            )
            
            # Update slide data
            state['slides'][current_idx]['html_path'] = str(html_path)
            
            logger.info(f"✓ HTML saved: {html_path.name}")
            
        except Exception as e:
            error_msg = f"HTML rendering failed for slide {slide_number}: {str(e)}"
            logger.error(f"✗ {error_msg}")
            state['errors'].append(error_msg)
        
        return state
    
    def increment_slide_index_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node: Move to next slide
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with incremented index
        """
        state['current_slide_index'] += 1
        return state
    
    def should_continue_slides(self, state: Dict[str, Any]) -> str:
        """
        Conditional edge: Check if more slides to process
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node name
        """
        if state['current_slide_index'] < state['num_slides']:
            return "continue"
        else:
            return "finish"

