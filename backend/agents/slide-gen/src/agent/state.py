"""
Shared state schema for LangGraph workflow
"""

from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated


class SlideOutlineEntry(TypedDict):
    """Single slide outline entry"""
    slide_number: int
    title: str
    key_points: List[str]


class ContentBlock(TypedDict):
    """Content block within a slide layout"""
    type: str  # "text" or "image_placeholder"
    content: Optional[str]
    position: Dict[str, int]  # x, y, width, height
    char_limit: Optional[int]
    image_prompt: Optional[str]
    image_path: Optional[str]


class SlideLayout(TypedDict):
    """Slide layout specification"""
    title: str
    content_blocks: List[ContentBlock]


class SlideData(TypedDict):
    """Complete data for a single slide"""
    slide_number: int
    template_type: str
    layout: SlideLayout
    html_path: Optional[str]
    image_path: Optional[str]


class SlideGenerationState(TypedDict):
    """Shared state for slide generation workflow"""
    # Input parameters
    base_text: str
    num_slides: int
    aspect_ratio: str
    style: str
    content_richness: str
    color_scheme: str
    
    # Workflow state
    outline: List[SlideOutlineEntry]
    current_slide_index: int
    slides: List[SlideData]
    
    # Output paths
    output_dir: str
    pdf_path: Optional[str]
    ppt_path: Optional[str]
    
    # Error tracking
    errors: List[str]

