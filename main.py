"""
AI Model Manager - Main Demonstration
Shows examples of all AI model management features
"""

import os
import time
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

# Load environment variables
load_dotenv()


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_basic_generation():
    """Demonstrate basic text generation"""
    print_section("1. Basic Text Generation with Gemini")
    
    try:
        # Initialize model
        gemini = GeminiModel()
        
        prompt = "Explain what AI model integration means in 2 sentences."
        
        print(f"\nPrompt: {prompt}")
        print("\nGenerating response...")
        
        result = gemini.generate(prompt, max_tokens=100)
        
        print(f"\nResponse: {result['response']}")
        print(f"\nMetrics:")
        print(f"   Tokens: {result['tokens']}")
        print(f"   Latency: {result['latency']:.2f}s")
        print(f"   Cost: ${result['cost']:.6f}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure GEMINI_API_KEY is set in .env file")


def demo_streaming():
    """Demonstrate streaming generation"""
    print_section("2. Streaming Text Generation")
    
    try:
        gemini = GeminiModel()
        
        prompt = "Write a haiku about artificial intelligence."
        
        print(f"\nPrompt: {prompt}")
        print("\nStreaming response:")
        print("-" * 50)
        
        for chunk in gemini.generate_stream(prompt, max_tokens=50):
            print(chunk, end='', flush=True)
        
        print("\n" + "-" * 50)
        print("\nStreaming completed!")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_workflow():
    """Demonstrate workflow execution"""
    print_section("3. AI Workflow Execution")
    
    try:
        # Setup
        db_path = 'demo.db'
        model_registry = ModelRegistry(db_path)
        gemini = GeminiModel()
        model_registry.register_model(gemini)
        
        workflow_engine = WorkflowEngine(model_registry, db_path)
        
        # Get workflow template
        steps = WorkflowTemplates.content_generation_workflow('gemini-2.0-flash-exp')
        
        print("\nWorkflow: Content Generation")
        print("Steps:")
        print("   1. Generate initial content")
        print("   2. Improve content")
        print("   3. Format content")
        
        initial_input = "Python programming"
        
        print(f"\nInput: {initial_input}")
        print("\nExecuting workflow...")
        
        result = workflow_engine.execute_workflow(
            'content_generation',
            steps,
            initial_input
        )
        
        print(f"\nWorkflow completed!")
        print(f"\nFinal output (first 200 chars):")
        print(result['final_output'][:200] + "...")
        
        print(f"\nWorkflow metrics:")
        print(f"   Total steps: {len(result['steps'])}")
        print(f"   Total tokens: {result['total_tokens']}")
        print(f"   Total latency: {result['total_latency']:.2f}s")
        print(f"   Total cost: ${result['total_cost']:.6f}")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_comparison():
    """Demonstrate model comparison"""
    print_section("4. Model Comparison")
    
    print("\nNote: This demo requires multiple models to be registered.")
    print("Currently only Gemini is available in this demo.")
    print("\nIn production, you would compare:")
    print("   - Gemini vs GPT-4")
    print("   - Claude vs Gemini")
    print("   - Different model versions")
    
    print("\nComparison metrics include:")
    print("   - Response latency")
    print("   - Token count")
    print("   - API cost")
    print("   - Response quality")
    
    print("\nExample comparison output:")
    print("   Model A: 1.2s, 150 tokens, $0.0015")
    print("   Model B: 0.8s, 120 tokens, $0.0012")
    print("   Winner: Model B (faster and cheaper)")


