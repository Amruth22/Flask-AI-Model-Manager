"""
Workflow Templates
Pre-built workflow examples
"""

import logging

logger = logging.getLogger(__name__)


class WorkflowTemplates:
    """
    Pre-built workflow templates
    """
    
    @staticmethod
    def content_generation_workflow(model_name):
        """
        Content generation workflow: Generate -> Improve -> Format
        
        Args:
            model_name: Model to use
            
        Returns:
            Workflow steps
        """
        return [
            {
                'model': model_name,
                'prompt_template': 'Generate a short article about: {input}'
            },
            {
                'model': model_name,
                'prompt_template': 'Improve the following article by making it more engaging:\n\n{input}'
            },
            {
                'model': model_name,
                'prompt_template': 'Format the following article with proper headings and structure:\n\n{input}'
            }
        ]
    
    @staticmethod
    def translation_workflow(model_name):
        """
        Translation workflow: Translate -> Review -> Polish
        
        Args:
            model_name: Model to use
            
        Returns:
            Workflow steps
        """
        return [
            {
                'model': model_name,
                'prompt_template': 'Translate the following text to Spanish:\n\n{input}'
            },
            {
                'model': model_name,
                'prompt_template': 'Review this Spanish translation and fix any errors:\n\n{input}'
            },
            {
                'model': model_name,
                'prompt_template': 'Polish this Spanish text to make it sound more natural:\n\n{input}'
            }
        ]
    
    @staticmethod
    def analysis_workflow(model_name):
        """
        Analysis workflow: Extract -> Summarize -> Report
        
        Args:
            model_name: Model to use
            
        Returns:
            Workflow steps
        """
        return [
            {
                'model': model_name,
                'prompt_template': 'Extract the key points from the following text:\n\n{input}'
            },
            {
                'model': model_name,
                'prompt_template': 'Summarize these key points in 2-3 sentences:\n\n{input}'
            },
            {
                'model': model_name,
                'prompt_template': 'Create a brief report based on this summary:\n\n{input}'
            }
        ]
    
    @staticmethod
    def get_all_templates():
        """
        Get all available workflow templates
        
        Returns:
            Dictionary of template names and descriptions
        """
        return {
            'content_generation': 'Generate, improve, and format content',
            'translation': 'Translate, review, and polish text',
            'analysis': 'Extract, summarize, and report on text'
        }
