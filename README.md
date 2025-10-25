# AI Model Manager

Educational Flask application demonstrating **AI model integration with Gemini LLM**, **workflow management**, **model comparison**, **A/B testing**, and **performance monitoring** with **SQLite storage**.

## Features

### AI Model Integration
- **Gemini API Integration** - Connect to Google Gemini LLM
- **Base Model Interface** - Abstract interface for all models
- **Model Registry** - Register and manage multiple models
- **Streaming Support** - Real-time text streaming
- **Token Counting** - Track token usage
- **Cost Calculation** - Calculate API costs

### Workflow Management
- **Multi-Step Workflows** - Chain AI operations together
- **Workflow Templates** - Pre-built workflow examples
- **Sequential Execution** - Execute steps in order
- **Result Persistence** - Store workflow results
- **Error Handling** - Graceful error management

### Model Comparison
- **Side-by-Side Comparison** - Compare multiple models
- **Performance Metrics** - Latency, tokens, cost
- **Winner Determination** - Automatic winner selection
- **Comparison History** - Store past comparisons
- **Win Rate Tracking** - Track model performance

### A/B Testing
- **Experiment Management** - Create and manage experiments
- **Traffic Routing** - Route users to variants
- **Statistical Analysis** - Conversion rates, ratings
- **Result Recording** - Track experiment outcomes
- **Winner Determination** - Data-driven decisions

### Performance Monitoring
- **Metrics Tracking** - Track latency, tokens, success rate
- **Cost Tracking** - Monitor API costs
- **Budget Alerts** - Alert on cost thresholds
- **Historical Data** - Store metrics over time
- **Dashboard Data** - Aggregated statistics

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Amruth22/Flask-AI-Model-Manager.git
cd Flask-AI-Model-Manager
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get API key from: https://makersuite.google.com/app/apikey
```

### 5. Run Demonstrations
```bash
python main.py
```

### 6. Run Flask API
```bash
python api/app.py
```

### 7. Run Tests
```bash
python tests.py
```

## Project Structure

```
Flask-AI-Model-Manager/
│
├── models/
│   ├── base_model.py           # Base class for all models
│   ├── gemini_model.py         # Google Gemini integration
│   └── model_registry.py       # Model registration
│
├── workflows/
│   ├── workflow_engine.py      # Execute workflows
│   └── workflow_templates.py   # Pre-built templates
│
├── comparison/
│   ├── model_comparator.py     # Compare models
│   └── comparison_store.py     # Store comparisons
│
├── ab_testing/
│   ├── experiment_manager.py   # Manage experiments
│   └── traffic_router.py       # Route traffic
│
├── monitoring/
│   ├── metrics_tracker.py      # Track metrics
│   └── cost_tracker.py         # Track costs
│
├── storage/
│   ├── database.py             # SQLite setup
│   └── request_logger.py       # Log requests
│
├── api/
│   └── app.py                  # Flask REST API
│
├── main.py                     # Demonstrations
├── tests.py                    # 10 unit tests
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## Usage Examples

### Basic Text Generation

```python
from models.gemini_model import GeminiModel

# Initialize model
gemini = GeminiModel()

# Generate text
result = gemini.generate("Explain AI in one sentence.")

print(result['response'])
print(f"Tokens: {result['tokens']}")
print(f"Cost: ${result['cost']:.6f}")
```

### Streaming Generation

```python
from models.gemini_model import GeminiModel

gemini = GeminiModel()

# Stream response
for chunk in gemini.generate_stream("Write a haiku about AI"):
    print(chunk, end='', flush=True)
```

### Workflow Execution

```python
from models.model_registry import ModelRegistry
from workflows.workflow_engine import WorkflowEngine
from workflows.workflow_templates import WorkflowTemplates

# Setup
registry = ModelRegistry()
gemini = GeminiModel()
registry.register_model(gemini)

engine = WorkflowEngine(registry)

# Get template
steps = WorkflowTemplates.content_generation_workflow('gemini-2.0-flash-exp')

# Execute workflow
result = engine.execute_workflow('content_gen', steps, 'Python programming')

print(result['final_output'])
print(f"Total cost: ${result['total_cost']:.6f}")
```

### Model Comparison

```python
from comparison.model_comparator import ModelComparator

comparator = ModelComparator(registry)

# Compare models
result = comparator.compare_models(
    ['gemini-2.0-flash-exp', 'other-model'],
    'Explain machine learning'
)

print(f"Winner: {result['winner']}")
for r in result['results']:
    print(f"{r['model']}: {r['latency']:.2f}s, ${r['cost']:.6f}")
```

### A/B Testing

```python
from ab_testing.experiment_manager import ExperimentManager

manager = ExperimentManager()

# Create experiment
exp_id = manager.create_experiment(
    'Model Test',
    'gemini-2.0-flash-exp',
    'other-model'
)

# Record results
manager.record_result(exp_id, 'A', success=True, rating=5)
manager.record_result(exp_id, 'B', success=True, rating=4)

# Get statistics
stats = manager.get_experiment_stats(exp_id)
print(f"Winner: Variant {stats['winner']}")
```

### Performance Monitoring

```python
from monitoring.metrics_tracker import MetricsTracker

tracker = MetricsTracker()

# Get metrics
metrics = tracker.get_model_metrics('gemini-2.0-flash-exp')

print(f"Total requests: {metrics['total_requests']}")
print(f"Avg latency: {metrics['avg_latency']:.3f}s")
print(f"Success rate: {metrics['success_rate']:.1f}%")
```

### Cost Tracking

