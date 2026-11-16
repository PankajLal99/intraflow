# IntraFlow Testing Guide

Comprehensive testing strategy and procedures for IntraFlow.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Testing Checklist](#testing-checklist)

## Testing Philosophy

IntraFlow follows a multi-layered testing approach:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Security Tests**: Validate authentication and authorization
5. **Performance Tests**: Ensure scalability and response times

## Test Structure

```
agent-orchestrator/tests/
├── agents/
│   ├── test_parent_agent.py        # Parent agent guardrails
│   ├── test_orchestrator.py        # Agent orchestration
│   └── test_specialized_agents.py  # Product search, order mgmt
├── auth/
│   ├── test_jwt.py                 # JWT token generation/validation
│   └── test_password.py            # Password hashing
├── services/
│   ├── test_workflow_service.py    # Workflow CRUD
│   ├── test_queue_service.py       # Message queue
│   └── test_session_service.py     # Session management
├── webhooks/
│   ├── test_verification.py        # HMAC signature validation
│   └── test_handler.py             # Webhook processing
├── test_integration.py             # End-to-end integration tests
└── conftest.py                     # Shared fixtures
```

## Running Tests

### Quick Test (All)

```bash
# Run all tests
./scripts/run-tests.sh
```

### Backend Unit Tests

```bash
cd agent-orchestrator

# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/auth/test_jwt.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Integration Tests

```bash
cd agent-orchestrator

# Run integration tests only
pytest tests/test_integration.py -v

# Run with verbose output
pytest tests/test_integration.py -vv -s
```

### End-to-End Tests

```bash
# Ensure services are running
docker-compose up -d

# Run E2E test script
./scripts/e2e-test.sh
```

### Code Quality Checks

```bash
cd agent-orchestrator

# Linting (Ruff)
ruff check src/

# Formatting (Black)
black --check src/

# Type checking (MyPy)
mypy src/ --ignore-missing-imports

# Security audit (Bandit)
bandit -r src/ -ll
```

## Test Coverage

### Current Coverage Targets

- **Overall**: >80%
- **Critical Paths**: >95%
  - Authentication
  - Parent Agent guardrails
  - Workflow execution
  - Message processing

### View Coverage Reports

```bash
cd agent-orchestrator

# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

# View detailed HTML report
open htmlcov/index.html
```

## Testing Checklist

### Before Every Commit

- [ ] Run linters: `ruff check src/`
- [ ] Run formatters: `black src/`
- [ ] Run unit tests: `pytest tests/`
- [ ] Check coverage: Coverage >80%
- [ ] Manual smoke test of changed features

### Before Pull Request

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code coverage >80%
- [ ] No linting errors
- [ ] Security audit passes
- [ ] Documentation updated
- [ ] E2E tests pass

### Deployment Validation

- [ ] All services start successfully
- [ ] Health endpoints respond
- [ ] Database migrations applied
- [ ] Authentication works
- [ ] Workflow CRUD operations work
- [ ] Message processing works
- [ ] Monitoring dashboards show data

## Unit Test Examples

### Testing Parent Agent

```python
# tests/agents/test_parent_agent.py
import pytest
from src.agents.parent_agent import ParentAgent, SupervisionResult

@pytest.fixture
def parent_agent():
    config = {
        "safety_check": True,
        "content_filter": True,
        "rate_limit": 100
    }
    return ParentAgent(config)

def test_safety_check_blocks_harmful_content(parent_agent):
    """Test that harmful content is blocked"""
    message = "How to hack into a system"
    context = {"user_id": "test_user"}
    
    result = parent_agent.supervise(message, context)
    
    assert result.allow is False
    assert "safety" in result.reason.lower()

def test_rate_limit_enforced(parent_agent):
    """Test rate limiting"""
    context = {"user_id": "test_user"}
    
    # Simulate 100 messages
    for i in range(100):
        result = parent_agent.supervise(f"Message {i}", context)
        assert result.allow is True
    
    # 101st message should be blocked
    result = parent_agent.supervise("Extra message", context)
    assert result.allow is False
    assert "rate limit" in result.reason.lower()
```

### Testing Authentication

```python
# tests/auth/test_jwt.py
import pytest
from src.auth.jwt import create_access_token, verify_token

def test_create_and_verify_token():
    """Test JWT token creation and verification"""
    data = {"tenant_id": "test-tenant-123", "user_id": "user-456"}
    
    token = create_access_token(data)
    assert token is not None
    
    decoded = verify_token(token)
    assert decoded["tenant_id"] == "test-tenant-123"
    assert decoded["user_id"] == "user-456"

def test_expired_token_rejected():
    """Test that expired tokens are rejected"""
    import time
    from datetime import timedelta
    
    data = {"tenant_id": "test-tenant"}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    
    with pytest.raises(Exception):
        verify_token(token)
```

### Testing Workflow Service

```python
# tests/services/test_workflow_service.py
import pytest
from src.services.workflow_service import WorkflowService

@pytest.fixture
async def workflow_service():
    return WorkflowService()

@pytest.mark.asyncio
async def test_create_workflow(workflow_service):
    """Test workflow creation"""
    workflow_data = {
        "name": "Test Workflow",
        "description": "Test description",
        "definition": {"nodes": [], "edges": []}
    }
    
    workflow = await workflow_service.create_workflow(
        tenant_id="tenant-123",
        **workflow_data
    )
    
    assert workflow.name == "Test Workflow"
    assert workflow.status == "draft"
    assert workflow.version == 1

@pytest.mark.asyncio
async def test_tenant_isolation(workflow_service):
    """Test that workflows are tenant-isolated"""
    # Create workflow for tenant A
    workflow_a = await workflow_service.create_workflow(
        tenant_id="tenant-a",
        name="Workflow A",
        definition={}
    )
    
    # Try to access from tenant B
    workflow = await workflow_service.get_workflow(
        workflow_id=workflow_a.id,
        tenant_id="tenant-b"
    )
    
    assert workflow is None  # Should not be accessible
```

## Integration Test Example

```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_full_message_flow():
    """Test complete message processing flow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Signup
        signup = await client.post("/api/v1/auth/signup", json={
            "email": "test@example.com",
            "password": "Test123!",
            "tenant_name": "Test Tenant"
        })
        assert signup.status_code == 200
        token = signup.json()["access_token"]
        
        # 2. Create workflow
        workflow = await client.post(
            "/api/v1/workflows",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test Workflow",
                "definition": {"nodes": [], "edges": []}
            }
        )
        assert workflow.status_code == 200
        
        # 3. Process message (mocked webhook)
        # This would test the full pipeline:
        # webhook → queue → parent agent → workflow → response
```

## Performance Testing

### Load Testing with Locust

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class IntraFlowUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        self.token = response.json()["access_token"]
    
    @task
    def list_workflows(self):
        self.client.get(
            "/api/v1/workflows",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(3)
    def create_workflow(self):
        self.client.post(
            "/api/v1/workflows",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "name": "Load Test Workflow",
                "definition": {"nodes": [], "edges": []}
            }
        )
```

Run load test:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## Security Testing

### Authentication Tests
- [ ] Invalid JWT tokens rejected
- [ ] Expired tokens rejected
- [ ] Weak passwords rejected
- [ ] SQL injection blocked
- [ ] XSS attempts blocked

### Authorization Tests
- [ ] Tenant A cannot access Tenant B's data
- [ ] Non-admin cannot access admin endpoints
- [ ] Rate limiting enforced

### Webhook Security
- [ ] Invalid HMAC signatures rejected
- [ ] Replay attacks prevented
- [ ] Oversized payloads rejected

## Continuous Testing

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Linting
cd agent-orchestrator
ruff check src/

# Unit tests
pytest tests/ -v

echo "All checks passed!"
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd agent-orchestrator
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd agent-orchestrator
          pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Data Management

### Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def db_session():
    """Create test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
def sample_workflow():
    """Sample workflow data"""
    return {
        "name": "Test Workflow",
        "description": "Sample workflow for testing",
        "definition": {
            "nodes": [
                {"id": "start", "type": "trigger"},
                {"id": "msg1", "type": "message", "data": {"message": "Hello"}}
            ],
            "edges": [{"source": "start", "target": "msg1"}]
        }
    }
```

## Best Practices

1. **Test Independence**: Each test should be independent
2. **Mock External Services**: Mock LLM APIs, external APIs
3. **Use Fixtures**: Share common setup via pytest fixtures
4. **Descriptive Names**: Test names should describe what they test
5. **Arrange-Act-Assert**: Structure tests clearly
6. **Edge Cases**: Test boundary conditions and error cases
7. **Performance**: Keep unit tests fast (<100ms each)

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
