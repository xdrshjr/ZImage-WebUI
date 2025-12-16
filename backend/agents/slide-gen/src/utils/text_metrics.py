"""
Text measurement and font scaling utilities for slide generation
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TextMetrics:
    """Calculate text dimensions and optimal font sizes for slides"""
    
    # Base font sizes (in pixels)
    BASE_TITLE_SIZE = 56
    BASE_HEADER_SIZE = 28
    BASE_CONTENT_SIZE = 32
    
    # Line height multipliers
    TITLE_LINE_HEIGHT = 1.1
    HEADER_LINE_HEIGHT = 1.2
    CONTENT_LINE_HEIGHT = 1.4
    
    # Average character width as percentage of font size
    AVG_CHAR_WIDTH_RATIO = 0.6
    
    # Scaling constraints
    MIN_SCALE_FACTOR = 0.7
    MAX_SCALE_FACTOR = 1.0
    SCALE_WARNING_THRESHOLD = 0.8
    
    # Content density thresholds
    DENSITY_LOW = 500      # Characters
    DENSITY_MEDIUM = 1000  # Characters
    DENSITY_HIGH = 1500    # Characters
    DENSITY_EXTREME = 2000 # Characters
    
    @staticmethod
    def estimate_text_height(
        text: str,
        font_size: int,
        line_height: float,
        max_width: int
    ) -> int:
        """
        Estimate rendered text height in pixels
        
        Args:
            text: Text content
            font_size: Font size in pixels
            line_height: Line height multiplier
            max_width: Maximum width in pixels
            
        Returns:
            Estimated height in pixels
        """
        if not text:
            return 0
        
        # Calculate characters per line based on average character width
        char_width = font_size * TextMetrics.AVG_CHAR_WIDTH_RATIO
        chars_per_line = max(1, int(max_width / char_width))
        
        # Calculate number of lines (accounting for newlines)
        text_length = len(text)
        newline_count = text.count('\n')
        
        # Estimate wrapped lines
        wrapped_lines = text_length // chars_per_line
        total_lines = wrapped_lines + newline_count + 1
        
        # Calculate total height
        line_height_px = font_size * line_height
        estimated_height = int(total_lines * line_height_px)
        
        logger.debug(
            f"Text height estimation: {text_length} chars, "
            f"{total_lines} lines, {estimated_height}px height"
        )
        
        return estimated_height
    
    @staticmethod
    def calculate_content_density(
        title: str,
        content_blocks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate content density metrics for a slide
        
        Args:
            title: Slide title
            content_blocks: List of content blocks
            
        Returns:
            Dictionary with density metrics
        """
        total_chars = len(title)
        text_blocks = 0
        images = 0
        section_headers = 0
        
        for block in content_blocks:
            if block.get('type') == 'text':
                text_blocks += 1
                content = block.get('content', '')
                total_chars += len(content)
                
                if block.get('section_title'):
                    section_headers += 1
                    total_chars += len(block['section_title'])
            elif block.get('type') == 'image_placeholder':
                images += 1
        
        # Calculate density score (0-1)
        # Based on character count with adjustments for images and sections
        base_density = total_chars / TextMetrics.DENSITY_EXTREME
        
        # Images reduce perceived density
        image_reduction = images * 0.1
        
        # Many sections increase perceived density
        section_penalty = max(0, (section_headers - 2) * 0.05)
        
        density_score = min(1.0, max(0.0, base_density - image_reduction + section_penalty))
        
        # Determine overflow risk
        if total_chars < TextMetrics.DENSITY_MEDIUM:
            overflow_risk = 'low'
        elif total_chars < TextMetrics.DENSITY_HIGH:
            overflow_risk = 'medium'
        else:
            overflow_risk = 'high'
        
        logger.debug(
            f"Content density: {total_chars} chars, {text_blocks} text blocks, "
            f"{images} images, density score: {density_score:.2f}"
        )
        
        return {
            'total_chars': total_chars,
            'text_blocks': text_blocks,
            'images': images,
            'section_headers': section_headers,
            'density_score': density_score,
            'overflow_risk': overflow_risk
        }
    
    @staticmethod
    def calculate_scale_factor(
        content_density: Dict[str, Any],
        available_height: int,
        template_type: str = 'title_and_content'
    ) -> float:
        """
        Calculate font scale factor to fit content within available space
        
        Args:
            content_density: Content density metrics
            available_height: Available height in pixels
            template_type: Template type being used
            
        Returns:
            Scale factor between MIN_SCALE_FACTOR and MAX_SCALE_FACTOR
        """
        density_score = content_density['density_score']
        total_chars = content_density['total_chars']
        text_blocks = content_density['text_blocks']
        
        # Start with base scale
        scale_factor = TextMetrics.MAX_SCALE_FACTOR
        
        # Adjust based on density score
        if density_score > 0.8:
            # Very high density - scale down significantly
            scale_factor = 0.75
            logger.debug(f"High density detected ({density_score:.2f}), scaling to 0.75")
        elif density_score > 0.6:
            # High density - moderate scaling
            scale_factor = 0.85
            logger.debug(f"Medium-high density ({density_score:.2f}), scaling to 0.85")
        elif density_score > 0.4:
            # Medium density - slight scaling
            scale_factor = 0.92
            logger.debug(f"Medium density ({density_score:.2f}), scaling to 0.92")
        else:
            # Low density - no scaling needed
            logger.debug(f"Low density ({density_score:.2f}), no scaling needed")
        
        # Template-specific adjustments
        if template_type == 'two_column':
            # Two column needs more aggressive scaling
            scale_factor *= 0.95
            logger.debug(f"Two-column template adjustment: {scale_factor:.2f}")
        elif template_type == 'image_focus':
            # Image focus has less text space
            if text_blocks > 2:
                scale_factor *= 0.90
                logger.debug(f"Image focus with multiple text blocks: {scale_factor:.2f}")
        
        # Ensure within bounds
        scale_factor = max(TextMetrics.MIN_SCALE_FACTOR, min(TextMetrics.MAX_SCALE_FACTOR, scale_factor))
        
        logger.info(f"Calculated font scale factor: {scale_factor:.2f}")
        
        return scale_factor
    
    @staticmethod
    def get_recommendations(
        content_density: Dict[str, Any],
        scale_factor: float
    ) -> List[str]:
        """
        Generate recommendations for content optimization
        
        Args:
            content_density: Content density metrics
            scale_factor: Calculated scale factor
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        total_chars = content_density['total_chars']
        overflow_risk = content_density['overflow_risk']
        
        # Scaling warnings
        if scale_factor < TextMetrics.SCALE_WARNING_THRESHOLD:
            recommendations.append(
                f"Font size scaled down to {scale_factor:.0%} due to content density"
            )
        
        if scale_factor <= TextMetrics.MIN_SCALE_FACTOR:
            recommendations.append(
                "Content is at maximum density - consider splitting into multiple slides"
            )
        
        # Character count warnings
        if total_chars > TextMetrics.DENSITY_EXTREME:
            recommendations.append(
                f"Very high character count ({total_chars}) - recommend reducing content"
            )
        elif total_chars > TextMetrics.DENSITY_HIGH:
            recommendations.append(
                f"High character count ({total_chars}) - consider using 'concise' content richness"
            )
        
        # Overflow risk warnings
        if overflow_risk == 'high':
            recommendations.append(
                "High overflow risk detected - content may not fit properly"
            )
        elif overflow_risk == 'medium':
            recommendations.append(
                "Medium overflow risk - monitor text rendering carefully"
            )
        
        return recommendations
    
    @staticmethod
    def log_scaling_analysis(
        slide_number: int,
        content_density: Dict[str, Any],
        scale_factor: float,
        template_type: str
    ):
        """
        Log detailed scaling analysis for debugging
        
        Args:
            slide_number: Current slide number
            content_density: Content density metrics
            scale_factor: Calculated scale factor
            template_type: Template type
        """
        logger.info(
            f"Slide {slide_number} font scaling analysis:",
            extra={
                'slide_number': slide_number,
                'template_type': template_type,
                'total_chars': content_density['total_chars'],
                'text_blocks': content_density['text_blocks'],
                'images': content_density['images'],
                'density_score': content_density['density_score'],
                'overflow_risk': content_density['overflow_risk'],
                'scale_factor': scale_factor
            }
        )
        
        # Log warnings
        if scale_factor < TextMetrics.SCALE_WARNING_THRESHOLD:
            logger.warning(
                f"Slide {slide_number}: Font scaled down to {scale_factor:.0%} "
                f"({content_density['total_chars']} chars, "
                f"density: {content_density['density_score']:.2f})"
            )
        
        # Get and log recommendations
        recommendations = TextMetrics.get_recommendations(content_density, scale_factor)
        if recommendations:
            logger.info(f"Slide {slide_number} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec}")

