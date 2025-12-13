"""
Template selection validator for ensuring diverse slide layouts
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class TemplateValidator:
    """Validates and enforces template selection rules for slide generation"""
    
    # Valid template types
    VALID_TEMPLATES = ['title_and_content', 'two_column', 'image_focus']
    
    # Default template if validation fails
    DEFAULT_TEMPLATE = 'title_and_content'
    
    @staticmethod
    def validate_and_enforce_template(
        selected_template: str,
        slide_number: int,
        total_slides: int,
        previous_templates: List[str],
        slide_title: str
    ) -> str:
        """
        Validate and potentially override template selection to ensure diversity
        
        Args:
            selected_template: Template selected by LLM
            slide_number: Current slide number (1-indexed)
            total_slides: Total number of slides
            previous_templates: List of templates used in previous slides
            slide_title: Title of current slide for logging
            
        Returns:
            Validated and potentially corrected template type
        """
        original_template = selected_template
        
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
            'image_focus': 0
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
        for template, count in template_counts.items():
            percentage = (count / len(slides)) * 100 if slides else 0
            logger.info(f"  - {template}: {count} slides ({percentage:.1f}%)")
        
        logger.info(f"Template sequence: {' → '.join(template_sequence)}")
        
        # Warn if too homogeneous
        max_count = max(template_counts.values())
        if max_count > len(slides) * 0.7 and len(slides) > 3:
            dominant_template = [t for t, c in template_counts.items() if c == max_count][0]
            logger.warning(
                f"⚠ Template distribution is not diverse: '{dominant_template}' used in "
                f"{max_count}/{len(slides)} slides ({(max_count/len(slides)*100):.1f}%)"
            )
        else:
            logger.info("✓ Template distribution shows good variety")
        
        logger.info("=" * 60)

