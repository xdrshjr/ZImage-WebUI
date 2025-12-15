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
        system_prompt = """You are an expert presentation designer specializing in academic and professional presentations. Your task is to create a structured outline for a presentation based on the given content.

Generate a JSON response with the following structure:
{
  "outline": [
    {
      "slide_number": 1,
      "title": "Slide title here",
      "sections": [
        {
          "section_title": "Section 1 Title",
          "bullet_points": ["• Key point 1", "• Key point 2", "• Key point 3"]
        },
        {
          "section_title": "Section 2 Title", 
          "bullet_points": ["• Key point 1", "• Key point 2", "• Key point 3"]
        }
      ]
    }
  ]
}

CRITICAL REQUIREMENTS FOR RICH, STRUCTURED CONTENT:
- Create exactly the requested number of slides
- Each slide should have 2-4 distinct SECTIONS with subsection titles
- Each section should have 3-5 bullet points (brief phrases or short sentences)
- Bullet points should start with • symbol
- Points should be concise (5-15 words each) - NOT long paragraphs
- Organize content into logical, well-structured sections
- First slide: introduction with multiple sections (overview, objectives, etc.)
- Middle slides: develop topic with multiple organized sections per slide
- Last slide: conclusion with multiple sections (summary, takeaways, etc.)
- Aim for rich structure with multiple organized content blocks, not dense text
"""
        
        user_prompt = f"""Create a well-structured outline for a {num_slides}-slide presentation with MULTIPLE content sections per slide.

Topic: {base_text}

Style: {style}
Content Richness: {content_richness}
Aspect Ratio: {aspect_ratio}

IMPORTANT INSTRUCTIONS:
- Generate exactly {num_slides} slides
- Each slide must have 2-4 distinct SECTIONS (content blocks)
- Each section needs a clear subsection title
- Each section should contain 3-5 bullet points
- Bullet points should be brief, clear phrases (5-15 words each)
- Use • symbol to start each bullet point
- Create rich structure through multiple organized sections, NOT through long text
- Organize information logically with clear hierarchical structure

Please generate a structured outline with {num_slides} slides, each having multiple sections with bullet points."""
        
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
        
        # Character limits based on content richness - for bullet point text blocks
        char_limits = {
            "concise": {"title": 60, "section_title": 40, "bullet_block": 200, "caption": 120},
            "moderate": {"title": 70, "section_title": 50, "bullet_block": 300, "caption": 150},
            "detailed": {"title": 80, "section_title": 60, "bullet_block": 400, "caption": 200}
        }
        limits = char_limits[content_richness]
        
        # Determine recommended template based on slide position and keywords
        recommended_template = PromptTemplates._recommend_template(
            slide_outline, slide_number, total_slides
        )
        
        system_prompt = f"""You are an expert slide designer specializing in academic and professional presentations. Create detailed, visually appealing slide layouts with MULTIPLE text blocks, each containing organized bullet points.

CRITICAL REQUIREMENT: You MUST create visual variety by selecting different templates for different slides.
DO NOT use "title_and_content" for every slide - this creates boring, repetitive presentations.

CONTENT STRUCTURE REQUIREMENT - VERY IMPORTANT:
- Rich content means MULTIPLE separate text blocks on each slide
- Each text block should have a section title and 3-5 bullet points
- Bullet points should be brief phrases (5-15 words), starting with •
- DO NOT create large paragraphs - use structured bullet lists instead
- Typical slide should have 2-3 text blocks + 1-2 images

Available templates and when to use them:
1. "title_and_content": Standard layout with multiple text sections and supporting images
   - Use when: Content has multiple sections with bullet points and 1-2 supporting visuals
   - Layout: Title at top, multiple text blocks (left/center) each with section title + bullets, 1-2 images on right
   - Best for: Organized explanations, multiple concept areas with visual support
   - Image margins: Minimum 60px from edges
   
2. "two_column": Side-by-side comparison or parallel information layout
   - Use when: Comparing two things, showing before/after, pros/cons, or parallel concepts
   - Layout: Title at top, left column (multiple text blocks), right column (text blocks or image)
   - Best for: Detailed comparisons, contrasts, dual concepts
   - Image margins: Minimum 60px from edges, 35px internal padding
   
3. "image_focus": Visual-dominant layout with structured text below
   - Use when: The visual is the primary message
   - Layout: Large centered image (85% width max) with organized bullet points below
   - Best for: Demonstrations, visual examples, impactful showcases
   - Image margins: 60px horizontal margins, 40px bottom margin

Slide dimensions: {dims['width']}x{dims['height']}

MANDATORY TEMPLATE SELECTION RULES:
- Slide 1 (title/intro): MUST use "title_and_content" for clear, comprehensive introduction
- Slides 2-{total_slides-1} (body): MUST vary between all three templates based on content
- Last slide (conclusion): SHOULD use "image_focus" for visual impact (unless content demands otherwise)
- NEVER use the same template for 3+ consecutive slides
- Actively look for opportunities to use "two_column" and "image_focus"

RECOMMENDED TEMPLATE FOR THIS SLIDE: {recommended_template}
(You may override this if content strongly suggests a different template)

IMAGE POSITIONING REQUIREMENTS (CRITICAL - STRICTLY ENFORCED):
- ALL images MUST have MINIMUM 60px margin from ALL slide edges (top, bottom, left, right)
- Images MUST NEVER touch or be close to the slide border
- Template will automatically constrain images, but you must provide safe positions
- Safe zones for images:
  * Minimum X position: 60px
  * Maximum X position: {dims['width']} - 60 - image_width
  * Minimum Y position: 80px (below title)
  * Maximum Y position: {dims['height']} - 80 - image_height
- For "title_and_content": Recommended image x ≥ 1180, width ≤ 660, y ≥ 200, height ≤ 800
- For "two_column": Images should be within column bounds with extra internal padding
- For "image_focus": Center images with x ≥ 240, width ≤ 1440, y ≥ 220, height ≤ 600
- NEVER position images at edges like x=1250+ for 1920px width slides
- Calculate carefully: if x=1200 and width=640, then x+width=1840, leaving only 80px margin (OK)
- Calculate carefully: if x=1300 and width=640, then x+width=1940 > 1920-60=1860 (TOO CLOSE!)
- Always ensure: position.x + position.width ≤ {dims['width']} - 60
- Always ensure: position.y + position.height ≤ {dims['height']} - 80
- Leave proper spacing between text blocks and images (minimum 50px gap)

IMAGE ASPECT RATIO GUIDANCE (IMPORTANT FOR QUALITY):
- Use standard aspect ratios to prevent distortion and ensure professional appearance
- Recommended aspect ratios for different placements:
  * Landscape images: 16:9 (e.g., 800x450, 960x540, 1440x810) or 4:3 (e.g., 800x600, 960x720)
  * Portrait images: 3:4 (e.g., 450x600, 540x720) or 2:3 (e.g., 400x600, 480x720)
  * Square images: 1:1 (e.g., 600x600, 720x720, 800x800)
  * Wide images: 21:9 (e.g., 840x360) for panoramic views
- For "title_and_content": Use landscape (16:9 or 4:3) or portrait (3:4) images
- For "two_column": Use portrait (3:4, 2:3) or square (1:1) images within columns
- For "image_focus": Use landscape (16:9) images for maximum visual impact
- Avoid extreme aspect ratios (narrower than 1:3 or wider than 3:1) to prevent distortion
- Example good dimensions: 960x540 (16:9), 800x600 (4:3), 720x720 (1:1), 480x720 (2:3)
- Images will be scaled to fit within containers while preserving aspect ratio (no cropping)

Example for "title_and_content" with MULTIPLE text blocks:
{{
  "slide_number": {slide_number},
  "template_type": "title_and_content",
  "layout": {{
    "title": "Main Slide Title",
    "content_blocks": [
      {{
        "type": "text",
        "section_title": "First Section",
        "content": "• First key point (brief phrase)\\n• Second key point\\n• Third key point\\n• Fourth key point",
        "position": {{"x": 80, "y": 200, "width": 520, "height": 300}},
        "char_limit": {limits['bullet_block']}
      }},
      {{
        "type": "text",
        "section_title": "Second Section",
        "content": "• First key point\\n• Second key point\\n• Third key point",
        "position": {{"x": 80, "y": 530, "width": 520, "height": 250}},
        "char_limit": {limits['bullet_block']}
      }},
      {{
        "type": "text",
        "section_title": "Third Section",
        "content": "• Key point one\\n• Key point two\\n• Key point three",
        "position": {{"x": 650, "y": 200, "width": 490, "height": 300}},
        "char_limit": {limits['bullet_block']}
      }},
      {{
        "type": "image_placeholder",
        "position": {{"x": 1180, "y": 200, "width": 660, "height": 700}},
        "image_prompt": "Highly detailed, descriptive prompt for generating a professional image"
      }}
    ]
  }}
}}

Example for "two_column" with multiple sections:
{{
  "slide_number": {slide_number},
  "template_type": "two_column",
  "layout": {{
    "title": "Comparison Title",
    "content_blocks": [
      {{
        "type": "text",
        "section_title": "Left Approach - Section 1",
        "content": "• Point one\\n• Point two\\n• Point three",
        "position": {{"x": 80, "y": 200, "width": 850, "height": 350}},
        "char_limit": {limits['bullet_block']}
      }},
      {{
        "type": "text",
        "section_title": "Left Approach - Section 2",
        "content": "• Additional point\\n• More details\\n• Further info",
        "position": {{"x": 80, "y": 580, "width": 850, "height": 300}},
        "char_limit": {limits['bullet_block']}
      }},
      {{
        "type": "text",
        "section_title": "Right Approach - Section 1",
        "content": "• Point one\\n• Point two\\n• Point three",
        "position": {{"x": 1000, "y": 200, "width": 840, "height": 350}},
        "char_limit": {limits['bullet_block']}
      }},
      {{
        "type": "text",
        "section_title": "Right Approach - Section 2",
        "content": "• Additional point\\n• More details\\n• Further info",
        "position": {{"x": 1000, "y": 580, "width": 840, "height": 300}},
        "char_limit": {limits['bullet_block']}
      }}
    ]
  }}
}}

Example for "image_focus":
{{
  "slide_number": {slide_number},
  "template_type": "image_focus",
  "layout": {{
    "title": "Visual Demonstration Title",
    "content_blocks": [
      {{
        "type": "image_placeholder",
        "position": {{"x": 240, "y": 220, "width": 1440, "height": 580}},
        "image_prompt": "Highly detailed professional image description"
      }},
      {{
        "type": "text",
        "section_title": "Key Findings",
        "content": "• Main finding one\\n• Main finding two\\n• Main finding three",
        "position": {{"x": 240, "y": 840, "width": 1440, "height": 180}},
        "char_limit": {limits['caption']}
      }}
    ]
  }}
}}

CONTENT QUALITY REQUIREMENTS:
- Titles: descriptive and informative ({limits['title']} chars max)
- Section titles: clear subsection headers ({limits['section_title']} chars max)
- Bullet point blocks: 3-5 concise points per block ({limits['bullet_block']} chars max total)
- Each bullet point: 5-15 words (brief phrases, NOT long sentences)
- Use • symbol at start of each bullet point
- Captions: substantive with bullet structure ({limits['caption']} chars max)
- Create multiple text blocks per slide for rich, organized content

POSITIONING RULES:
- All positions must fit within {dims['width']}x{dims['height']}
- Text blocks: position multiple blocks across the slide (left, center, right areas)
- Images: MUST maintain 60px minimum margin from ALL edges (strictly enforced)
- Image positioning formula: x ∈ [60, {dims['width']}-60-width], y ∈ [80, {dims['height']}-80-height]
- VERIFY your calculations: x + width ≤ {dims['width']} - 60 and y + height ≤ {dims['height']} - 80
- Ensure no overlapping elements
- Create visual balance with distributed text blocks and images
- Templates will constrain images to safe zones automatically
"""
        
        user_prompt = f"""Design slide {slide_number} of {total_slides} with MULTIPLE structured text blocks based on the outline sections:

Title: {slide_outline['title']}
Sections: {slide_outline.get('sections', [])}

Style: {style}
Content Richness: {content_richness}

TEMPLATE SELECTION (CRITICAL):
You MUST select ONE of these templates - analyze the content carefully:
- "title_and_content": For multiple organized sections with bullet points and supporting visuals
- "two_column": For side-by-side comparisons with multiple sections in each column
- "image_focus": For visual showcases with organized bullet points below

ANALYSIS CHECKLIST:
1. Slide position: {slide_number} of {total_slides} (first? middle? last?)
2. Content type: Multiple sections? Comparison? Visual-heavy?
3. Sections count: {len(slide_outline.get('sections', []))} sections to present
4. Recommended template: {recommended_template} (strongly consider using this)

CONTENT STRUCTURE REQUIREMENTS - VERY IMPORTANT:
- Create MULTIPLE separate text blocks (one per section from outline)
- Each text block must have:
  * A "section_title" field with the section heading
  * A "content" field with 3-5 bullet points
  * Bullet points formatted as: "• Point text\\n• Point text\\n• Point text"
- Each bullet point should be brief (5-15 words)
- DO NOT write long paragraphs - use structured bullet lists
- Position text blocks in different areas of the slide (left, center, right)
- Typical slide should have 2-3 text blocks + 1-2 images for rich content

IMAGE POSITIONING (CRITICAL - MUST FOLLOW):
- ALL images MUST have MINIMUM 60px margin from ALL slide edges
- Images positioned away from borders (NEVER touching edges)
- Safe positioning formulas:
  * x_min = 60, x_max = {dims['width']} - 60 - width
  * y_min = 80, y_max = {dims['height']} - 80 - height
- Verify: x + width ≤ {dims['width']} - 60
- Verify: y + height ≤ {dims['height']} - 80
- For 1920x1080 slides: max safe right edge is 1840 (not 1920!)
- Example BAD: x=1300, width=640 → right edge=1940 (exceeds 1860 limit!)
- Example GOOD: x=1180, width=660 → right edge=1840 (exactly at limit)
- Leave proper spacing between text blocks and images (minimum 50px gap)
- Templates will enforce margins automatically, but provide safe positions

IMAGE ASPECT RATIO (IMPORTANT):
- Use standard aspect ratios for best results: 16:9, 4:3, 1:1, 3:4, 2:3
- Recommended dimensions: 960x540 (16:9), 800x600 (4:3), 720x720 (1:1), 480x720 (2:3)
- Avoid extreme ratios (narrower than 1:3 or wider than 3:1)
- Images will be scaled with aspect ratio preserved (no cropping/distortion)

REMEMBER: 
- Rich content = multiple organized text blocks, NOT long text
- Each text block = section title + bullet points
- Avoid repetition! Use different templates for different slides
- Ensure images have proper margins and don't touch edges
- Your response MUST include "template_type" at the top level

Create a visually appealing, well-structured layout with multiple content blocks."""
        
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
            "professional": "corporate, clean, modern, professional photography, high quality, sharp details, polished look",
            "creative": "artistic, vibrant, creative composition, dynamic, eye-catching, bold colors, innovative design",
            "minimal": "minimalist, simple, clean lines, elegant, uncluttered, sophisticated simplicity, refined aesthetic",
            "academic": "educational, clear, informative, scholarly, technical illustration, professional, high-quality diagrams, research-grade visuals"
        }
        
        system_prompt = """You are an expert prompt engineer for image generation, specializing in creating detailed, high-quality prompts for professional and academic presentations. Enhance image prompts with specific artistic direction, technical details, and visual clarity requirements.

Respond with ONLY the enhanced prompt text, no JSON or additional formatting."""
        
        user_prompt = f"""Enhance this image prompt for a professional presentation slide {slide_number}:

Original prompt: {raw_prompt}

Style: {style}
Visual Guidelines: {style_guidelines.get(style, 'professional')}

ENHANCEMENT REQUIREMENTS:
Add comprehensive, specific details about:
- Precise composition and framing (rule of thirds, focal points, perspective)
- Lighting conditions and mood (natural light, studio lighting, dramatic, soft)
- Detailed color palette with specific hues and tones
- Art style, medium, or photographic approach (realistic, illustrative, technical)
- Quality indicators and resolution (4K, high-resolution, professional grade, sharp focus)
- Spatial arrangement and depth (foreground, background, layering)
- Professional finish and polish requirements

IMPORTANT:
- Create a detailed, descriptive prompt that will generate high-quality, presentation-ready visuals
- Ensure the image will be suitable for an academic/professional audience
- Emphasize clarity, professionalism, and visual appeal
- Include sufficient detail to guide accurate image generation

Output the enhanced prompt only, no additional text or explanation."""
        
        return system_prompt, user_prompt

