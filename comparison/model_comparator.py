"""
Model Comparator
Compare outputs from different AI models
"""

import logging
from comparison.comparison_store import ComparisonStore

logger = logging.getLogger(__name__)


class ModelComparator:
    """
    Compare multiple AI models side-by-side
    """
    
    def __init__(self, model_registry, db_path='ai_models.db'):
        """
        Initialize model comparator
        
        Args:
            model_registry: ModelRegistry instance
            db_path: Path to database file
        """
        self.model_registry = model_registry
        self.comparison_store = ComparisonStore(db_path)
        logger.info("Model comparator initialized")
    
    def compare_models(self, model_names, prompt):
        """
        Compare multiple models on same prompt
        
        Args:
            model_names: List of model names to compare
            prompt: Prompt to send to all models
            
        Returns:
            Dictionary with comparison results
        """
        logger.info(f"Comparing {len(model_names)} models")
        
        results = []
        
        for model_name in model_names:
            model = self.model_registry.get_model(model_name)
            
            if not model:
                logger.warning(f"Model not found: {model_name}")
                continue
            
            # Generate response
            result = model.generate(prompt)
            
            results.append({
                'model': model_name,
                'response': result['response'],
                'tokens': result['tokens'],
                'latency': result['latency'],
                'cost': result['cost']
            })
        
        # Determine winner (fastest with good quality)
        winner = self._determine_winner(results)
        
        # Store comparison
        if len(results) >= 2:
            self.comparison_store.store_comparison(prompt, results, winner)
        
        logger.info(f"Comparison completed. Winner: {winner}")
        
        return {
            'prompt': prompt,
            'results': results,
            'winner': winner,
            'comparison_metrics': self._calculate_metrics(results)
        }
    
    def _determine_winner(self, results):
        """
        Determine winner based on latency and cost
        
        Args:
            results: List of model results
            
        Returns:
            Winner model name
        """
        if not results:
            return None
        
        # Simple scoring: lower latency and cost is better
        best_score = float('inf')
        winner = None
        
        for result in results:
            # Score = latency + (cost * 1000)
            score = result['latency'] + (result['cost'] * 1000)
            
            if score < best_score:
                best_score = score
                winner = result['model']
        
        return winner
    
    def _calculate_metrics(self, results):
        """
        Calculate comparison metrics
        
        Args:
            results: List of model results
            
        Returns:
            Dictionary with metrics
        """
        if not results:
            return {}
        
        return {
            'avg_latency': sum(r['latency'] for r in results) / len(results),
            'avg_tokens': sum(r['tokens'] for r in results) / len(results),
            'avg_cost': sum(r['cost'] for r in results) / len(results),
            'fastest_model': min(results, key=lambda x: x['latency'])['model'],
            'cheapest_model': min(results, key=lambda x: x['cost'])['model']
        }
    
    def get_comparison_history(self, limit=10):
        """
        Get comparison history
        
        Args:
            limit: Number of records to retrieve
            
        Returns:
            List of past comparisons
        """
        return self.comparison_store.get_comparison_history(limit)
