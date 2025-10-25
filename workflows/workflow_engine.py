"""
Workflow Engine
Execute multi-step AI workflows
"""

import logging
import json
from storage.database import get_connection

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Execute multi-step AI workflows
    """
    
    def __init__(self, model_registry, db_path='ai_models.db'):
        """
        Initialize workflow engine
        
        Args:
            model_registry: ModelRegistry instance
            db_path: Path to database file
        """
        self.model_registry = model_registry
        self.db_path = db_path
        logger.info("Workflow engine initialized")
    
    def execute_workflow(self, workflow_name, steps, initial_input):
        """
        Execute a workflow
        
        Args:
            workflow_name: Name of workflow
            steps: List of workflow steps
                   Each step: {'model': 'model_name', 'prompt_template': 'template'}
            initial_input: Initial input data
            
        Returns:
            Dictionary with workflow results
        """
        logger.info(f"Executing workflow: {workflow_name}")
        
        results = []
        current_input = initial_input
        
        for i, step in enumerate(steps, 1):
            logger.info(f"Executing step {i}/{len(steps)}")
            
            # Get model
            model_name = step.get('model')
            model = self.model_registry.get_model(model_name)
            
            if not model:
                raise ValueError(f"Model not found: {model_name}")
            
            # Build prompt
            prompt_template = step.get('prompt_template')
            prompt = prompt_template.format(input=current_input)
            
            # Generate
            result = model.generate(prompt)
            
            # Store step result
            step_result = {
                'step': i,
                'model': model_name,
                'prompt': prompt,
                'response': result['response'],
                'tokens': result['tokens'],
                'latency': result['latency'],
                'cost': result['cost']
            }
            results.append(step_result)
            
            # Use output as input for next step
            current_input = result['response']
        
        # Store workflow execution
        self._store_workflow(workflow_name, steps, results)
        
        logger.info(f"Workflow completed: {workflow_name}")
        
        return {
            'workflow_name': workflow_name,
            'steps': results,
            'final_output': current_input,
            'total_tokens': sum(s['tokens'] for s in results),
            'total_latency': sum(s['latency'] for s in results),
            'total_cost': sum(s['cost'] for s in results)
        }
    
    def _store_workflow(self, name, steps, results):
        """
        Store workflow execution in database
        
        Args:
            name: Workflow name
            steps: Workflow steps
            results: Execution results
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workflows (name, steps, result)
            VALUES (?, ?, ?)
        ''', (name, json.dumps(steps), json.dumps(results)))
        
        conn.commit()
        conn.close()
    
    def get_workflow_history(self, limit=10):
        """
        Get workflow execution history
        
        Args:
            limit: Number of records to retrieve
            
        Returns:
            List of workflow executions
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, steps, result, timestamp
            FROM workflows
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
