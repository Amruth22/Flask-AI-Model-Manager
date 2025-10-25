"""
Experiment Manager
Manage A/B testing experiments
"""

import logging
from storage.database import get_connection

logger = logging.getLogger(__name__)


class ExperimentManager:
    """
    Manage A/B testing experiments
    """
    
    def __init__(self, db_path='ai_models.db'):
        """
        Initialize experiment manager
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Experiment manager initialized")
    
    def create_experiment(self, name, variant_a, variant_b):
        """
        Create a new A/B experiment
        
        Args:
            name: Experiment name
            variant_a: Model name for variant A
            variant_b: Model name for variant B
            
        Returns:
            Experiment ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO experiments (name, variant_a, variant_b, status)
            VALUES (?, ?, ?, 'active')
        ''', (name, variant_a, variant_b))
        
        experiment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Experiment created: {name} (ID: {experiment_id})")
        return experiment_id
    
    def record_result(self, experiment_id, variant, success, rating=None):
        """
        Record experiment result
        
        Args:
            experiment_id: Experiment ID
            variant: Variant name ('A' or 'B')
            success: Whether the result was successful
            rating: Optional user rating (1-5)
            
        Returns:
            Result ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO experiment_results (experiment_id, variant, success, rating)
            VALUES (?, ?, ?, ?)
        ''', (experiment_id, variant, success, rating))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.debug(f"Result recorded for experiment {experiment_id}")
        return result_id
    
    def get_experiment_stats(self, experiment_id):
        """
        Get experiment statistics
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Dictionary with statistics
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Get experiment info
        cursor.execute('''
            SELECT name, variant_a, variant_b, status
            FROM experiments
            WHERE id = ?
        ''', (experiment_id,))
        
        experiment = cursor.fetchone()
        
        if not experiment:
            conn.close()
            return None
        
        # Get variant A stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                AVG(rating) as avg_rating
            FROM experiment_results
            WHERE experiment_id = ? AND variant = 'A'
        ''', (experiment_id,))
        
        variant_a_stats = cursor.fetchone()
        
        # Get variant B stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                AVG(rating) as avg_rating
            FROM experiment_results
            WHERE experiment_id = ? AND variant = 'B'
        ''', (experiment_id,))
        
        variant_b_stats = cursor.fetchone()
        conn.close()
        
        # Calculate conversion rates
        variant_a_rate = 0.0
        if variant_a_stats['total'] > 0:
            variant_a_rate = (variant_a_stats['successes'] / variant_a_stats['total']) * 100
        
        variant_b_rate = 0.0
        if variant_b_stats['total'] > 0:
            variant_b_rate = (variant_b_stats['successes'] / variant_b_stats['total']) * 100
        
        # Determine winner
        winner = None
        if variant_a_rate > variant_b_rate:
            winner = 'A'
        elif variant_b_rate > variant_a_rate:
            winner = 'B'
        else:
            winner = 'Tie'
        
        return {
            'experiment_id': experiment_id,
            'name': experiment['name'],
            'variant_a': {
                'model': experiment['variant_a'],
                'total': variant_a_stats['total'],
                'successes': variant_a_stats['successes'],
                'conversion_rate': variant_a_rate,
                'avg_rating': variant_a_stats['avg_rating']
            },
            'variant_b': {
                'model': experiment['variant_b'],
                'total': variant_b_stats['total'],
                'successes': variant_b_stats['successes'],
                'conversion_rate': variant_b_rate,
                'avg_rating': variant_b_stats['avg_rating']
            },
            'winner': winner,
            'status': experiment['status']
        }
    
    def stop_experiment(self, experiment_id):
        """
        Stop an experiment
        
        Args:
            experiment_id: Experiment ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE experiments
            SET status = 'completed'
            WHERE id = ?
        ''', (experiment_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Experiment stopped: {experiment_id}")
    
    def list_experiments(self):
        """
        List all experiments
        
        Returns:
            List of experiments
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, variant_a, variant_b, status, created_at
            FROM experiments
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
