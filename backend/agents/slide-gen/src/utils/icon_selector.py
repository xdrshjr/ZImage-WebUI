"""
Icon selection utility for slide content
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class IconSelector:
    """Select appropriate icons based on content context"""
    
    # Keyword mappings for section icon selection
    SECTION_KEYWORDS = {
        'icon-lightbulb': [
            'idea', 'concept', 'innovation', 'creative', 'insight', 'inspiration',
            'brainstorm', 'thinking', 'solution', 'approach', 'perspective'
        ],
        'icon-chart': [
            'data', 'analytics', 'metrics', 'results', 'statistics', 'analysis',
            'performance', 'measure', 'growth', 'trend', 'report', 'findings'
        ],
        'icon-target': [
            'goal', 'objective', 'aim', 'target', 'mission', 'purpose', 
            'achievement', 'milestone', 'outcome', 'focus', 'priority'
        ],
        'icon-book': [
            'learn', 'education', 'study', 'knowledge', 'research', 'academic',
            'literature', 'reference', 'theory', 'background', 'context', 'documentation'
        ],
        'icon-checkmark': [
            'benefit', 'advantage', 'feature', 'success', 'achievement', 'complete',
            'done', 'verified', 'approved', 'positive', 'win', 'accomplish'
        ],
        'icon-rocket': [
            'launch', 'start', 'begin', 'initiate', 'deploy', 'implementation',
            'startup', 'kickoff', 'momentum', 'acceleration', 'growth'
        ],
        'icon-trophy': [
            'award', 'achievement', 'excellence', 'winner', 'best', 'champion',
            'success', 'recognition', 'accomplishment', 'reward'
        ],
        'icon-flag': [
            'milestone', 'marker', 'checkpoint', 'indicator', 'highlight',
            'important', 'note', 'attention', 'key point'
        ],
        'icon-users': [
            'team', 'group', 'people', 'collaboration', 'community', 'social',
            'stakeholder', 'audience', 'participant', 'user', 'customer'
        ],
        'icon-brain': [
            'intelligence', 'cognitive', 'mental', 'thinking', 'mind', 'smart',
            'ai', 'artificial', 'neural', 'learning', 'reasoning'
        ],
        'icon-code': [
            'programming', 'software', 'development', 'code', 'coding', 'technical',
            'algorithm', 'script', 'implementation', 'engineering'
        ],
        'icon-clipboard': [
            'checklist', 'task', 'todo', 'list', 'requirement', 'specification',
            'criteria', 'plan', 'agenda', 'outline'
        ],
        'icon-puzzle': [
            'problem', 'challenge', 'solution', 'complexity', 'component',
            'piece', 'integration', 'system', 'architecture'
        ],
        'icon-key': [
            'essential', 'critical', 'important', 'core', 'fundamental', 'primary',
            'access', 'unlock', 'enable', 'security'
        ],
        'icon-shield': [
            'security', 'protection', 'safety', 'defense', 'guard', 'secure',
            'privacy', 'safeguard', 'risk', 'compliance'
        ],
        'icon-globe': [
            'global', 'world', 'international', 'worldwide', 'universal', 'network',
            'internet', 'web', 'online', 'geography'
        ],
        'icon-search': [
            'find', 'discover', 'explore', 'investigate', 'research', 'query',
            'locate', 'identify', 'examine', 'inspect'
        ],
        'icon-document': [
            'document', 'file', 'paper', 'record', 'report', 'publication',
            'article', 'content', 'text', 'material'
        ],
        'icon-heart': [
            'favorite', 'like', 'love', 'passion', 'care', 'value',
            'preference', 'important', 'priority', 'emotion'
        ],
        'icon-database': [
            'storage', 'database', 'repository', 'archive', 'collection',
            'dataset', 'information', 'record', 'warehouse'
        ],
        'icon-link': [
            'connection', 'relationship', 'link', 'network', 'integration',
            'association', 'connect', 'tie', 'bridge'
        ],
        'icon-warning': [
            'warning', 'caution', 'alert', 'danger', 'risk', 'issue',
            'problem', 'concern', 'limitation', 'constraint'
        ],
        'icon-info': [
            'information', 'detail', 'about', 'description', 'explanation',
            'overview', 'summary', 'introduction', 'background'
        ],
        'icon-success': [
            'success', 'complete', 'finished', 'done', 'achieved', 'accomplished',
            'result', 'outcome', 'victory', 'resolution'
        ],
        'icon-tools': [
            'tool', 'utility', 'instrument', 'resource', 'method', 'technique',
            'mechanism', 'process', 'workflow', 'framework'
        ],
        'icon-settings': [
            'configuration', 'setting', 'option', 'preference', 'parameter',
            'control', 'adjustment', 'customize', 'setup'
        ],
        'icon-star': [
            'featured', 'highlight', 'special', 'premium', 'quality', 'excellent',
            'rating', 'favorite', 'top', 'outstanding'
        ]
    }
    
    # Default icon for bullet points (used in CSS)
    DEFAULT_BULLET_ICON = 'icon-circle'
    
    # Default icon for sections when no match found
    DEFAULT_SECTION_ICON = 'icon-arrow-right'
    
    @staticmethod
    def select_icon_for_section(section_title: str) -> str:
        """
        Select appropriate icon based on section title keywords
        
        Args:
            section_title: The section title text to analyze
            
        Returns:
            Icon ID string (e.g., 'icon-lightbulb')
        """
        if not section_title:
            logger.debug("Empty section title, using default icon")
            return IconSelector.DEFAULT_SECTION_ICON
        
        title_lower = section_title.lower()
        
        # Check each icon's keywords
        for icon, keywords in IconSelector.SECTION_KEYWORDS.items():
            if any(keyword in title_lower for keyword in keywords):
                logger.debug(f"Icon '{icon}' selected for section: '{section_title}'")
                return icon
        
        # No match found, use default
        logger.debug(f"No icon match for section: '{section_title}', using default")
        return IconSelector.DEFAULT_SECTION_ICON
    
    @staticmethod
    def select_icons_for_content_blocks(content_blocks: List[Dict]) -> List[Dict]:
        """
        Process content blocks and add icon selections
        
        Args:
            content_blocks: List of content block dictionaries
            
        Returns:
            Updated content blocks with 'icon' field added to text blocks
        """
        updated_blocks = []
        
        for block in content_blocks:
            # Create a copy to avoid modifying original
            updated_block = dict(block)
            
            # Only process text blocks with section titles
            if block.get('type') == 'text' and block.get('section_title'):
                section_title = block.get('section_title', '')
                selected_icon = IconSelector.select_icon_for_section(section_title)
                updated_block['icon'] = selected_icon
                logger.debug(f"Added icon '{selected_icon}' to text block: {section_title[:50]}...")
            
            updated_blocks.append(updated_block)
        
        return updated_blocks
    
    @staticmethod
    def get_all_available_icons() -> List[str]:
        """
        Get list of all available icon IDs
        
        Returns:
            List of icon ID strings
        """
        return list(IconSelector.SECTION_KEYWORDS.keys())
    
    @staticmethod
    def get_icon_description(icon_id: str) -> str:
        """
        Get a human-readable description of what an icon represents
        
        Args:
            icon_id: The icon ID (e.g., 'icon-lightbulb')
            
        Returns:
            Description string
        """
        keywords = IconSelector.SECTION_KEYWORDS.get(icon_id, [])
        if keywords:
            return f"Icon for: {', '.join(keywords[:5])}"
        return "Generic icon"
    
    @staticmethod
    def suggest_icon(keywords: List[str]) -> str:
        """
        Suggest an icon based on a list of keywords
        
        Args:
            keywords: List of keyword strings
            
        Returns:
            Suggested icon ID
        """
        # Count matches for each icon
        icon_scores: Dict[str, int] = {}
        
        for icon, icon_keywords in IconSelector.SECTION_KEYWORDS.items():
            score = sum(1 for kw in keywords if any(ikw in kw.lower() for ikw in icon_keywords))
            if score > 0:
                icon_scores[icon] = score
        
        if icon_scores:
            # Return icon with highest score
            best_icon = max(icon_scores.items(), key=lambda x: x[1])[0]
            logger.debug(f"Suggested icon '{best_icon}' based on keywords: {keywords}")
            return best_icon
        
        return IconSelector.DEFAULT_SECTION_ICON

