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
        logger.debug(f"Outline generation parameters - Style: {state['style']}, Content Richness: {state['content_richness']}, Aspect Ratio: {state['aspect_ratio']}")
        
        try:
            logger.debug("Preparing LLM prompts for outline generation with rich content requirements")
            system_prompt, user_prompt = PromptTemplates.outline_generation_prompt(
                base_text=state['base_text'],
                num_slides=state['num_slides'],
                style=state['style'],
                content_richness=state['content_richness'],
                aspect_ratio=state['aspect_ratio']
            )
            
            logger.info("→ Requesting LLM to generate comprehensive outline with detailed key points")
            logger.debug(f"System prompt length: {len(system_prompt)} chars, User prompt length: {len(user_prompt)} chars")
            
            response = self.llm_client.generate_json_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            outline = response.get('outline', [])
            
            if len(outline) != state['num_slides']:
                logger.warning(
                    f"Outline length mismatch: expected {state['num_slides']}, got {len(outline)}. This may affect presentation structure."
                )
            else:
                logger.debug(f"Outline length matches expected slide count: {len(outline)}")
            
            logger.info(f"✓ Outline generated successfully: {len(outline)} slides")
            for i, entry in enumerate(outline, 1):
                logger.info(f"  Slide {entry['slide_number']}: {entry['title']}")
                sections = entry.get('sections', entry.get('key_points', []))
                if isinstance(sections, list) and sections:
                    if isinstance(sections[0], dict):
                        # New format with sections
                        logger.debug(f"    - Sections count: {len(sections)}")
                        if logger.isEnabledFor(logging.DEBUG):
                            for j, section in enumerate(sections[:2], 1):
                                section_title = section.get('section_title', 'Untitled')
                                bullet_count = len(section.get('bullet_points', []))
                                logger.debug(f"      Section {j}: {section_title} ({bullet_count} bullets)")
                    else:
                        # Old format with key_points
                        logger.debug(f"    - Key points count: {len(sections)}")
                        if logger.isEnabledFor(logging.DEBUG):
                            for j, point in enumerate(sections[:3], 1):
                                preview = point[:80] + "..." if len(point) > 80 else point
                                logger.debug(f"      Point {j}: {preview}")
            
            return {
                **state,
                'outline': outline,
                'current_slide_index': 0
            }
            
        except Exception as e:
            error_msg = f"Outline generation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
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
            logger.info("All slides processed, moving to final stages")
            return state
        
        slide_outline = state['outline'][current_idx]
        slide_number = slide_outline['slide_number']
        
        logger.info("=" * 60)
        logger.info(f"PHASE 2: Slide {slide_number}/{state['num_slides']}")
        logger.info(f"Title: {slide_outline['title']}")
        logger.info("=" * 60)
        sections = slide_outline.get('sections', slide_outline.get('key_points', []))
        if isinstance(sections, list) and sections and isinstance(sections[0], dict):
            logger.debug(f"Slide outline contains {len(sections)} sections with structured content")
        else:
            logger.debug(f"Slide outline contains {len(sections)} key points")
        
        try:
            logger.info(f"→ Step 2.1: Generating layout and rich content for slide {slide_number}")
            logger.debug(f"Requesting LLM to analyze content and select appropriate template based on:")
            logger.debug(f"  - Content type and structure")
            logger.debug(f"  - Slide position: {slide_number}/{state['num_slides']}")
            logger.debug(f"  - Previous templates used for variety")
            
            system_prompt, user_prompt = PromptTemplates.layout_generation_prompt(
                slide_outline=slide_outline,
                style=state['style'],
                content_richness=state['content_richness'],
                aspect_ratio=state['aspect_ratio'],
                slide_number=slide_number,
                total_slides=state['num_slides']
            )
            
            logger.debug(f"LLM prompt emphasizes template variety, position-based selection, and proper image margins")
            logger.debug(f"Content richness level: {state['content_richness']}")
            
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
            logger.debug(f"Previously used templates: {previous_templates}")
            
            # Validate and potentially correct template selection
            validated_template = TemplateValidator.validate_and_enforce_template(
                selected_template=llm_selected_template,
                slide_number=slide_number,
                total_slides=state['num_slides'],
                previous_templates=previous_templates,
                slide_title=slide_outline['title']
            )
            
            if validated_template != llm_selected_template:
                logger.info(f"  Template adjusted by validator: '{llm_selected_template}' → '{validated_template}'")
            
            slide_data = {
                'slide_number': slide_number,
                'template_type': validated_template,
                'layout': response.get('layout', {}),
                'html_path': None,
                'image_path': None
            }
            
            content_blocks = slide_data['layout'].get('content_blocks', [])
            logger.info(f"✓ Layout generated successfully")
            logger.info(f"  Final template: '{validated_template}'")
            logger.info(f"  Content blocks: {len(content_blocks)}")
            
            # Log content block details at debug level
            if logger.isEnabledFor(logging.DEBUG):
                for i, block in enumerate(content_blocks, 1):
                    block_type = block.get('type', 'unknown')
                    position = block.get('position', {})
                    logger.debug(f"  Block {i}: type={block_type}, pos=({position.get('x', 0)}, {position.get('y', 0)}), size=({position.get('width', 0)}x{position.get('height', 0)})")
                    if block_type == 'text':
                        content_preview = block.get('content', '')[:60] + "..." if len(block.get('content', '')) > 60 else block.get('content', '')
                        logger.debug(f"    Content preview: {content_preview}")
                    elif block_type == 'image_placeholder':
                        prompt_preview = block.get('image_prompt', '')[:60] + "..." if len(block.get('image_prompt', '')) > 60 else block.get('image_prompt', '')
                        logger.debug(f"    Image prompt preview: {prompt_preview}")
            
            # Add slide to state
            state['slides'].append(slide_data)
            
            return state
            
        except Exception as e:
            error_msg = f"Layout generation failed for slide {slide_number}: {str(e)}"
            logger.error(error_msg, exc_info=True)
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
            logger.debug("No more slides to process for image generation")
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
            logger.info(f"  No images needed for slide {slide_number} - text-only layout")
            return state
        
        logger.info(f"→ Step 2.2 & 2.3: Generating {len(image_blocks)} image(s) for slide {slide_number}")
        logger.debug(f"Image generation style: {state['style']}")
        
        for block_idx, block in image_blocks:
            try:
                raw_prompt = block.get('image_prompt', 'placeholder image')
                position = block.get('position', {})
                width = position.get('width', 800)
                height = position.get('height', 600)
                x_pos = position.get('x', 0)
                y_pos = position.get('y', 0)
                
                logger.debug(f"  Image {block_idx + 1} details:")
                logger.debug(f"    - Position: ({x_pos}, {y_pos})")
                logger.debug(f"    - Dimensions: {width}x{height}")
                logger.debug(f"    - Raw prompt length: {len(raw_prompt)} chars")
                
                # Refine prompt
                logger.info(f"  Image {block_idx + 1}: Refining prompt for professional quality...")
                refined_prompt = self.image_refiner.refine_prompt(
                    raw_prompt=raw_prompt,
                    style=state['style'],
                    slide_number=slide_number
                )
                logger.debug(f"    - Refined prompt length: {len(refined_prompt)} chars")
                if logger.isEnabledFor(logging.DEBUG):
                    prompt_preview = refined_prompt[:100] + "..." if len(refined_prompt) > 100 else refined_prompt
                    logger.debug(f"    - Refined prompt preview: {prompt_preview}")
                
                # Generate image
                image_filename = f"slide_{slide_number}_img_{block_idx + 1}.png"
                image_path = config.images_dir / image_filename
                
                logger.info(f"  Image {block_idx + 1}: Generating {width}x{height} image...")
                logger.debug(f"    - Output path: {image_path}")
                
                success, error = self.image_generator.generate_image(
                    prompt=refined_prompt,
                    width=width,
                    height=height,
                    output_path=image_path
                )
                
                if success:
                    logger.info(f"  ✓ Image {block_idx + 1} generated successfully")
                    logger.debug(f"    - Saved to: {image_filename}")
                else:
                    logger.warning(f"  ⚠ Image {block_idx + 1} generation failed, using placeholder")
                    if error:
                        logger.error(f"    - Error details: {error}")
                        state['errors'].append(error)
                
                # Update block with image path
                content_blocks[block_idx]['image_path'] = str(image_path)
                logger.debug(f"    - Image path updated in content block")
                
            except Exception as e:
                error_msg = f"Image generation error (slide {slide_number}, block {block_idx}): {str(e)}"
                logger.error(f"  ✗ {error_msg}", exc_info=True)
                state['errors'].append(error_msg)
        
        logger.info(f"✓ Completed image generation for slide {slide_number}")
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
            logger.debug("No more slides to render to HTML")
            return state
        
        slide_data = state['slides'][current_idx]
        slide_number = slide_data['slide_number']
        template_type = slide_data.get('template_type', 'unknown')
        
        logger.info(f"→ Step 2.4: Rendering HTML for slide {slide_number}")
        logger.debug(f"  Template type: {template_type}")
        logger.debug(f"  Style: {state['style']}")
        logger.debug(f"  Aspect ratio: {state['aspect_ratio']}")
        
        try:
            html_path = self.html_renderer.render_slide(
                slide_data=slide_data,
                style=state['style'],
                aspect_ratio=state['aspect_ratio']
            )
            
            # Update slide data
            state['slides'][current_idx]['html_path'] = str(html_path)
            
            logger.info(f"✓ HTML saved: {html_path.name}")
            logger.debug(f"  Full path: {html_path}")
            
        except Exception as e:
            error_msg = f"HTML rendering failed for slide {slide_number}: {str(e)}"
            logger.error(f"✗ {error_msg}", exc_info=True)
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
        old_index = state['current_slide_index']
        state['current_slide_index'] += 1
        logger.debug(f"Incremented slide index: {old_index} → {state['current_slide_index']}")
        return state
    
    def should_continue_slides(self, state: Dict[str, Any]) -> str:
        """
        Conditional edge: Check if more slides to process
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node name
        """
        current = state['current_slide_index']
        total = state['num_slides']
        
        if current < total:
            logger.debug(f"Continuing to next slide: {current + 1}/{total}")
            return "continue"
        else:
            logger.info(f"All {total} slides processed, proceeding to finalization")
            return "finish"

