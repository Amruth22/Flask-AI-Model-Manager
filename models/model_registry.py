"""
Model Registry
Register and manage AI models
"""

import logging
from storage.database import get_connection

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Registry for managing AI models
    """
    
    def __init__(self, db_path='ai_models.db'):
        """
        Initialize model registry
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.models = {}
        logger.info("Model registry initialized")
    
    def register_model(self, model):
        """
        Register a model
        
        Args:
            model: Model instance (BaseModel subclass)
            
        Returns:
            Model ID
        """
        # Store in memory
        self.models[model.name] = model
        
        # Store in database
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO models (name, provider, cost_per_token)
            VALUES (?, ?, ?)
        ''', (model.name, model.provider, model.cost_per_token))
        
        model_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Model registered: {model.name}")
        return model_id
    
    def get_model(self, name):
        """
        Get model by name
        
        Args:
            name: Model name
            
        Returns:
            Model instance or None
        """
        return self.models.get(name)
    
    def list_models(self):
        """
        List all registered models
        
        Returns:
            List of model names
        """
        return list(self.models.keys())
    
    def get_model_info(self, name):
        """
        Get model information
        
        Args:
            name: Model name
            
        Returns:
            Dictionary with model info
        """
        model = self.get_model(name)
        if model:
            return model.get_info()
        return None
    
    def get_model_id(self, name):
        """
        Get model ID from database
        
        Args:
            name: Model name
            
        Returns:
            Model ID or None
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM models WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result['id']
        return None
