"""
Metrics Tracker
Track performance metrics for AI models
"""

import logging
from storage.database import get_connection

logger = logging.getLogger(__name__)


class MetricsTracker:
    """
    Track performance metrics for AI models
    """
    
    def __init__(self, db_path='ai_models.db'):
        """
        Initialize metrics tracker
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Metrics tracker initialized")
    
    def track_metric(self, model_id, metric_name, metric_value):
        """
        Track a metric
        
        Args:
            model_id: Model ID
            metric_name: Metric name (e.g., 'latency', 'tokens')
            metric_value: Metric value
            
        Returns:
            Metric ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (model_id, metric_name, metric_value)
            VALUES (?, ?, ?)
        ''', (model_id, metric_name, metric_value))
        
        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.debug(f"Metric tracked: {metric_name} = {metric_value}")
        return metric_id
    
    def get_model_metrics(self, model_name):
        """
        Get metrics for a model
        
        Args:
            model_name: Model name
            
        Returns:
            Dictionary with aggregated metrics
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
        
        # Get total requests
        cursor.execute('''
            SELECT COUNT(*) as total_requests
            FROM requests
            WHERE model_id = ?
        ''', (model_id,))
        
        total_requests = cursor.fetchone()['total_requests']
        
        # Get average latency
        cursor.execute('''
            SELECT AVG(latency) as avg_latency
            FROM responses
            WHERE request_id IN (
                SELECT id FROM requests WHERE model_id = ?
            )
        ''', (model_id,))
        
        avg_latency = cursor.fetchone()['avg_latency'] or 0.0
        
        # Get success rate (responses with content)
        cursor.execute('''
            SELECT 
                COUNT(*) as total_responses,
                SUM(CASE WHEN response IS NOT NULL AND response != '' THEN 1 ELSE 0 END) as successful
            FROM responses
            WHERE request_id IN (
                SELECT id FROM requests WHERE model_id = ?
            )
        ''', (model_id,))
        
        response_stats = cursor.fetchone()
        success_rate = 0.0
        if response_stats['total_responses'] > 0:
            success_rate = (response_stats['successful'] / response_stats['total_responses']) * 100
        
        # Get average tokens
        cursor.execute('''
            SELECT AVG(tokens) as avg_tokens
            FROM responses
            WHERE request_id IN (
                SELECT id FROM requests WHERE model_id = ?
            )
        ''', (model_id,))
        
        avg_tokens = cursor.fetchone()['avg_tokens'] or 0.0
        
        conn.close()
        
        return {
            'model_name': model_name,
            'total_requests': total_requests,
            'avg_latency': round(avg_latency, 3),
            'success_rate': round(success_rate, 2),
            'avg_tokens': round(avg_tokens, 1)
        }
    
    def get_all_metrics(self):
        """
        Get metrics for all models
        
        Returns:
            List of model metrics
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM models')
        models = cursor.fetchall()
        conn.close()
        
        metrics = []
        for model in models:
            model_metrics = self.get_model_metrics(model['name'])
            if model_metrics:
                metrics.append(model_metrics)
        
        return metrics
    
    def get_metric_history(self, model_name, metric_name, limit=100):
        """
        Get metric history
        
        Args:
            model_name: Model name
            metric_name: Metric name
            limit: Number of records
            
        Returns:
            List of metric values over time
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.metric_value, m.timestamp
            FROM metrics m
            JOIN models mo ON m.model_id = mo.id
            WHERE mo.name = ? AND m.metric_name = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        ''', (model_name, metric_name, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
