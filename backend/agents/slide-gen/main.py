"""
Main entry point for intelligent slide generation system
"""

import os
import logging
import sys
from pathlib import Path
from colorlog import ColoredFormatter

# Set USE_BRIDGE to false for standalone execution (before importing any modules)
# This ensures the agent uses HTTP API calls instead of the internal bridge
os.environ["USE_BRIDGE"] = "false"

from src.agent.graph import SlideGenerationAgent


def setup_logging():
    """Configure logging with colored output"""
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Set level for specific modules
    logging.getLogger('src').setLevel(logging.INFO)


def main():
    """Main execution function"""
    # Setup logging
    setup_logging()
    
    logger = logging.getLogger(__name__)
    
    # Hardcoded test parameters
    params = {
        "base_text": "Introduction to Artificial Intelligence and its applications in modern technology",
        "num_slides": 6,
        "aspect_ratio": "16:9",
        "style": "professional",
        "content_richness": "moderate"
    }
    
    logger.info("="*60)
    logger.info("INTELLIGENT SLIDE GENERATION SYSTEM")
    logger.info("="*60)
    logger.info("")
    
    try:
        # Initialize agent
        agent = SlideGenerationAgent()
        
        # Generate slides
        result = agent.generate_slides(**params)
        
        # Display results
        print("\n")
        logger.info("="*60)
        logger.info("GENERATION COMPLETE")
        logger.info("="*60)
        
        if result['success']:
            logger.info(f"✓ Slides generated successfully!")
            logger.info(f"✓ Total slides: {result['slides_generated']}")
            logger.info(f"✓ Output location: {result['output_path']}")
            
            if result.get('pdf_path'):
                logger.info(f"✓ PDF: {result['pdf_path']}")
            
            logger.info("")
            logger.info("Output files:")
            logger.info(f"  - HTML slides: {Path(result['output_path']) / 'html'}")
            logger.info(f"  - Generated images: {Path(result['output_path']) / 'images'}")
            logger.info(f"  - Slide PNGs: {Path(result['output_path']) / 'slide_images'}")
            logger.info(f"  - Final PDF: {result.get('pdf_path', 'N/A')}")
            
        else:
            logger.error("⚠ Generation completed with errors:")
            for error in result.get('errors', []):
                logger.error(f"  - {error}")
            sys.exit(1)
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        logger.error("Please check your .env file and input parameters")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

