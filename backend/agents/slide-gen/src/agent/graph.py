"""
LangGraph workflow definition for slide generation
"""

import logging
from typing import Dict, Any
from pathlib import Path
from langgraph.graph import StateGraph, END
from src.agent.state import SlideGenerationState
from src.agent.nodes import SlideGenerationNodes
from src.renderer.image_exporter import ImageExporter
from src.renderer.pdf_exporter import PDFExporter
from src.renderer.ppt_exporter import PPTExporter
from src.utils.validators import InputValidator
from src.utils.template_validator import TemplateValidator
from src.utils.config import config

logger = logging.getLogger(__name__)


class SlideGenerationAgent:
    """Main agent orchestrating slide generation workflow"""
    
    def __init__(self):
        """Initialize agent with workflow graph"""
        self.nodes = SlideGenerationNodes()
        self.image_exporter = ImageExporter()
        self.pdf_exporter = PDFExporter()
        self.ppt_exporter = PPTExporter()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow
        
        Returns:
            Compiled StateGraph
        """
        # Create workflow graph
        workflow = StateGraph(SlideGenerationState)
        
        # Add nodes
        workflow.add_node("generate_outline", self.nodes.generate_outline_node)
        workflow.add_node("generate_layout", self.nodes.generate_slide_layout_node)
        workflow.add_node("generate_images", self.nodes.generate_images_node)
        workflow.add_node("render_html", self.nodes.render_slide_html_node)
        workflow.add_node("increment_index", self.nodes.increment_slide_index_node)
        workflow.add_node("export_final", self._export_final_outputs)
        
        # Set entry point
        workflow.set_entry_point("generate_outline")
        
        # Add edges
        workflow.add_edge("generate_outline", "generate_layout")
        workflow.add_edge("generate_layout", "generate_images")
        workflow.add_edge("generate_images", "render_html")
        workflow.add_edge("render_html", "increment_index")
        
        # Conditional edge for loop
        workflow.add_conditional_edges(
            "increment_index",
            self.nodes.should_continue_slides,
            {
                "continue": "generate_layout",
                "finish": "export_final"
            }
        )
        
        workflow.add_edge("export_final", END)
        
        return workflow.compile()
    
    def _export_final_outputs(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export final outputs (slide images, PDF, and PPT)
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with export paths
        """
        logger.info("=" * 60)
        logger.info("PHASE 3: Final Export")
        logger.info("=" * 60)
        
        # Log comprehensive template distribution analysis
        TemplateValidator.log_template_distribution(state['slides'])
        
        try:
            # Export individual slide images
            logger.info("→ Step 3.1: Exporting slide images (HTML to PNG)")
            exported_image_paths = []
            
            for slide_data in state['slides']:
                if slide_data.get('html_path'):
                    html_path = Path(slide_data['html_path'])
                    slide_number = slide_data['slide_number']
                    
                    image_path = config.slide_images_dir / f"slide_{slide_number}.png"
                    
                    logger.debug(f"Exporting slide {slide_number}: {html_path.name} -> {image_path.name}")
                    
                    success = self.image_exporter.export_html_to_image(
                        html_path=html_path,
                        output_path=image_path,
                        aspect_ratio=state['aspect_ratio']
                    )
                    
                    if success:
                        slide_data['image_path'] = str(image_path)
                        exported_image_paths.append(image_path)
                        logger.info(f"  ✓ Slide {slide_number} exported to PNG")
                    else:
                        logger.warning(f"  ⚠ Failed to export slide {slide_number}")
            
            # Generate PDF from exported images
            logger.info("→ Step 3.2: Generating PDF from slide images")
            
            # Collect image files in order
            image_files = [
                Path(slide['image_path']) 
                for slide in state['slides'] 
                if slide.get('image_path') and Path(slide['image_path']).exists()
            ]
            
            # Also get HTML files as fallback
            html_files = [
                Path(slide['html_path']) 
                for slide in state['slides'] 
                if slide.get('html_path')
            ]
            
            if image_files:
                logger.info(f"Using {len(image_files)} pre-rendered PNG images for PDF generation")
                logger.debug(f"Image files: {[img.name for img in image_files]}")
                
                pdf_path = config.output_dir / "final_presentation.pdf"
                
                # Pass both image files (preferred) and HTML files (fallback)
                success = self.pdf_exporter.export_to_pdf(
                    html_files=html_files,
                    output_path=pdf_path,
                    aspect_ratio=state['aspect_ratio'],
                    image_files=image_files
                )
                
                if success:
                    state['pdf_path'] = str(pdf_path)
                    logger.info(f"  ✓ PDF generated successfully: {pdf_path.name}")
                else:
                    logger.error("  ✗ PDF generation failed")
                    state['errors'].append("PDF generation failed")
            else:
                logger.warning("  ⚠ No slide images available for PDF generation")
                state['errors'].append("No slide images available for PDF generation")
            
            # Generate PowerPoint presentation
            logger.info("→ Step 3.3: Generating PowerPoint presentation (PPTX)")
            logger.info("Converting HTML slides to editable PowerPoint format...")
            
            if state['slides']:
                ppt_path = config.output_dir / "final_presentation.pptx"
                color_scheme = state.get('color_scheme', 'light_blue')
                
                logger.debug(f"Preparing {len(state['slides'])} slides for PPT export")
                logger.debug(f"Using color scheme: {color_scheme}")
                
                # Export slides to PPT
                success = self.ppt_exporter.export_to_ppt(
                    slides_data=state['slides'],
                    output_path=ppt_path,
                    aspect_ratio=state['aspect_ratio'],
                    color_scheme=color_scheme
                )
                
                if success:
                    state['ppt_path'] = str(ppt_path)
                    logger.info(f"  ✓ PowerPoint generated successfully: {ppt_path.name}")
                else:
                    logger.error("  ✗ PowerPoint generation failed")
                    state['errors'].append("PowerPoint generation failed")
            else:
                logger.warning("  ⚠ No slides available for PowerPoint generation")
                state['errors'].append("No slides available for PowerPoint generation")
            
        except Exception as e:
            error_msg = f"Final export failed: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            state['errors'].append(error_msg)
        
        return state
    
    def generate_slides(
        self,
        base_text: str,
        num_slides: int,
        aspect_ratio: str,
        style: str,
        content_richness: str,
        color_scheme: str = "light_blue"
    ) -> Dict[str, Any]:
        """
        Generate presentation slides
        
        Args:
            base_text: Source content
            num_slides: Number of slides to generate
            aspect_ratio: Slide aspect ratio
            style: Visual style
            content_richness: Content detail level
            color_scheme: Color scheme for slides
            
        Returns:
            Result dictionary with output paths
        """
        # Validate inputs
        params = {
            'base_text': base_text,
            'num_slides': num_slides,
            'aspect_ratio': aspect_ratio,
            'style': style,
            'content_richness': content_richness,
            'color_scheme': color_scheme
        }
        
        valid, error = InputValidator.validate_parameters(params)
        if not valid:
            raise ValueError(f"Invalid parameters: {error}")
        
        # Validate configuration
        valid, error = config.validate()
        if not valid:
            raise ValueError(f"Invalid configuration: {error}")
        
        logger.info("=" * 60)
        logger.info("SLIDE GENERATION STARTED")
        logger.info("=" * 60)
        logger.info(f"Topic: {base_text[:80]}...")
        logger.info(f"Slides: {num_slides}")
        logger.info(f"Aspect Ratio: {aspect_ratio}")
        logger.info(f"Style: {style}")
        logger.info(f"Content Richness: {content_richness}")
        logger.info(f"Color Scheme: {color_scheme}")
        logger.info("=" * 60)
        
        # Initialize state
        initial_state: SlideGenerationState = {
            'base_text': base_text,
            'num_slides': num_slides,
            'aspect_ratio': aspect_ratio,
            'style': style,
            'content_richness': content_richness,
            'color_scheme': color_scheme,
            'outline': [],
            'current_slide_index': 0,
            'slides': [],
            'output_dir': str(config.output_dir),
            'pdf_path': None,
            'ppt_path': None,
            'errors': []
        }
        
        # Run workflow with appropriate recursion limit
        # Calculate required limit: 1 (outline) + num_slides * 4 (layout/images/html/increment) + 1 (export) + buffer
        recursion_limit = max(50, num_slides * 5 + 10)
        
        logger.debug(f"Setting recursion limit to {recursion_limit} for {num_slides} slides")
        
        final_state = self.workflow.invoke(
            initial_state,
            config={"recursion_limit": recursion_limit}
        )
        
        # Prepare result
        result = {
            'success': len(final_state.get('errors', [])) == 0,
            'output_path': str(config.output_dir),
            'pdf_path': final_state.get('pdf_path'),
            'ppt_path': final_state.get('ppt_path'),
            'slides_generated': len(final_state.get('slides', [])),
            'errors': final_state.get('errors', [])
        }
        
        logger.info("=" * 60)
        if result['success']:
            logger.info("✓ SLIDE GENERATION COMPLETED SUCCESSFULLY")
            logger.info("")
            logger.info("Generated Slides Overview:")
            for slide in final_state.get('slides', []):
                slide_num = slide.get('slide_number', '?')
                template = slide.get('template_type', 'unknown')
                title = slide.get('layout', {}).get('title', 'Untitled')
                logger.info(f"  Slide {slide_num}: [{template}] {title}")
            logger.info("")
            logger.info("Output Files:")
            if result.get('pdf_path'):
                logger.info(f"  PDF: {result['pdf_path']}")
            if result.get('ppt_path'):
                logger.info(f"  PPT: {result['ppt_path']}")
        else:
            logger.info("⚠ SLIDE GENERATION COMPLETED WITH ERRORS")
            for error in result['errors']:
                logger.error(f"  - {error}")
        logger.info("=" * 60)
        
        return result

