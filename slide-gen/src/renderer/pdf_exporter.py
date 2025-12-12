"""
PDF export from HTML slides
"""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class PDFExporter:
    """Exports HTML slides to multi-page PDF"""
    
    def __init__(self):
        """Initialize PDF exporter"""
        pass
    
    def export_to_pdf(
        self,
        html_files: List[Path],
        output_path: Path,
        aspect_ratio: str = "16:9",
        image_files: Optional[List[Path]] = None
    ) -> bool:
        """
        Export HTML slides to PDF
        
        Args:
            html_files: List of HTML file paths (in order)
            output_path: Path for output PDF
            aspect_ratio: Aspect ratio for page dimensions
            image_files: Optional list of pre-rendered PNG images to use instead
            
        Returns:
            Success status
        """
        # If pre-rendered PNG images are provided, use them directly
        if image_files and all(img.exists() for img in image_files):
            logger.info(f"Using {len(image_files)} pre-rendered PNG images for PDF generation")
            logger.debug(f"Image files: {[img.name for img in image_files]}")
            return self._export_from_images(image_files, output_path)
        
        if not html_files:
            logger.error("No HTML files provided for PDF export")
            return False
        
        logger.info(f"Attempting PDF export from {len(html_files)} HTML files")
        logger.debug(f"HTML files: {[html.name for html in html_files]}")
        
        try:
            return self._export_with_weasyprint(html_files, output_path, aspect_ratio)
        except Exception as e:
            logger.error(f"WeasyPrint export failed: {str(e)}")
            logger.info("Attempting alternative PDF export method...")
            return self._export_with_alternative(html_files, output_path, aspect_ratio)
    
    def _export_from_images(
        self,
        image_files: List[Path],
        output_path: Path
    ) -> bool:
        """
        Export PNG images directly to PDF
        
        This method combines pre-rendered PNG slide images into a single PDF.
        This is more reliable than HTML-to-PDF conversion when the images are already generated.
        
        Args:
            image_files: List of PNG file paths (in order)
            output_path: Output PDF path
            
        Returns:
            Success status
        """
        try:
            from PIL import Image
            
            logger.info(f"Starting PDF generation from {len(image_files)} PNG images")
            logger.debug(f"Output path: {output_path}")
            
            # Load all images
            images = []
            for i, img_path in enumerate(image_files):
                try:
                    logger.debug(f"Loading image {i+1}/{len(image_files)}: {img_path.name}")
                    img = Image.open(img_path)
                    
                    # Convert to RGB if necessary (PDFs require RGB mode)
                    if img.mode != 'RGB':
                        logger.debug(f"Converting image {i+1} from {img.mode} to RGB mode")
                        img = img.convert('RGB')
                    
                    images.append(img)
                    logger.debug(f"Successfully loaded image {i+1}, size: {img.size}")
                    
                except Exception as e:
                    logger.error(f"Failed to load image {img_path.name}: {str(e)}")
                    return False
            
            if not images:
                logger.error("No images were successfully loaded")
                return False
            
            # Save as PDF
            logger.info(f"Combining {len(images)} images into PDF...")
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:] if len(images) > 1 else [],
                resolution=100.0,
                quality=95
            )
            
            # Verify PDF was created
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"✓ PDF successfully generated: {output_path}")
                logger.info(f"  File size: {file_size / 1024:.2f} KB")
                logger.info(f"  Total pages: {len(images)}")
                return True
            else:
                logger.error("PDF file was not created")
                return False
            
        except ImportError:
            logger.error("PIL/Pillow is required for image-to-PDF conversion")
            logger.error("Install it with: pip install Pillow")
            return False
        except Exception as e:
            logger.error(f"Failed to create PDF from images: {str(e)}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _export_with_weasyprint(
        self,
        html_files: List[Path],
        output_path: Path,
        aspect_ratio: str
    ) -> bool:
        """
        Export using WeasyPrint
        
        Args:
            html_files: List of HTML files
            output_path: Output PDF path
            aspect_ratio: Aspect ratio
            
        Returns:
            Success status
        """
        logger.info("Attempting PDF export using WeasyPrint")
        logger.debug(f"Aspect ratio: {aspect_ratio}, Output: {output_path.name}")
        
        try:
            from weasyprint import HTML, CSS
        except ImportError:
            logger.error("WeasyPrint is not installed")
            logger.info("Install it with: pip install weasyprint")
            raise
        
        # Dimensions in mm (A4 landscape approximation for 16:9)
        dimensions = {
            "16:9": {"width": "297mm", "height": "167mm"},
            "4:3": {"width": "280mm", "height": "210mm"},
            "16:10": {"width": "297mm", "height": "185mm"}
        }
        
        dims = dimensions.get(aspect_ratio, dimensions["16:9"])
        logger.debug(f"Using dimensions: {dims['width']} x {dims['height']}")
        
        # Create CSS for page size
        page_css = CSS(string=f'''
            @page {{
                size: {dims['width']} {dims['height']};
                margin: 0;
            }}
            body {{
                margin: 0;
                padding: 0;
            }}
        ''')
        
        logger.info(f"Exporting {len(html_files)} HTML slides to PDF...")
        
        # More reliable: render each separately and combine
        from PyPDF2 import PdfMerger
        merger = PdfMerger()
        
        temp_pdfs = []
        for i, html_file in enumerate(html_files):
            logger.debug(f"Processing HTML file {i+1}/{len(html_files)}: {html_file.name}")
            
            temp_pdf = output_path.parent / f"temp_slide_{i}.pdf"
            html_content = html_file.read_text(encoding='utf-8')
            html_content = self._fix_image_paths(html_content, html_file.parent)
            
            logger.debug(f"Writing temporary PDF: {temp_pdf.name}")
            HTML(string=html_content, base_url=str(html_file.parent)).write_pdf(
                temp_pdf,
                stylesheets=[page_css]
            )
            merger.append(str(temp_pdf))
            temp_pdfs.append(temp_pdf)
            logger.debug(f"✓ Slide {i+1} converted to PDF")
        
        logger.info("Merging individual PDFs...")
        merger.write(str(output_path))
        merger.close()
        
        # Clean up temp files
        logger.debug("Cleaning up temporary PDF files...")
        for temp_pdf in temp_pdfs:
            temp_pdf.unlink(missing_ok=True)
        
        # Verify output
        if output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"✓ PDF exported successfully using WeasyPrint: {output_path.name}")
            logger.info(f"  File size: {file_size / 1024:.2f} KB")
            return True
        else:
            logger.error("PDF file was not created")
            return False
    
    def _export_with_alternative(
        self,
        html_files: List[Path],
        output_path: Path,
        aspect_ratio: str
    ) -> bool:
        """
        Alternative export using PIL to create PDF from placeholder images
        
        NOTE: This creates simple placeholder pages and should only be used as a last resort.
        It does NOT render the actual HTML content.
        
        Args:
            html_files: List of HTML files
            output_path: Output PDF path
            aspect_ratio: Aspect ratio
            
        Returns:
            Success status
        """
        logger.warning("Using PIL-based fallback PDF export")
        logger.warning("This will create PLACEHOLDER pages with only slide numbers!")
        logger.info("For full HTML rendering, please ensure WeasyPrint is properly installed")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create simple placeholder pages
            dimensions = {
                "16:9": (1920, 1080),
                "4:3": (1600, 1200),
                "16:10": (1920, 1200)
            }
            
            dims = dimensions.get(aspect_ratio, dimensions["16:9"])
            logger.debug(f"Creating placeholder images at {dims[0]}x{dims[1]}")
            
            images = []
            for i, html_file in enumerate(html_files):
                logger.debug(f"Creating placeholder for slide {i+1}")
                
                img = Image.new('RGB', dims, color='white')
                draw = ImageDraw.Draw(img)
                
                # Draw border
                draw.rectangle(
                    [(10, 10), (dims[0] - 10, dims[1] - 10)],
                    outline='gray',
                    width=3
                )
                
                # Add text
                text = f"Slide {i + 1}"
                draw.text(
                    (dims[0] // 2 - 100, dims[1] // 2),
                    text,
                    fill='black'
                )
                
                images.append(img)
            
            if images:
                logger.info(f"Saving {len(images)} placeholder pages to PDF...")
                images[0].save(
                    output_path,
                    save_all=True,
                    append_images=images[1:] if len(images) > 1 else [],
                    resolution=100.0
                )
                
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    logger.warning(f"⚠ PDF created with PLACEHOLDERS only: {output_path.name}")
                    logger.info(f"  File size: {file_size / 1024:.2f} KB")
                    return True
            
            logger.error("Failed to create placeholder images")
            return False
            
        except ImportError:
            logger.error("PIL/Pillow is required for fallback PDF export")
            logger.error("Install it with: pip install Pillow")
            return False
        except Exception as e:
            logger.error(f"Alternative PDF export failed: {str(e)}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _fix_image_paths(self, html_content: str, base_path: Path) -> str:
        """
        Convert relative image paths to absolute paths
        
        Args:
            html_content: HTML content string
            base_path: Base path for relative paths
            
        Returns:
            Modified HTML content
        """
        import re
        
        def replace_path(match):
            rel_path = match.group(1)
            if not rel_path.startswith(('http://', 'https://', 'file://')):
                abs_path = (base_path / rel_path).resolve()
                return f'src="file://{abs_path}"'
            return match.group(0)
        
        return re.sub(r'src="([^"]+)"', replace_path, html_content)

