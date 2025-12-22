"""
Template selection validator for ensuring diverse slide layouts
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class TemplateValidator:
    """Validates and enforces template selection rules for slide generation"""
    
    # Valid template types
    VALID_TEMPLATES = [
        'title_and_content', 'two_column', 'image_focus',
        'xiaohongshu_minimal', 'xiaohongshu_fashion', 
        'xiaohongshu_mixed', 'xiaohongshu_bold'
    ]
    
    # Xiaohongshu templates (for 3:4 aspect ratio)
    XIAOHONGSHU_TEMPLATES = [
        'xiaohongshu_minimal', 'xiaohongshu_fashion',
        'xiaohongshu_mixed', 'xiaohongshu_bold'
    ]
    
    # Default template if validation fails
    DEFAULT_TEMPLATE = 'title_and_content'
    
    @staticmethod
    def validate_and_enforce_template(
        selected_template: str,
        slide_number: int,
        total_slides: int,
        previous_templates: List[str],
        slide_title: str,
        aspect_ratio: Optional[str] = None
    ) -> str:
        """
        Validate and potentially override template selection to ensure diversity
        
        Args:
            selected_template: Template selected by LLM
            slide_number: Current slide number (1-indexed)
            total_slides: Total number of slides
            previous_templates: List of templates used in previous slides
            slide_title: Title of current slide for logging
            aspect_ratio: Aspect ratio (e.g., "3:4", "16:9") - used for template recommendations
            
        Returns:
            Validated and potentially corrected template type
        """
        original_template = selected_template
        
        # Step 0: Special handling for 3:4 aspect ratio - prefer Xiaohongshu templates
        if aspect_ratio == "3:4":
            logger.debug(f"Slide {slide_number}: 3:4 aspect ratio detected - prioritizing Xiaohongshu templates")
            # If LLM selected a non-xiaohongshu template, suggest a xiaohongshu one
            if selected_template not in TemplateValidator.XIAOHONGSHU_TEMPLATES:
                # Check if any xiaohongshu template was used before
                used_xiaohongshu = [t for t in previous_templates if t in TemplateValidator.XIAOHONGSHU_TEMPLATES]
                if used_xiaohongshu:
                    # Use a different xiaohongshu template for variety
                    available = [t for t in TemplateValidator.XIAOHONGSHU_TEMPLATES if t not in used_xiaohongshu[-2:]]
                    if available:
                        selected_template = available[0]
                        logger.info(
                            f"Slide {slide_number}: 3:4 aspect ratio - switched to Xiaohongshu template "
                            f"'{selected_template}' (was '{original_template}')"
                        )
                    else:
                        # All xiaohongshu templates used recently, use the least recent one
                        selected_template = TemplateValidator.XIAOHONGSHU_TEMPLATES[0]
                        logger.info(
                            f"Slide {slide_number}: 3:4 aspect ratio - using Xiaohongshu template "
                            f"'{selected_template}' for variety"
                        )
                else:
                    # First xiaohongshu template, use minimal as default
                    selected_template = 'xiaohongshu_minimal'
                    logger.info(
                        f"Slide {slide_number}: 3:4 aspect ratio - using Xiaohongshu template "
                        f"'{selected_template}' (was '{original_template}')"
                    )
        
        # Step 1: Validate template is one of the allowed types
        if selected_template not in TemplateValidator.VALID_TEMPLATES:
            logger.warning(
                f"Slide {slide_number}: Invalid template '{selected_template}', "
                f"defaulting to '{TemplateValidator.DEFAULT_TEMPLATE}'"
            )
            selected_template = TemplateValidator.DEFAULT_TEMPLATE
        
        # Step 2: Enforce first slide rule
        if slide_number == 1 and selected_template != 'title_and_content':
            logger.info(
                f"Slide 1: Enforcing 'title_and_content' template for introduction "
                f"(LLM selected '{selected_template}')"
            )
            selected_template = 'title_and_content'
        
        # Step 3: Check for excessive repetition (3+ consecutive same templates)
        if len(previous_templates) >= 2:
            last_two = previous_templates[-2:]
            if (last_two[0] == last_two[1] == selected_template and
                selected_template == 'title_and_content'):
                # Too many title_and_content in a row, force diversity
                alternative_templates = [t for t in TemplateValidator.VALID_TEMPLATES 
                                       if t != selected_template]
                # Prefer two_column over image_focus for middle slides
                selected_template = alternative_templates[0] if slide_number < total_slides else 'image_focus'
                logger.warning(
                    f"Slide {slide_number}: Detected 3+ consecutive '{original_template}' templates. "
                    f"Enforcing diversity by switching to '{selected_template}'"
                )
        
        # Step 4: Encourage image_focus for last slide if appropriate
        if slide_number == total_slides and selected_template == 'title_and_content':
            if 'conclusion' in slide_title.lower() or 'summary' in slide_title.lower():
                logger.debug(
                    f"Slide {slide_number}: Last slide uses '{selected_template}' "
                    f"(could consider 'image_focus' for more impact)"
                )
        
        # Log the final decision
        if selected_template != original_template:
            logger.info(
                f"Slide {slide_number} ({slide_title}): Template corrected from "
                f"'{original_template}' to '{selected_template}'"
            )
        else:
            logger.info(
                f"Slide {slide_number} ({slide_title}): Template '{selected_template}' validated"
            )
        
        return selected_template
    
    @staticmethod
    def log_template_distribution(slides: List[Dict[str, Any]]) -> None:
        """
        Log the distribution of templates across all slides
        
        Args:
            slides: List of slide data dictionaries
        """
        if not slides:
            return
        
        template_counts = {
            'title_and_content': 0,
            'two_column': 0,
            'image_focus': 0,
            'xiaohongshu_minimal': 0,
            'xiaohongshu_fashion': 0,
            'xiaohongshu_mixed': 0,
            'xiaohongshu_bold': 0
        }
        
        template_sequence = []
        
        for slide in slides:
            template = slide.get('template_type', 'unknown')
            template_sequence.append(template)
            if template in template_counts:
                template_counts[template] += 1
        
        logger.info("=" * 60)
        logger.info("TEMPLATE DISTRIBUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total slides: {len(slides)}")
        logger.info(f"Template usage:")
        
        # Group templates for better readability
        standard_templates = ['title_and_content', 'two_column', 'image_focus']
        xiaohongshu_templates = ['xiaohongshu_minimal', 'xiaohongshu_fashion', 'xiaohongshu_mixed', 'xiaohongshu_bold']
        
        # Log standard templates
        standard_count = 0
        for template in standard_templates:
            count = template_counts.get(template, 0)
            if count > 0:
                percentage = (count / len(slides)) * 100 if slides else 0
                logger.info(f"  - {template}: {count} slides ({percentage:.1f}%)")
                standard_count += count
        
        # Log xiaohongshu templates
        xiaohongshu_count = 0
        for template in xiaohongshu_templates:
            count = template_counts.get(template, 0)
            if count > 0:
                percentage = (count / len(slides)) * 100 if slides else 0
                logger.info(f"  - {template}: {count} slides ({percentage:.1f}%)")
                xiaohongshu_count += count
        
        # Log unknown templates
        for template in template_sequence:
            if template not in template_counts:
                logger.debug(f"  - {template}: unknown template type")
        
        logger.info(f"Template sequence: {' → '.join(template_sequence)}")
        
        # Log template category summary
        if xiaohongshu_count > 0:
            logger.info(f"Xiaohongshu templates used: {xiaohongshu_count} slides ({(xiaohongshu_count/len(slides)*100):.1f}%)")
            logger.debug("Xiaohongshu templates are optimized for 3:4 portrait aspect ratio (social media cards)")
        
        # Warn if too homogeneous (only check standard templates for now)
        standard_template_counts = {t: template_counts.get(t, 0) for t in standard_templates}
        max_count = max(standard_template_counts.values()) if standard_template_counts.values() else 0
        if max_count > len(slides) * 0.7 and len(slides) > 3:
            dominant_template = [t for t, c in standard_template_counts.items() if c == max_count][0]
            logger.warning(
                f"⚠ Template distribution is not diverse: '{dominant_template}' used in "
                f"{max_count}/{len(slides)} slides ({(max_count/len(slides)*100):.1f}%)"
            )
        else:
            logger.info("✓ Template distribution shows good variety")
        
        logger.info("=" * 60)

