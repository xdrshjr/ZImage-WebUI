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
        slide_number: int,
        total_slides: int
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
        
        # Determine recommended template based on slide position and keywords
        recommended_template = PromptTemplates._recommend_template(
            slide_outline, slide_number, total_slides
        )
        
        system_prompt = f"""You are an expert slide designer. Create detailed slide layouts with precise positioning and content.

CRITICAL REQUIREMENT: You MUST create visual variety by selecting different templates for different slides.
DO NOT use "title_and_content" for every slide - this creates boring, repetitive presentations.

Available templates and when to use them:
1. "title_and_content": Standard layout with text and supporting images
   - Use when: Content has bullet points, lists, or paragraphs with 1-2 supporting visuals
   - Layout: Title at top, main text content (left/center), 1-2 images on right
   - Best for: Explanations, lists, key points with visual support
   
2. "two_column": Side-by-side comparison or parallel information layout
   - Use when: Comparing two things, showing before/after, pros/cons, or parallel concepts
   - Layout: Title at top, two equal columns (can be text vs text, or text vs image)
   - Best for: Comparisons, contrasts, dual concepts, process flows
   
3. "image_focus": Visual-dominant layout with minimal text
   - Use when: The visual is the main message, or content is highly visual
   - Layout: Large centered image with brief caption below
   - Best for: Showcases, demonstrations, visual examples, impactful closings

Slide dimensions: {dims['width']}x{dims['height']}

MANDATORY TEMPLATE SELECTION RULES:
- Slide 1 (title/intro): MUST use "title_and_content" for clear introduction
- Slides 2-{total_slides-1} (body): MUST vary between all three templates based on content
- Last slide (conclusion): SHOULD use "image_focus" for visual impact (unless content demands otherwise)
- NEVER use the same template for 3+ consecutive slides
- Actively look for opportunities to use "two_column" and "image_focus"

RECOMMENDED TEMPLATE FOR THIS SLIDE: {recommended_template}
(You may override this if content strongly suggests a different template)

Example for "title_and_content":
{{
  "slide_number": {slide_number},
  "template_type": "title_and_content",
  "layout": {{
    "title": "Introduction to Key Concepts",
    "content_blocks": [
      {{
        "type": "text",
        "content": "Main content with bullet points",
        "position": {{"x": 80, "y": 200, "width": 1100, "height": 600}},
        "char_limit": {limits['body']}
      }},
      {{
        "type": "image_placeholder",
        "position": {{"x": 1250, "y": 200, "width": 580, "height": 600}},
        "image_prompt": "Detailed description for image"
      }}
    ]
  }}
}}

Example for "two_column":
{{
  "slide_number": {slide_number},
  "template_type": "two_column",
  "layout": {{
    "title": "Comparison of Approaches",
    "content_blocks": [
      {{
        "type": "text",
        "content": "Left column content",
        "position": {{"x": 80, "y": 200, "width": 850, "height": 700}},
        "char_limit": {limits['body']}
      }},
      {{
        "type": "text",
        "content": "Right column content",
        "position": {{"x": 990, "y": 200, "width": 850, "height": 700}},
        "char_limit": {limits['body']}
      }}
    ]
  }}
}}

Example for "image_focus":
{{
  "slide_number": {slide_number},
  "template_type": "image_focus",
  "layout": {{
    "title": "Visual Demonstration",
    "content_blocks": [
      {{
        "type": "image_placeholder",
        "position": {{"x": 300, "y": 250, "width": 1320, "height": 700}},
        "image_prompt": "High-quality detailed image description"
      }},
      {{
        "type": "text",
        "content": "Brief caption or explanation",
        "position": {{"x": 300, "y": 980, "width": 1320, "height": 80}},
        "char_limit": {limits['caption']}
      }}
    ]
  }}
}}

Rules:
- You MUST analyze the content and select the MOST APPROPRIATE template type
- DO NOT default to "title_and_content" for all slides
- Title max {limits['title']} characters
- Body text max {limits['body']} characters
- Captions max {limits['caption']} characters
- All positions must fit within {dims['width']}x{dims['height']}
- Image prompts should be detailed and specific
- Consider slide position in presentation when selecting template
"""
        
        user_prompt = f"""Design slide {slide_number} of {total_slides} with the following outline:

Title: {slide_outline['title']}
Key Points: {', '.join(slide_outline['key_points'])}

Style: {style}
Content Richness: {content_richness}

TEMPLATE SELECTION (CRITICAL):
You MUST select ONE of these templates - analyze the content carefully:
- "title_and_content": For explanations, lists, concepts with supporting visuals
- "two_column": For comparisons, contrasts, parallel concepts, side-by-side information
- "image_focus": For visual showcases, demonstrations, impactful visuals

ANALYSIS CHECKLIST:
1. Slide position: {slide_number} of {total_slides} (first? middle? last?)
2. Content type: Does it compare/contrast? Is it visual-heavy? Is it a list/explanation?
3. Key points: {len(slide_outline['key_points'])} points to present
4. Recommended template: {recommended_template} (consider using this)

REMEMBER: Avoid repetition! Create variety by using different templates for different slides.

Your response MUST include "template_type" at the top level of the JSON with one of the three template names.

Create a visually appealing layout with the selected template."""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def _recommend_template(
        slide_outline: Dict[str, Any],
        slide_number: int,
        total_slides: int
    ) -> str:
        """
        Recommend a template based on slide position and content analysis
        
        Args:
            slide_outline: The slide outline with title and key points
            slide_number: Current slide number (1-indexed)
            total_slides: Total number of slides
            
        Returns:
            Recommended template type string
        """
        title = slide_outline.get('title', '').lower()
        key_points = slide_outline.get('key_points', [])
        key_points_text = ' '.join(key_points).lower()
        
        # First slide: always title_and_content for introduction
        if slide_number == 1:
            return "title_and_content"
        
        # Last slide: prefer image_focus for visual impact
        if slide_number == total_slides:
            return "image_focus"
        
        # Check for comparison/contrast keywords -> two_column
        comparison_keywords = [
            'vs', 'versus', 'comparison', 'compare', 'contrast', 'difference', 
            'before', 'after', 'pros', 'cons', 'advantages', 'disadvantages',
            'traditional', 'modern', 'old', 'new', 'left', 'right'
        ]
        if any(keyword in title or keyword in key_points_text for keyword in comparison_keywords):
            return "two_column"
        
        # Check for visual/showcase keywords -> image_focus
        visual_keywords = [
            'demo', 'demonstration', 'example', 'showcase', 'visual', 'image',
            'photo', 'illustration', 'diagram', 'chart', 'graph', 'result',
            'output', 'screenshot', 'gallery', 'preview'
        ]
        if any(keyword in title or keyword in key_points_text for keyword in visual_keywords):
            return "image_focus"
        
        # Middle slides: vary based on position to ensure diversity
        # Use modulo to cycle through templates
        middle_slide_index = slide_number - 2  # 0-indexed for middle slides
        template_cycle = ['title_and_content', 'two_column', 'image_focus']
        return template_cycle[middle_slide_index % 3]
    
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

