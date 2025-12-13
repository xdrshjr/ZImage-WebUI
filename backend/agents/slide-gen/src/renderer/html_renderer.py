"""
HTML slide renderer using Jinja2 templates
"""

import logging
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.utils.config import config
from src.utils.validators import InputValidator

logger = logging.getLogger(__name__)


class HTMLRenderer:
    """Renders slides to HTML using Jinja2 templates"""
    
    def __init__(self):
        """Initialize HTML renderer with Jinja2 environment"""
        templates_dir = Path(__file__).parent.parent / "templates"
        
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Aspect ratio dimensions
        self.dimensions = {
            "16:9": {"width": 1920, "height": 1080},
            "4:3": {"width": 1600, "height": 1200},
            "16:10": {"width": 1920, "height": 1200}
        }
    
    def render_slide(
        self,
        slide_data: Dict[str, Any],
        style: str,
        aspect_ratio: str
    ) -> Path:
        """
        Render slide to HTML file
        
        Args:
            slide_data: Slide data dictionary
            style: Visual style
            aspect_ratio: Aspect ratio
            
        Returns:
            Path to generated HTML file
        """
        slide_number = slide_data['slide_number']
        template_type = slide_data['template_type']
        layout = slide_data['layout']
        
        logger.debug(f"Rendering slide {slide_number} with {template_type} template")
        
        # Get dimensions
        dims = self.dimensions[aspect_ratio]
        
        # Validate and truncate text content
        title = layout.get('title', '')
        title = self._validate_and_truncate(title, 70, 'title', slide_number)
        
        content_blocks = layout.get('content_blocks', [])
        for block in content_blocks:
            if block.get('type') == 'text':
                char_limit = block.get('char_limit', 500)
                content = block.get('content', '')
                block['content'] = self._validate_and_truncate(
                    content, char_limit, 'content block', slide_number
                )
        
        # Load template
        template_file = f"{template_type}.html"
        try:
            template = self.env.get_template(template_file)
        except Exception as e:
            logger.warning(f"Template {template_file} not found, using title_and_content.html")
            template = self.env.get_template("title_and_content.html")
        
        # Render template
        html_content = template.render(
            slide_number=slide_number,
            title=title,
            content_blocks=content_blocks,
            style=style,
            width=dims['width'],
            height=dims['height']
        )
        
        # Save to file
        output_path = config.html_dir / f"slide_{slide_number}.html"
        output_path.write_text(html_content, encoding='utf-8')
        
        logger.debug(f"HTML saved to {output_path}")
        return output_path
    
    def _validate_and_truncate(
        self,
        text: str,
        max_length: int,
        field_name: str,
        slide_number: int
    ) -> str:
        """
        Validate and truncate text to character limit
        
        Args:
            text: Text to validate
            max_length: Maximum length
            field_name: Field name for logging
            slide_number: Current slide number
            
        Returns:
            Validated and possibly truncated text
        """
        if len(text) > max_length:
            logger.warning(
                f"Slide {slide_number} {field_name} exceeds {max_length} chars "
                f"({len(text)}), truncating"
            )
            return InputValidator.truncate_text(text, max_length)
        return text

