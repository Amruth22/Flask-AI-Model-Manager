"""
Flask API for AI Model Manager
Provides REST API for AI model operations
"""

from flask import Flask, request, jsonify
import logging
import os
from dotenv import load_dotenv

from storage.database import init_database
from models.gemini_model import GeminiModel
from models.model_registry import ModelRegistry
from workflows.workflow_engine import WorkflowEngine
from workflows.workflow_templates import WorkflowTemplates
from comparison.model_comparator import ModelComparator
from ab_testing.experiment_manager import ExperimentManager
from ab_testing.traffic_router import TrafficRouter
from monitoring.metrics_tracker import MetricsTracker
from monitoring.cost_tracker import CostTracker
from storage.request_logger import RequestLogger

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize database
db_path = os.getenv('DATABASE_PATH', 'ai_models.db')
init_database(db_path)

# Initialize components
model_registry = ModelRegistry(db_path)
workflow_engine = WorkflowEngine(model_registry, db_path)
model_comparator = ModelComparator(model_registry, db_path)
experiment_manager = ExperimentManager(db_path)
traffic_router = TrafficRouter(model_registry)
metrics_tracker = MetricsTracker(db_path)
cost_tracker = CostTracker(db_path)
request_logger = RequestLogger(db_path)

# Register Gemini model
try:
    gemini = GeminiModel()
    model_registry.register_model(gemini)
    logger.info("Gemini model registered")
except Exception as e:
    logger.warning(f"Could not register Gemini model: {e}")


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'AI Model Manager API',
        'version': '1.0.0',
        'features': [
            'AI Model Integration',
            'Workflow Management',
            'Model Comparison',
            'A/B Testing',
            'Performance Monitoring'
        ],
        'endpoints': {
            'generate': '/api/generate',
            'workflow': '/api/workflow',
            'compare': '/api/compare',
            'experiment': '/api/experiment',
            'metrics': '/api/metrics',
            'costs': '/api/costs'
        }
    })


@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})


@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    models = model_registry.list_models()
    return jsonify({
        'models': models,
        'count': len(models)
    })


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate text with AI model"""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Prompt required'}), 400
    
    prompt = data['prompt']
    model_name = data.get('model', 'gemini-2.0-flash-exp')
    
    # Get model
    model = model_registry.get_model(model_name)
    if not model:
        return jsonify({'error': f'Model not found: {model_name}'}), 404
    
    try:
        # Generate
        result = model.generate(prompt)
        
        # Log request
        model_id = model_registry.get_model_id(model_name)
        request_id = request_logger.log_request(model_id, prompt)
        request_logger.log_response(
            request_id,
            result['response'],
            result['tokens'],
            result['latency'],
            result['cost']
        )
        
        # Track metrics
        metrics_tracker.track_metric(model_id, 'latency', result['latency'])
        metrics_tracker.track_metric(model_id, 'tokens', result['tokens'])
        
        # Track cost
        cost_tracker.track_cost(model_id, result['cost'], result['tokens'])
        
        return jsonify({
            'status': 'success',
            'model': model_name,
            'response': result['response'],
            'tokens': result['tokens'],
            'latency': result['latency'],
            'cost': result['cost']
        })
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflow', methods=['POST'])
def execute_workflow():
    """Execute AI workflow"""
    data = request.get_json()
    
    if not data or 'template' not in data or 'input' not in data:
        return jsonify({'error': 'Template and input required'}), 400
    
    template_name = data['template']
    initial_input = data['input']
    model_name = data.get('model', 'gemini-2.0-flash-exp')
    
    # Get workflow template
    if template_name == 'content_generation':
        steps = WorkflowTemplates.content_generation_workflow(model_name)
    elif template_name == 'translation':
        steps = WorkflowTemplates.translation_workflow(model_name)
    elif template_name == 'analysis':
        steps = WorkflowTemplates.analysis_workflow(model_name)
    else:
        return jsonify({'error': f'Unknown template: {template_name}'}), 400
    
    try:
        # Execute workflow
        result = workflow_engine.execute_workflow(template_name, steps, initial_input)
        
        return jsonify({
            'status': 'success',
            'workflow': result
        })
        
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_models():
    """Compare multiple models"""
    data = request.get_json()
    
    if not data or 'models' not in data or 'prompt' not in data:
        return jsonify({'error': 'Models and prompt required'}), 400
    
    model_names = data['models']
    prompt = data['prompt']
    
    if len(model_names) < 2:
        return jsonify({'error': 'At least 2 models required'}), 400
    
    try:
        # Compare models
        result = model_comparator.compare_models(model_names, prompt)
        
        return jsonify({
            'status': 'success',
            'comparison': result
        })
        
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment', methods=['POST'])
def create_experiment():
    """Create A/B experiment"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'variant_a' not in data or 'variant_b' not in data:
        return jsonify({'error': 'Name, variant_a, and variant_b required'}), 400
    
    try:
        experiment_id = experiment_manager.create_experiment(
            data['name'],
            data['variant_a'],
            data['variant_b']
        )
        
        return jsonify({
            'status': 'success',
            'experiment_id': experiment_id
        }), 201
        
    except Exception as e:
        logger.error(f"Experiment creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/<int:experiment_id>/test', methods=['POST'])
def test_experiment(experiment_id):
    """Test A/B experiment"""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'prompt' not in data:
        return jsonify({'error': 'user_id and prompt required'}), 400
    
    try:
        # Get experiment
        stats = experiment_manager.get_experiment_stats(experiment_id)
        if not stats:
            return jsonify({'error': 'Experiment not found'}), 404
        
        # Route request
        result = traffic_router.generate_with_routing(
            data['user_id'],
            data['prompt'],
            stats['variant_a']['model'],
            stats['variant_b']['model']
        )
        
        return jsonify({
            'status': 'success',
            'experiment_id': experiment_id,
            'variant': result['variant'],
            'response': result['response']
        })
        
    except Exception as e:
        logger.error(f"Experiment test error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/<int:experiment_id>/record', methods=['POST'])
def record_experiment_result(experiment_id):
    """Record experiment result"""
    data = request.get_json()
    
    if not data or 'variant' not in data or 'success' not in data:
        return jsonify({'error': 'variant and success required'}), 400
    
    try:
        result_id = experiment_manager.record_result(
            experiment_id,
            data['variant'],
            data['success'],
            data.get('rating')
        )
        
        return jsonify({
            'status': 'success',
            'result_id': result_id
        })
        
    except Exception as e:
        logger.error(f"Record result error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/<int:experiment_id>/stats', methods=['GET'])
def get_experiment_stats(experiment_id):
    """Get experiment statistics"""
    try:
        stats = experiment_manager.get_experiment_stats(experiment_id)
        
        if not stats:
            return jsonify({'error': 'Experiment not found'}), 404
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics"""
    try:
        metrics = metrics_tracker.get_all_metrics()
        
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Get metrics error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/costs', methods=['GET'])
def get_costs():
    """Get cost data"""
    try:
        costs = cost_tracker.get_all_costs()
        total_cost = cost_tracker.get_total_cost()
        
        return jsonify({
            'status': 'success',
            'costs': costs,
            'total_cost': total_cost
        })
        
    except Exception as e:
        logger.error(f"Get costs error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("AI Model Manager - Flask API")
    print("=" * 60)
    print(f"Starting on port {port}")
    print("Features:")
    print("  - AI Model Integration")
    print("  - Workflow Management")
    print("  - Model Comparison")
    print("  - A/B Testing")
    print("  - Performance Monitoring")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
