"""
Request Logger
Log all AI requests and responses to database
"""

import logging
from datetime import datetime
from storage.database import get_connection

logger = logging.getLogger(__name__)


class RequestLogger:
    """
    Log AI requests and responses to database
    """
    
    def __init__(self, db_path='ai_models.db'):
        """
        Initialize request logger
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
    
    def log_request(self, model_id, prompt):
        """
        Log AI request
        
        Args:
            model_id: Model ID
            prompt: User prompt
            
        Returns:
            Request ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO requests (model_id, prompt)
            VALUES (?, ?)
        ''', (model_id, prompt))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.debug(f"Request logged: {request_id}")
        return request_id
    
    def log_response(self, request_id, response, tokens, latency, cost):
        """
        Log AI response
        
        Args:
            request_id: Request ID
            response: AI response text
            tokens: Token count
            latency: Response time in seconds
            cost: API cost
            
        Returns:
            Response ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO responses (request_id, response, tokens, latency, cost)
            VALUES (?, ?, ?, ?, ?)
        ''', (request_id, response, tokens, latency, cost))
        
        response_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.debug(f"Response logged: {response_id}")
        return response_id
    
    def get_request_history(self, limit=10):
        """
        Get recent request history
        
        Args:
            limit: Number of records to retrieve
            
        Returns:
            List of request records
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.prompt, r.timestamp, res.response, res.tokens, res.latency, res.cost
            FROM requests r
            LEFT JOIN responses res ON r.id = res.request_id
            ORDER BY r.timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_total_requests(self):
        """
        Get total number of requests
        
        Returns:
            Total request count
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM requests')
        result = cursor.fetchone()
        conn.close()
        
        return result['count']
