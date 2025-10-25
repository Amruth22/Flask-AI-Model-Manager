"""
Comparison Store
Store and retrieve model comparison results
"""

import logging
from storage.database import get_connection

logger = logging.getLogger(__name__)


class ComparisonStore:
    """
    Store model comparison results in database
    """
    
    def __init__(self, db_path='ai_models.db'):
        """
        Initialize comparison store
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
    
    def store_comparison(self, prompt, results, winner):
        """
        Store comparison results
        
        Args:
            prompt: Prompt used for comparison
            results: List of model results
            winner: Winner model name
            
        Returns:
            Comparison ID
        """
        if len(results) < 2:
            logger.warning("Need at least 2 results for comparison")
            return None
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Get model IDs
        model1_name = results[0]['model']
        model2_name = results[1]['model']
        
        cursor.execute('SELECT id FROM models WHERE name = ?', (model1_name,))
        model1_id = cursor.fetchone()['id']
        
        cursor.execute('SELECT id FROM models WHERE name = ?', (model2_name,))
        model2_id = cursor.fetchone()['id']
        
        # Store comparison
        cursor.execute('''
            INSERT INTO comparisons (
                prompt, model1_id, model2_id,
                model1_response, model2_response,
                model1_latency, model2_latency,
                model1_tokens, model2_tokens,
                winner
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prompt,
            model1_id, model2_id,
            results[0]['response'], results[1]['response'],
            results[0]['latency'], results[1]['latency'],
            results[0]['tokens'], results[1]['tokens'],
            winner
        ))
        
        comparison_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Comparison stored: {comparison_id}")
        return comparison_id
    
    def get_comparison_history(self, limit=10):
        """
        Get comparison history
        
        Args:
            limit: Number of records to retrieve
            
        Returns:
            List of comparisons
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.id, c.prompt, c.winner, c.timestamp,
                m1.name as model1_name, m2.name as model2_name,
                c.model1_latency, c.model2_latency,
                c.model1_tokens, c.model2_tokens
            FROM comparisons c
            JOIN models m1 ON c.model1_id = m1.id
            JOIN models m2 ON c.model2_id = m2.id
            ORDER BY c.timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_model_win_rate(self, model_name):
        """
        Get win rate for a model
        
        Args:
            model_name: Model name
            
        Returns:
            Win rate percentage
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Total comparisons
        cursor.execute('''
            SELECT COUNT(*) as total
            FROM comparisons c
            JOIN models m1 ON c.model1_id = m1.id
            JOIN models m2 ON c.model2_id = m2.id
            WHERE m1.name = ? OR m2.name = ?
        ''', (model_name, model_name))
        
        total = cursor.fetchone()['total']
        
        if total == 0:
            return 0.0
        
        # Wins
        cursor.execute('''
            SELECT COUNT(*) as wins
            FROM comparisons
            WHERE winner = ?
        ''', (model_name,))
        
        wins = cursor.fetchone()['wins']
        conn.close()
        
        return (wins / total) * 100
