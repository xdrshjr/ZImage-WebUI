"""
Input validation utilities
"""

from typing import Dict, Any, Optional


class ColorScheme:
    """Color scheme definitions with background and text colors"""
    
    # Define color schemes: name -> (background_color, text_color, accent_color)
    SCHEMES = {
        "light_blue": {
            "name": "Light Blue",
            "background": "#f0f7ff",
            "text": "#1a2332",
            "accent": "#0071e3",
            "header": "#4c9eff"
        },
        "dark_slate": {
            "name": "Dark Slate",
            "background": "#1e293b",
            "text": "#f1f5f9",
            "accent": "#38bdf8",
            "header": "#94a3b8"
        },
        "warm_cream": {
            "name": "Warm Cream",
            "background": "#fef6e4",
            "text": "#2d2424",
            "accent": "#f582ae",
            "header": "#8d5b4c"
        },
        "dark_navy": {
            "name": "Dark Navy",
            "background": "#0f172a",
            "text": "#e2e8f0",
            "accent": "#60a5fa",
            "header": "#cbd5e1"
        },
        "soft_green": {
            "name": "Soft Green",
            "background": "#f0fdf4",
            "text": "#14532d",
            "accent": "#22c55e",
            "header": "#16a34a"
        }
    }
    
    @staticmethod
    def get_scheme(scheme_name: str) -> Dict[str, str]:
        """
        Get color scheme by name
        
        Args:
            scheme_name: Name of the color scheme
            
        Returns:
            Dictionary with color values
        """
        return ColorScheme.SCHEMES.get(scheme_name, ColorScheme.SCHEMES["light_blue"])
    
    @staticmethod
    def get_available_schemes() -> list:
        """
        Get list of available color scheme names
        
        Returns:
            List of scheme names
        """
        return list(ColorScheme.SCHEMES.keys())


class InputValidator:
    """Validates input parameters for slide generation"""
    
    VALID_ASPECT_RATIOS = ["16:9", "4:3", "16:10"]
    VALID_STYLES = ["professional", "creative", "minimal", "academic"]
    VALID_CONTENT_RICHNESS = ["concise", "moderate", "detailed"]
    VALID_COLOR_SCHEMES = ColorScheme.get_available_schemes()
    
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
        
        # Validate color_scheme (optional parameter)
        if "color_scheme" in params and params["color_scheme"]:
            if params["color_scheme"] not in InputValidator.VALID_COLOR_SCHEMES:
                return False, f"color_scheme must be one of {InputValidator.VALID_COLOR_SCHEMES}"
        
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


