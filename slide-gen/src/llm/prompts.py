"""
Prompt templates for LLM interactions
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for slide generation"""
    
    @staticmethod
    def outline_generation_prompt(
        base_text: str,
        num_slides: int,
        style: str,
        content_richness: str,
        aspect_ratio: str
    ) -> tuple[str, str]:
        """
        Generate prompt for creating slide outline
        
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        system_prompt = """You are an expert presentation designer. Your task is to create a structured outline for a presentation based on the given content.

Generate a JSON response with the following structure:
{
  "outline": [
    {
      "slide_number": 1,
      "title": "Slide title here",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }
  ]
}

Rules:
- Create exactly the requested number of slides
- Ensure logical flow and progression
- Make titles engaging and informative
- Key points should be concise and actionable
- First slide should be a title/introduction slide
- Last slide can be a conclusion or summary
"""
        
        user_prompt = f"""Create an outline for a {num_slides}-slide presentation.

Topic: {base_text}

Style: {style}
Content Richness: {content_richness}
Aspect Ratio: {aspect_ratio}

Please generate a structured outline with {num_slides} slides."""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def layout_generation_prompt(
        slide_outline: Dict[str, Any],
        style: str,
        content_richness: str,
        aspect_ratio: str,
        slide_number: int
    ) -> tuple[str, str]:
        """
        Generate prompt for creating slide layout and content
        
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        # Calculate dimensions based on aspect ratio
        dimensions = {
            "16:9": {"width": 1920, "height": 1080},
            "4:3": {"width": 1600, "height": 1200},
            "16:10": {"width": 1920, "height": 1200}
        }
        dims = dimensions[aspect_ratio]
        
        # Character limits based on content richness
        char_limits = {
            "concise": {"title": 50, "body": 250, "caption": 80},
            "moderate": {"title": 60, "body": 400, "caption": 100},
            "detailed": {"title": 70, "body": 600, "caption": 150}
        }
        limits = char_limits[content_richness]
        
        system_prompt = f"""You are an expert slide designer. Create detailed slide layouts with precise positioning and content.

Available templates:
1. "title_and_content": Title at top, content below, 1-2 images on right
2. "two_column": Title, left column (text), right column (text or image)
3. "image_focus": Large centered image with minimal text

Slide dimensions: {dims['width']}x{dims['height']}

Generate JSON response:
{{
  "slide_number": {slide_number},
  "template_type": "title_and_content",
  "layout": {{
    "title": "Slide title",
    "content_blocks": [
      {{
        "type": "text",
        "content": "Content here",
        "position": {{"x": 0, "y": 100, "width": 1200, "height": 400}},
        "char_limit": {limits['body']}
      }},
      {{
        "type": "image_placeholder",
        "position": {{"x": 1250, "y": 200, "width": 600, "height": 450}},
        "image_prompt": "Description for image generation"
      }}
    ]
  }}
}}

Rules:
- Title max {limits['title']} characters
- Body text max {limits['body']} characters
- Captions max {limits['caption']} characters
- All positions must fit within {dims['width']}x{dims['height']}
- Image prompts should be detailed and specific
- Use appropriate template for content type
"""
        
        user_prompt = f"""Design slide {slide_number} with the following outline:

Title: {slide_outline['title']}
Key Points: {', '.join(slide_outline['key_points'])}

Style: {style}
Content Richness: {content_richness}

Create a visually appealing layout with appropriate content and image placeholders."""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def image_prompt_refinement(
        raw_prompt: str,
        style: str,
        slide_number: int
    ) -> tuple[str, str]:
        """
        Generate prompt for refining image generation prompts
        
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        style_guidelines = {
            "professional": "corporate, clean, modern, professional photography, high quality",
            "creative": "artistic, vibrant, creative composition, dynamic, eye-catching",
            "minimal": "minimalist, simple, clean lines, elegant, uncluttered",
            "academic": "educational, clear, informative, technical illustration, professional"
        }
        
        system_prompt = """You are an expert prompt engineer for image generation. Enhance image prompts with specific artistic direction and technical details.

Respond with ONLY the enhanced prompt text, no JSON or additional formatting."""
        
        user_prompt = f"""Enhance this image prompt for slide {slide_number}:

Original prompt: {raw_prompt}

Style: {style}
Guidelines: {style_guidelines.get(style, 'professional')}

Add specific details about:
- Composition and framing
- Lighting and mood
- Color palette
- Art style or medium
- Quality indicators

Output the enhanced prompt only, no additional text."""
        
        return system_prompt, user_prompt