```python
from monitoring.cost_tracker import CostTracker

tracker = CostTracker()

# Get costs
costs = tracker.get_model_costs('gemini-2.0-flash-exp')

print(f"Total cost: ${costs['total_cost']:.6f}")
print(f"Total tokens: {costs['total_tokens']}")

# Check budget
over_budget = tracker.check_budget_alert(1.0)  # $1.00 limit
```

## Flask API Endpoints

### Model Operations
- `GET /api/models` - List available models
- `POST /api/generate` - Generate text

### Workflow Operations
- `POST /api/workflow` - Execute workflow

### Comparison Operations
- `POST /api/compare` - Compare models

### A/B Testing Operations
- `POST /api/experiment` - Create experiment
- `POST /api/experiment/<id>/test` - Test experiment
- `POST /api/experiment/<id>/record` - Record result
- `GET /api/experiment/<id>/stats` - Get statistics

### Monitoring Operations
- `GET /api/metrics` - Get performance metrics
- `GET /api/costs` - Get cost data

## API Examples

### Generate Text
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, AI!", "model": "gemini-2.0-flash-exp"}'
```

### Execute Workflow
```bash
curl -X POST http://localhost:5000/api/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "template": "content_generation",
    "input": "Python programming",
    "model": "gemini-2.0-flash-exp"
  }'
```

### Compare Models
```bash
curl -X POST http://localhost:5000/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["gemini-2.0-flash-exp", "gemini-2.0-flash-exp"],
    "prompt": "Explain AI"
  }'
```

## Testing

Run the comprehensive test suite:

```bash
python tests.py
```

### Test Coverage (10 Tests)

1. **Model Registry** - Test model registration
2. **Basic Generation** - Test text generation
3. **Request Logger** - Test logging
4. **Workflow Engine** - Test workflow execution
5. **Workflow Templates** - Test templates
6. **Model Comparison** - Test comparison
7. **A/B Testing** - Test experiments
8. **Traffic Router** - Test routing
9. **Metrics Tracking** - Test metrics
10. **Cost Tracking** - Test cost tracking

## Educational Notes

### 1. AI Model Integration

**Key Concepts:**
- Abstract base classes for extensibility
- API key management
- Error handling for API calls
- Token counting and cost calculation

**Best Practices:**
- Use environment variables for API keys
- Implement retry logic for failures
- Track all API calls for monitoring
- Calculate costs in real-time

### 2. Workflow Management

**Key Concepts:**
- Sequential execution of AI operations
- Passing outputs between steps
- Workflow state management
- Result persistence

**Use Cases:**
- Content generation pipelines
- Translation workflows
- Analysis pipelines
- Multi-step processing

### 3. Model Comparison

**Key Concepts:**
- Objective comparison metrics
- Performance vs cost tradeoffs
- Winner determination algorithms
- Historical comparison tracking

**Metrics:**
- Latency (response time)
- Token count (efficiency)
- Cost (economics)
- Quality (subjective)

### 4. A/B Testing

**Key Concepts:**
- Controlled experiments
- Traffic splitting
- Statistical significance
- Data-driven decisions

**Process:**
1. Create experiment with variants
2. Route traffic consistently
3. Record results
4. Analyze statistics
5. Determine winner

### 5. Performance Monitoring

**Key Concepts:**
- Real-time metrics collection
- Aggregated statistics
- Historical trends
- Alerting on anomalies

**Metrics to Track:**
- Request count
- Average latency
- Success rate
- Token usage
- API costs

## Production Considerations

For production use, consider:

1. **Multiple Model Providers:**
   - Add OpenAI GPT integration
   - Add Anthropic Claude integration
   - Add local model support (Ollama)

2. **Advanced Features:**
   - Caching for repeated prompts
   - Rate limiting per user
   - Authentication and authorization
   - Request queuing for high load

3. **Monitoring:**
   - Prometheus metrics export
   - Grafana dashboards
   - Error tracking (Sentry)
   - Log aggregation (ELK stack)

4. **Scalability:**
   - Use PostgreSQL instead of SQLite
   - Implement Redis for caching
   - Add load balancing
   - Horizontal scaling

5. **Security:**
   - API key rotation
   - Request validation
   - Rate limiting
   - Input sanitization

## Dependencies

- **Flask 3.0.0** - Web framework
- **google-genai 0.2.0** - Gemini API client
- **python-dotenv 1.0.0** - Environment variables
- **pytest 7.4.3** - Testing framework
- **requests 2.31.0** - HTTP client

## Real-World Applications

This pattern is used in:
- **Content Platforms** - AI-powered content generation
- **Chatbots** - Conversational AI systems
- **Development Tools** - Code generation assistants
- **Customer Support** - Automated support systems
- **Research** - Model evaluation and comparison
- **Product Development** - A/B testing AI features

## Learning Path

1. **Start with Basics** - Understand AI model integration
2. **Add Workflows** - Chain multiple operations
3. **Implement Comparison** - Compare different models
4. **Add A/B Testing** - Scientific model selection
5. **Build Monitoring** - Track performance and costs
6. **Create API** - Expose functionality via REST
7. **Write Tests** - Ensure code quality
8. **Deploy** - Take to production

## Troubleshooting

### API Key Issues
```
Error: GEMINI_API_KEY not found
Solution: Create .env file with your API key
```

### Import Errors
```
Error: No module named 'google.genai'
Solution: pip install -r requirements.txt
```

### Database Errors
```
Error: Database locked
Solution: Close other connections or delete .db file
```

## Contributing

This is an educational project. Feel free to:
- Add new model providers
- Improve workflow templates
- Add more comparison metrics
- Enhance monitoring features
- Write more tests

## License

This project is for educational purposes. Feel free to use and modify as needed.

---

**Happy Learning!**
