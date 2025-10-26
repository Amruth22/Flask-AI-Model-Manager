"""
Comprehensive Unit Tests for AI Model Manager
Tests model integration, workflows, comparison, A/B testing, and monitoring

TESTING APPROACH:
- test_02_basic_generation: REAL API test (verifies actual integration)
- test_04_workflow_engine: MOCKED (prevents quota exhaustion)
- test_06_model_comparison: MOCKED (prevents quota exhaustion)
- Other tests: No API calls required

NOTE ON FREE API LIMITS:
- Gemini free tier: 10 requests/minute
- Mocking prevents quota issues while keeping one real API test
- Total test runtime: ~5-10 seconds (including real API test)
"""

import unittest
import os
import time
from unittest.mock import patch, Mock
from dotenv import load_dotenv
import pytest

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


class AIModelManagerTestCase(unittest.TestCase):
    """Unit tests for AI Model Manager"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration"""
        print("\n" + "=" * 60)
        print("AI Model Manager - Unit Test Suite")
        print("=" * 60)
        print("Testing: Models, Workflows, Comparison, A/B, Monitoring")
        print("=" * 60 + "\n")
        
        # Use test database
        cls.db_path = 'test_ai_models.db'
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        
        init_database(cls.db_path)
        
        # Check for API key
        cls.has_api_key = bool(os.getenv('GEMINI_API_KEY'))
        if not cls.has_api_key:
            print("Warning: GEMINI_API_KEY not found. Some tests will be skipped.\n")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
    
    # Test 1: Model Registry
    def test_01_model_registry(self):
        """Test model registration and retrieval"""
        print("\n1. Testing model registry...")
        
        registry = ModelRegistry(self.db_path)
        
        if self.has_api_key:
            # Register Gemini model
            gemini = GeminiModel()
            model_id = registry.register_model(gemini)
            
            self.assertIsNotNone(model_id)
            print(f"   Model registered with ID: {model_id}")
            
            # Retrieve model
            retrieved = registry.get_model('gemini-2.0-flash')
            self.assertIsNotNone(retrieved)
            print(f"   Model retrieved: {retrieved.name}")

            # List models
            models = registry.list_models()
            self.assertIn('gemini-2.0-flash', models)
            print(f"   Total models: {len(models)}")
        else:
            print("   Skipped (no API key)")
            self.skipTest("No API key available")
    
    # Test 2: Basic Generation (REAL API TEST)
    def test_02_basic_generation(self):
        """Test basic text generation (REAL API - verifies actual integration)"""
        print("\n2. Testing basic generation (real API)...")

        if not self.has_api_key:
            print("   Skipped (no API key)")
            self.skipTest("No API key available")

        gemini = GeminiModel()

        prompt = "Say hello in one word."
        result = gemini.generate(prompt, max_tokens=10)

        self.assertIn('response', result)
        self.assertIn('tokens', result)
        self.assertIn('latency', result)
        self.assertIn('cost', result)

        print(f"   Response: {result['response'][:50]}")
        print(f"   Tokens: {result['tokens']}")
        print(f"   Latency: {result['latency']:.2f}s")
        print(f"   (Using REAL API connection)")
    
    # Test 3: Request Logger
    def test_03_request_logger(self):
        """Test request logging"""
        print("\n3. Testing request logger...")
        
        logger = RequestLogger(self.db_path)
        
        # Log request
        request_id = logger.log_request(1, "Test prompt")
        self.assertIsNotNone(request_id)
        print(f"   Request logged: ID {request_id}")
        
        # Log response
        response_id = logger.log_response(request_id, "Test response", 10, 0.5, 0.0001)
        self.assertIsNotNone(response_id)
        print(f"   Response logged: ID {response_id}")
        
        # Get history
        history = logger.get_request_history(limit=5)
        self.assertGreaterEqual(len(history), 1)
        print(f"   History records: {len(history)}")
    
    # Test 4: Workflow Engine
    def test_04_workflow_engine(self):
        """Test workflow execution (MOCKED to prevent quota exhaustion)"""
        print("\n4. Testing workflow engine (mocked)...")

        # Mock the GeminiModel.generate method to prevent API calls
        with patch('models.gemini_model.GeminiModel.generate') as mock_generate:
            # Setup sequential responses for 2-step workflow
            mock_generate.side_effect = [
                {
                    'response': 'Step 1: Generated content',
                    'tokens': 25,
                    'latency': 0.65,
                    'cost': 0.00025
                },
                {
                    'response': 'Step 2: Improved content',
                    'tokens': 30,
                    'latency': 0.70,
                    'cost': 0.00030
                }
            ]

            registry = ModelRegistry(self.db_path)
            gemini = GeminiModel()
            registry.register_model(gemini)

            engine = WorkflowEngine(registry, self.db_path)

            # Simple 2-step workflow
            steps = [
                {
                    'model': 'gemini-2.0-flash',
                    'prompt_template': 'Write one word about: {input}'
                },
                {
                    'model': 'gemini-2.0-flash',
                    'prompt_template': 'Make this word uppercase: {input}'
                }
            ]

            result = engine.execute_workflow('test_workflow', steps, 'AI')

            self.assertIn('final_output', result)
            self.assertEqual(len(result['steps']), 2)
            print(f"   Workflow steps: {len(result['steps'])}")
            print(f"   Total tokens: {result['total_tokens']}")
            print(f"   (Using mocked API responses)")
    
    # Test 5: Workflow Templates
    def test_05_workflow_templates(self):
        """Test workflow templates"""
        print("\n5. Testing workflow templates...")
        
        templates = WorkflowTemplates.get_all_templates()
        
        self.assertIn('content_generation', templates)
        self.assertIn('translation', templates)
        self.assertIn('analysis', templates)
        
        print(f"   Available templates: {len(templates)}")
        for name, desc in templates.items():
            print(f"      - {name}: {desc}")
    
    # Test 6: Model Comparison
    def test_06_model_comparison(self):
        """Test model comparison (MOCKED to prevent quota exhaustion)"""
        print("\n6. Testing model comparison (mocked)...")

        # Mock the GeminiModel.generate method to prevent API calls
        with patch('models.gemini_model.GeminiModel.generate') as mock_generate:
            # Setup responses for comparison (two models)
            mock_generate.side_effect = [
                {
                    'response': 'Hi! How are you?',
                    'tokens': 40,
                    'latency': 0.90,
                    'cost': 0.00040
                },
                {
                    'response': 'Hello! I am doing great.',
                    'tokens': 35,
                    'latency': 0.75,
                    'cost': 0.00035
                }
            ]

            registry = ModelRegistry(self.db_path)
            gemini = GeminiModel()
            registry.register_model(gemini)

            comparator = ModelComparator(registry, self.db_path)

            # Compare same model twice (for demo)
            result = comparator.compare_models(
                ['gemini-2.0-flash', 'gemini-2.0-flash'],
                'Say hi'
            )

            self.assertIn('results', result)
            self.assertEqual(len(result['results']), 2)
            self.assertIn('winner', result)

            print(f"   Models compared: {len(result['results'])}")
            print(f"   Winner: {result['winner']}")
            print(f"   (Using mocked API responses)")
    
    # Test 7: A/B Testing
    def test_07_ab_testing(self):
        """Test A/B experiment management"""
        print("\n7. Testing A/B testing...")
        
        manager = ExperimentManager(self.db_path)
        
        # Create experiment
        exp_id = manager.create_experiment(
            'Test Experiment',
            'model_a',
            'model_b'
        )
        
        self.assertIsNotNone(exp_id)
        print(f"   Experiment created: ID {exp_id}")
        
        # Record results
        manager.record_result(exp_id, 'A', True, 5)
        manager.record_result(exp_id, 'B', True, 4)
        
        # Get stats
        stats = manager.get_experiment_stats(exp_id)
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['variant_a']['total'], 1)
        self.assertEqual(stats['variant_b']['total'], 1)
        
        print(f"   Variant A: {stats['variant_a']['total']} requests")
        print(f"   Variant B: {stats['variant_b']['total']} requests")
        print(f"   Winner: {stats['winner']}")
    
    # Test 8: Traffic Router
    def test_08_traffic_router(self):
        """Test traffic routing"""
        print("\n8. Testing traffic router...")
        
        if not self.has_api_key:
            print("   Skipped (no API key)")
            self.skipTest("No API key available")
        
        registry = ModelRegistry(self.db_path)
        gemini = GeminiModel()
        registry.register_model(gemini)
        
        router = TrafficRouter(registry)
        
        # Test consistent routing
        variant1, model1 = router.route_request(
            'user123',
            'gemini-2.0-flash',
            'gemini-2.5-flash-lite'
        )

        variant2, model2 = router.route_request(
            'user123',
            'gemini-2.0-flash',
            'gemini-2.5-flash-lite'
        )
        
        # Same user should get same variant
        self.assertEqual(variant1, variant2)
        print(f"   User routed to variant: {variant1}")
        print(f"   Routing is consistent: True")
    
    # Test 9: Metrics Tracking
    def test_09_metrics_tracking(self):
        """Test metrics tracking"""
        print("\n9. Testing metrics tracking...")
        
        if not self.has_api_key:
            print("   Skipped (no API key)")
            self.skipTest("No API key available")
        
        registry = ModelRegistry(self.db_path)
        gemini = GeminiModel()
        model_id = registry.register_model(gemini)
        
        tracker = MetricsTracker(self.db_path)
        
        # Track some metrics
        tracker.track_metric(model_id, 'latency', 1.5)
        tracker.track_metric(model_id, 'latency', 2.0)
        tracker.track_metric(model_id, 'tokens', 100)
        
        # Get metrics
        metrics = tracker.get_model_metrics('gemini-2.0-flash')

        self.assertIsNotNone(metrics)
        print(f"   Metrics tracked for: {metrics['model_name']}")
        print(f"   Avg latency: {metrics['avg_latency']:.3f}s")
    
    # Test 10: Cost Tracking
    def test_10_cost_tracking(self):
        """Test cost tracking"""
        print("\n10. Testing cost tracking...")
        
        if not self.has_api_key:
            print("   Skipped (no API key)")
            self.skipTest("No API key available")
        
        registry = ModelRegistry(self.db_path)
        gemini = GeminiModel()
        model_id = registry.register_model(gemini)
        
        tracker = CostTracker(self.db_path)
        
        # Track costs
        tracker.track_cost(model_id, 0.001, 100)
        tracker.track_cost(model_id, 0.002, 200)
        
        # Get costs
        costs = tracker.get_model_costs('gemini-2.0-flash')

        self.assertIsNotNone(costs)
        self.assertEqual(costs['total_requests'], 2)
        self.assertGreater(costs['total_cost'], 0)
        
        print(f"   Total requests: {costs['total_requests']}")
        print(f"   Total cost: ${costs['total_cost']:.6f}")
        print(f"   Avg cost: ${costs['avg_cost']:.6f}")
        
        # Test budget alert
        over_budget = tracker.check_budget_alert(0.0001)
        print(f"   Budget alert: {over_budget}")


def run_tests():
    """Run all unit tests"""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(AIModelManagerTestCase)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if not result.failures and not result.errors:
        print("\nALL TESTS PASSED!")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("AI Model Manager - Unit Test Suite")
    print("=" * 60)
    print("\nYou can run tests with:")
    print("  - unittest: python tests.py")
    print("  - pytest: pytest tests.py")
    print("  - pytest verbose: pytest tests.py -v")
    print("  - pytest markers: pytest tests.py -m api_test (real API only)")
    print("=" * 60)

    try:
        success = run_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
