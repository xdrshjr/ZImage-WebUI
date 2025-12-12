"""
LangGraph agent for slide generation orchestration
"""

from .graph import SlideGenerationAgent
from .state import SlideGenerationState

__all__ = ["SlideGenerationAgent", "SlideGenerationState"]