def demo_ab_testing():
    """Demonstrate A/B testing"""
    print_section("5. A/B Testing")
    
    try:
        db_path = 'demo.db'
        experiment_manager = ExperimentManager(db_path)
        
        # Create experiment
        print("\nCreating A/B experiment...")
        experiment_id = experiment_manager.create_experiment(
            name="Model Performance Test",
            variant_a="gemini-2.0-flash-exp",
            variant_b="gemini-2.0-flash-exp"  # Same model for demo
        )
        
        print(f"Experiment created: ID {experiment_id}")
        
        # Simulate some results
        print("\nSimulating experiment results...")
        
        # Variant A results
        for i in range(10):
            success = i % 3 != 0  # 66% success rate
            experiment_manager.record_result(experiment_id, 'A', success, rating=4)
        
        # Variant B results
        for i in range(10):
            success = i % 4 != 0  # 75% success rate
            experiment_manager.record_result(experiment_id, 'B', success, rating=5)
        
        # Get statistics
        stats = experiment_manager.get_experiment_stats(experiment_id)
        
        print(f"\nExperiment Results:")
        print(f"\nVariant A ({stats['variant_a']['model']}):")
        print(f"   Total requests: {stats['variant_a']['total']}")
        print(f"   Successes: {stats['variant_a']['successes']}")
        print(f"   Conversion rate: {stats['variant_a']['conversion_rate']:.1f}%")
        print(f"   Avg rating: {stats['variant_a']['avg_rating']:.1f}")
        
        print(f"\nVariant B ({stats['variant_b']['model']}):")
        print(f"   Total requests: {stats['variant_b']['total']}")
        print(f"   Successes: {stats['variant_b']['successes']}")
        print(f"   Conversion rate: {stats['variant_b']['conversion_rate']:.1f}%")
        print(f"   Avg rating: {stats['variant_b']['avg_rating']:.1f}")
        
        print(f"\nWinner: Variant {stats['winner']}")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_monitoring():
    """Demonstrate performance monitoring"""
    print_section("6. Performance Monitoring")
    
    try:
        db_path = 'demo.db'
        model_registry = ModelRegistry(db_path)
        gemini = GeminiModel()
        model_registry.register_model(gemini)
        
        metrics_tracker = MetricsTracker(db_path)
        
        # Generate some requests to track
        print("\nGenerating sample requests...")
        
        for i in range(3):
            result = gemini.generate(f"Test prompt {i+1}", max_tokens=50)
            model_id = model_registry.get_model_id('gemini-2.0-flash-exp')
            metrics_tracker.track_metric(model_id, 'latency', result['latency'])
            metrics_tracker.track_metric(model_id, 'tokens', result['tokens'])
        
        # Get metrics
        metrics = metrics_tracker.get_model_metrics('gemini-2.0-flash-exp')
        
        print(f"\nPerformance Metrics for Gemini:")
        print(f"   Total requests: {metrics['total_requests']}")
        print(f"   Avg latency: {metrics['avg_latency']:.3f}s")
        print(f"   Success rate: {metrics['success_rate']:.1f}%")
        print(f"   Avg tokens: {metrics['avg_tokens']:.1f}")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_cost_tracking():
    """Demonstrate cost tracking"""
    print_section("7. Cost Tracking")
    
    try:
        db_path = 'demo.db'
        model_registry = ModelRegistry(db_path)
        gemini = GeminiModel()
        model_registry.register_model(gemini)
        
        cost_tracker = CostTracker(db_path)
        
        # Generate some requests
        print("\nGenerating sample requests...")
        
        model_id = model_registry.get_model_id('gemini-2.0-flash-exp')
        
        for i in range(5):
            result = gemini.generate(f"Cost test {i+1}", max_tokens=50)
            cost_tracker.track_cost(model_id, result['cost'], result['tokens'])
        
        # Get cost data
        costs = cost_tracker.get_model_costs('gemini-2.0-flash-exp')
        total_cost = cost_tracker.get_total_cost()
        
        print(f"\nCost Analysis for Gemini:")
        print(f"   Total requests: {costs['total_requests']}")
        print(f"   Total cost: ${costs['total_cost']:.6f}")
        print(f"   Avg cost per request: ${costs['avg_cost']:.6f}")
        print(f"   Total tokens: {costs['total_tokens']}")
        
        print(f"\nTotal cost across all models: ${total_cost:.6f}")
        
        # Budget check
        budget_limit = 1.0  # $1.00
        over_budget = cost_tracker.check_budget_alert(budget_limit)
        
        if over_budget:
            print(f"\nBudget Alert: Exceeded ${budget_limit:.2f} limit!")
        else:
            print(f"\nBudget Status: Within ${budget_limit:.2f} limit")
        
    except Exception as e:
        print(f"\nError: {e}")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("  AI Model Manager - Demonstration")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\nWarning: GEMINI_API_KEY not found in environment!")
        print("Please create a .env file with your API key.")
        print("See .env.example for template.")
        print("\nSome demos will be skipped.")
    
    try:
        # Clean up old database
        db_path = 'demo.db'
        if os.path.exists(db_path):
            os.remove(db_path)
        
        init_database(db_path)
        
        # Run demonstrations
        demo_basic_generation()
        demo_streaming()
        demo_workflow()
        demo_comparison()
        demo_ab_testing()
        demo_monitoring()
        demo_cost_tracking()
        
        print("\n" + "=" * 70)
        print("  All Demonstrations Completed!")
        print("=" * 70)
        print("\nKey Concepts Demonstrated:")
        print("  1. AI Model Integration - Connect to Gemini API")
        print("  2. Streaming Generation - Real-time text streaming")
        print("  3. Workflow Management - Multi-step AI operations")
        print("  4. Model Comparison - Compare different models")
        print("  5. A/B Testing - Scientific model selection")
        print("  6. Performance Monitoring - Track metrics")
        print("  7. Cost Tracking - Monitor API costs")
        print("\nTo run Flask API:")
        print("  python api/app.py")
        print("\nTo run tests:")
        print("  python tests.py")
        print()
        
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
