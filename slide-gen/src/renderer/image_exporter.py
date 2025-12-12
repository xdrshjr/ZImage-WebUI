"""
HTML to PNG image export using Playwright
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ImageExporter:
    """Exports HTML slides to PNG images"""
    
    def __init__(self):
        """Initialize image exporter"""
        self.dimensions = {
            "16:9": {"width": 1920, "height": 1080},
            "4:3": {"width": 1600, "height": 1200},
            "16:10": {"width": 1920, "height": 1200}
        }
    
    def export_html_to_image(
        self,
        html_path: Path,
        output_path: Path,
        aspect_ratio: str = "16:9"
    ) -> bool:
        """
        Export HTML file to PNG image
        
        Args:
            html_path: Path to HTML file
            output_path: Path for output PNG
            aspect_ratio: Aspect ratio for dimensions
            
        Returns:
            Success status
        """
        logger.debug(f"Exporting HTML to PNG: {html_path.name} -> {output_path.name}")
        logger.debug(f"Aspect ratio: {aspect_ratio}")
        
        try:
            # Use asyncio to run playwright
            asyncio.run(self._export_async(html_path, output_path, aspect_ratio))
            
            # Verify output
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.debug(f"✓ PNG exported successfully: {output_path.name} ({file_size / 1024:.2f} KB)")
                return True
            else:
                logger.error(f"PNG file was not created: {output_path.name}")
                return False
                
        except Exception as e:
            logger.error(f"Playwright export failed for {html_path.name}: {str(e)}")
            logger.info("Attempting fallback export method...")
            # Fallback: Try PIL-based screenshot (limited functionality)
            return self._fallback_export(html_path, output_path, aspect_ratio)
    
    async def _export_async(
        self,
        html_path: Path,
        output_path: Path,
        aspect_ratio: str
    ) -> None:
        """
        Async export using Playwright
        
        Args:
            html_path: Path to HTML file
            output_path: Path for output PNG
            aspect_ratio: Aspect ratio for dimensions
        """
        logger.debug("Using Playwright for HTML to PNG conversion")
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright is not installed")
            logger.info("Install it with: pip install playwright && playwright install chromium")
            raise
        
        dims = self.dimensions[aspect_ratio]
        logger.debug(f"Viewport size: {dims['width']}x{dims['height']}")
        
        async with async_playwright() as p:
            logger.debug("Launching Chromium browser...")
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={'width': dims['width'], 'height': dims['height']}
            )
            
            # Load HTML file
            html_url = f"file://{html_path.absolute()}"
            logger.debug(f"Loading HTML: {html_url}")
            await page.goto(html_url)
            
            # Wait for any images to load
            logger.debug("Waiting for page to load completely...")
            await page.wait_for_load_state('networkidle')
            
            # Take screenshot
            logger.debug(f"Taking screenshot: {output_path.name}")
            await page.screenshot(
                path=str(output_path),
                full_page=False
            )
            
            await browser.close()
            logger.debug("Browser closed")
    
    def _fallback_export(
        self,
        html_path: Path,
        output_path: Path,
        aspect_ratio: str
    ) -> bool:
        """
        Fallback export method using PIL (creates placeholder)
        
        NOTE: This creates a placeholder image and does NOT render actual HTML content.
        
        Args:
            html_path: Path to HTML file
            output_path: Path for output PNG
            aspect_ratio: Aspect ratio for dimensions
            
        Returns:
            Success status
        """
        logger.warning("Using PIL-based fallback for image export")
        logger.warning("This will create a PLACEHOLDER image, not actual HTML content!")
        logger.info("For proper rendering, ensure Playwright is installed: pip install playwright && playwright install chromium")
        
        try:
            from PIL import Image, ImageDraw
            
            dims = self.dimensions[aspect_ratio]
            logger.debug(f"Creating placeholder image at {dims['width']}x{dims['height']}")
            
            # Create placeholder image
            image = Image.new('RGB', (dims['width'], dims['height']), color='white')
            draw = ImageDraw.Draw(image)
            
            # Draw border
            draw.rectangle(
                [(0, 0), (dims['width'] - 1, dims['height'] - 1)],
                outline='gray',
                width=5
            )
            
            # Add text
            text = f"Slide Preview\n(Install Playwright for full rendering)"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (dims['width'] - text_width) // 2
            y = (dims['height'] - text_height) // 2
            
            draw.text((x, y), text, fill='gray')
            
            image.save(output_path)
            
            if output_path.exists():
                logger.warning(f"⚠ Created placeholder image: {output_path.name}")
                return True
            else:
                logger.error("Failed to save placeholder image")
                return False
            
        except ImportError:
            logger.error("PIL/Pillow is required for fallback image export")
            logger.error("Install it with: pip install Pillow")
            return False
        except Exception as e:
            logger.error(f"Fallback export failed: {str(e)}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return False

