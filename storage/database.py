"""
Database Module
Initialize and manage SQLite database
"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def init_database(db_path='ai_models.db'):
    """
    Initialize SQLite database with all required tables
    
    Args:
        db_path: Path to database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Models table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            provider TEXT NOT NULL,
            cost_per_token REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            prompt TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models(id)
        )
    ''')
    
    # Responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            response TEXT,
            tokens INTEGER,
            latency REAL,
            cost REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES requests(id)
        )
    ''')
    
    # Workflows table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            steps TEXT,
            result TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Comparisons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            model1_id INTEGER,
            model2_id INTEGER,
            model1_response TEXT,
            model2_response TEXT,
            model1_latency REAL,
            model2_latency REAL,
            model1_tokens INTEGER,
            model2_tokens INTEGER,
            winner TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Experiments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            variant_a TEXT,
            variant_b TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Experiment results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            variant TEXT,
            success BOOLEAN,
            rating INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        )
    ''')
    
    # Metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            metric_name TEXT,
            metric_value REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models(id)
        )
    ''')
    
    # Costs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            cost REAL,
            tokens INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info(f"Database initialized: {db_path}")


def get_connection(db_path='ai_models.db'):
    """
    Get database connection
    
    Args:
        db_path: Path to database file
        
    Returns:
        SQLite connection
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
