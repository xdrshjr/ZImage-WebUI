"""
Input validation utilities
"""

from typing import Dict, Any, Optional


class InputValidator:
    """Validates input parameters for slide generation"""
    
    VALID_ASPECT_RATIOS = ["16:9", "4:3", "16:10"]
    VALID_STYLES = ["professional", "creative", "minimal", "academic"]
    VALID_CONTENT_RICHNESS = ["concise", "moderate", "detailed"]
    
    @staticmethod
    def validate_parameters(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate slide generation parameters
        
        Args:
            params: Dictionary of input parameters
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check required parameters
        required = ["base_text", "num_slides", "aspect_ratio", "style", "content_richness"]
        for param in required:
            if param not in params:
                return False, f"Missing required parameter: {param}"
        
        # Validate base_text
        if not isinstance(params["base_text"], str) or not params["base_text"].strip():
            return False, "base_text must be a non-empty string"
        
        # Validate num_slides
        if not isinstance(params["num_slides"], int):
            return False, "num_slides must be an integer"
        
        if params["num_slides"] < 1 or params["num_slides"] > 50:
            return False, "num_slides must be between 1 and 50"
        
        # Validate aspect_ratio
        if params["aspect_ratio"] not in InputValidator.VALID_ASPECT_RATIOS:
            return False, f"aspect_ratio must be one of {InputValidator.VALID_ASPECT_RATIOS}"
        
        # Validate style
        if params["style"] not in InputValidator.VALID_STYLES:
            return False, f"style must be one of {InputValidator.VALID_STYLES}"
        
        # Validate content_richness
        if params["content_richness"] not in InputValidator.VALID_CONTENT_RICHNESS:
            return False, f"content_richness must be one of {InputValidator.VALID_CONTENT_RICHNESS}"
        
        return True, None
    
    @staticmethod
    def validate_text_length(text: str, max_length: int, field_name: str = "Text") -> tuple[bool, Optional[str]]:
        """
        Validate text length against character limit
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            field_name: Name of the field for error message
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(text) > max_length:
            return False, f"{field_name} exceeds maximum length of {max_length} characters (current: {len(text)})"
        return True, None
    
    @staticmethod
    def truncate_text(text: str, max_length: int) -> str:
        """
        Truncate text to maximum length with ellipsis
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

