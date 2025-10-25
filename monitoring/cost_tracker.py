"""
Cost Tracker
Track API costs for AI models
"""

import logging
from datetime import datetime, timedelta
from storage.database import get_connection

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Track API costs for AI models
    """
    
    def __init__(self, db_path='ai_models.db'):
        """
        Initialize cost tracker
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Cost tracker initialized")
    
    def track_cost(self, model_id, cost, tokens):
        """
        Track API cost
        
        Args:
            model_id: Model ID
            cost: Cost in USD
            tokens: Token count
            
        Returns:
            Cost record ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO costs (model_id, cost, tokens)
            VALUES (?, ?, ?)
        ''', (model_id, cost, tokens))
        
        cost_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.debug(f"Cost tracked: ${cost:.6f} for {tokens} tokens")
        return cost_id
    
    def get_model_costs(self, model_name):
        """
        Get total costs for a model
        
        Args:
            model_name: Model name
            
        Returns:
            Dictionary with cost statistics
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Get model ID
        cursor.execute('SELECT id FROM models WHERE name = ?', (model_name,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        model_id = result['id']
        
        # Get cost statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                SUM(cost) as total_cost,
                AVG(cost) as avg_cost,
                SUM(tokens) as total_tokens
            FROM costs
            WHERE model_id = ?
        ''', (model_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'model_name': model_name,
            'total_requests': stats['total_requests'],
            'total_cost': round(stats['total_cost'] or 0.0, 6),
            'avg_cost': round(stats['avg_cost'] or 0.0, 6),
            'total_tokens': stats['total_tokens'] or 0
        }
    
    def get_all_costs(self):
        """
        Get costs for all models
        
        Returns:
            List of model costs
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM models')
        models = cursor.fetchall()
        conn.close()
        
        costs = []
        for model in models:
            model_costs = self.get_model_costs(model['name'])
            if model_costs and model_costs['total_requests'] > 0:
                costs.append(model_costs)
        
        return costs
    
    def get_daily_costs(self, days=7):
        """
        Get daily costs for last N days
        
        Args:
            days: Number of days
            
        Returns:
            List of daily cost summaries
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                SUM(cost) as total_cost,
                SUM(tokens) as total_tokens,
                COUNT(*) as requests
            FROM costs
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''', (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_total_cost(self):
        """
        Get total cost across all models
        
        Returns:
            Total cost in USD
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(cost) as total FROM costs')
        result = cursor.fetchone()
        conn.close()
        
        return round(result['total'] or 0.0, 6)
    
    def check_budget_alert(self, budget_limit):
        """
        Check if costs exceed budget
        
        Args:
            budget_limit: Budget limit in USD
            
        Returns:
            True if over budget, False otherwise
        """
        total_cost = self.get_total_cost()
        
        if total_cost > budget_limit:
            logger.warning(f"Budget exceeded: ${total_cost:.2f} > ${budget_limit:.2f}")
            return True
        
        return False
