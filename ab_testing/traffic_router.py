"""
Traffic Router
Route requests to A/B test variants
"""

import logging
import hashlib

logger = logging.getLogger(__name__)


class TrafficRouter:
    """
    Route traffic to A/B test variants
    """
    
    def __init__(self, model_registry):
        """
        Initialize traffic router
        
        Args:
            model_registry: ModelRegistry instance
        """
        self.model_registry = model_registry
        logger.info("Traffic router initialized")
    
    def route_request(self, user_id, variant_a_model, variant_b_model, split=50):
        """
        Route request to variant based on user ID
        
        Args:
            user_id: User identifier (for consistent routing)
            variant_a_model: Model name for variant A
            variant_b_model: Model name for variant B
            split: Percentage for variant A (0-100)
            
        Returns:
            Tuple of (variant_name, model)
        """
        # Hash user ID for consistent assignment
        hash_value = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
        percentage = hash_value % 100
        
        if percentage < split:
            # Variant A
            model = self.model_registry.get_model(variant_a_model)
            variant = 'A'
        else:
            # Variant B
            model = self.model_registry.get_model(variant_b_model)
            variant = 'B'
        
        logger.debug(f"User {user_id} routed to variant {variant}")
        
        return variant, model
    
    def generate_with_routing(self, user_id, prompt, variant_a_model, variant_b_model, split=50):
        """
        Generate text with A/B routing
        
        Args:
            user_id: User identifier
            prompt: Input prompt
            variant_a_model: Model name for variant A
            variant_b_model: Model name for variant B
            split: Percentage for variant A (0-100)
            
        Returns:
            Dictionary with variant, response, and metrics
        """
        variant, model = self.route_request(user_id, variant_a_model, variant_b_model, split)
        
        if not model:
            raise ValueError(f"Model not found for variant {variant}")
        
        # Generate response
        result = model.generate(prompt)
        
        return {
            'variant': variant,
            'model': model.name,
            'response': result['response'],
            'tokens': result['tokens'],
            'latency': result['latency'],
            'cost': result['cost']
        }
