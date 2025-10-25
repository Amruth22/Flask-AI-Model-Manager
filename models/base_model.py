"""
Base Model
Abstract base class for all AI models
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for AI models
    Provides common interface for all model implementations
    """
    
    def __init__(self, name, provider, cost_per_token=0.0):
        """
        Initialize base model
        
        Args:
            name: Model name
            provider: Provider name (e.g., 'Google', 'OpenAI')
            cost_per_token: Cost per token in USD
        """
        self.name = name
        self.provider = provider
        self.cost_per_token = cost_per_token
        logger.info(f"Model initialized: {name} ({provider})")
    
    @abstractmethod
    def generate(self, prompt, **kwargs):
        """
        Generate text from prompt
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def generate_stream(self, prompt, **kwargs):
        """
        Generate text with streaming
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Yields:
            Text chunks
        """
        pass
    
    def count_tokens(self, text):
        """
        Count tokens in text (simple approximation)
        
        Args:
            text: Input text
            
        Returns:
            Approximate token count
        """
        # Simple approximation: 1 token ~ 4 characters
        return len(text) // 4
    
    def calculate_cost(self, tokens):
        """
        Calculate cost for token count
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Cost in USD
        """
        return tokens * self.cost_per_token
    
    def get_info(self):
        """
        Get model information
        
        Returns:
            Dictionary with model info
        """
        return {
            'name': self.name,
            'provider': self.provider,
            'cost_per_token': self.cost_per_token
        }
