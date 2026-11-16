# FastAPI Consolidation - Architecture Update

## Overview

The IntraFlow architecture has been **simplified** from a two-service design (Node.js + Python) to a **single consolidated FastAPI service**. This reduces complexity, improves maintainability, and simplifies deployment.

---

## Previous Architecture (Node.js + Python)

```
WhatsApp → OpenWA → Node.js Webhook Handler → Redis Queue → Python Agent Orchestrator → Response
                     (Express.js)                            (FastAPI + LangChain)
```

**Components:**
- **webhook-handler/** (Node.js/TypeScript)
  - Express server
  - HMAC verification
  - Message queuing
  - Metrics

- **agent-orchestrator/** (Python/FastAPI)
  - LangChain agents
  - Workflow execution
  - Database operations

---

## New Architecture (FastAPI Only)

```
WhatsApp → OpenWA → FastAPI Service → Redis Queue → Worker → Response
                     (All-in-one)      (Internal)    (Async)
```

**Single Service:**
- **agent-orchestrator/** (Python/FastAPI)
  - ✅ Webhook endpoints with HMAC verification
  - ✅ Message queue management (Redis)
  - ✅ Async worker processing
  - ✅ JWT authentication
  - ✅ Parent Agent guardrails
  - ✅ Workflow execution
  - ✅ LangChain agent orchestration
  - ✅ Database operations (SQLAlchemy + asyncpg)
  - ✅ Multi-tenant isolation
  - ✅ Prometheus metrics

---

## Key Changes

### 1. Consolidated Codebase

**Before:**
```
├── webhook-handler/         (Node.js)
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── agent-orchestrator/      (Python)
│   ├── src/
│   ├── requirements.txt
│   └── Dockerfile
```

**After:**
```
├── agent-orchestrator/      (Python FastAPI - Everything)
│   ├── src/
│   │   ├── webhooks/        ← NEW: Webhook handling
│   │   ├── auth/            ← NEW: JWT authentication
│   │   ├── database/        ← NEW: SQLAlchemy models
│   │   ├── services/        ← NEW: Queue, OpenWA client
│   │   ├── agents/          ← Parent Agent, orchestrator
│   │   ├── workflow/        ← Workflow executor
│   │   └── api/             ← REST API routes
│   ├── tests/               ← NEW: Pytest unit tests
│   ├── requirements.txt
│   └── Dockerfile
```

### 2. New Module Structure

```python
src/
├── webhooks/
│   ├── handler.py              # Webhook endpoint (/webhook)
│   └── verification.py         # HMAC-SHA256 validation
│
├── auth/
│   ├── jwt.py                  # JWT token management
│   └── password.py             # bcrypt password hashing
│
├── database/
│   ├── connection.py           # AsyncPG connection pool
│   ├── models.py               # SQLAlchemy ORM models
│   └── __init__.py
│
├── services/
│   ├── queue_service.py        # Redis queue (lpush/brpop)
│   ├── openwa_client.py        # OpenWA API client
│   └── session_service.py      # Session-to-tenant mapping
│
├── agents/
│   ├── parent_agent.py         # Guardrail system
│   ├── orchestrator.py         # Main orchestrator
│   ├── product_search.py       # Specialized agent
│   ├── order_management.py     # Specialized agent
│   └── customer_support.py     # Specialized agent
│
├── workflow/
│   └── executor.py             # Visual workflow engine
│
├── api/
│   ├── auth_routes.py          # /api/v1/auth (signup, login)
│   └── routes.py               # /agent (process message)
│
└── main.py                     # FastAPI app entry point
```

### 3. Docker Compose Simplification

**Before:**
- `openwa` service
- `webhook-handler` service (Node.js)
- `agent-orchestrator` service (Python)
- `postgres`, `redis`, monitoring

**After:**
- `openwa` service
- `agent-orchestrator` service (Python - consolidated)
- `postgres`, `redis`, monitoring

**Benefit:** One fewer Docker container, simpler networking

---

## Message Processing Pipeline

### Complete Flow

```mermaid
graph TD
    User[WhatsApp User] --> OpenWA[OpenWA Gateway]
    OpenWA -->|HTTP POST| Webhook[/webhook endpoint]
    Webhook -->|Verify HMAC| Validator[Signature Validator]
    Validator -->|Valid| Queue[Redis Queue]
    Queue --> Worker[Async Worker]
    Worker --> SessionMap[Session→Tenant Mapper]
    SessionMap --> ParentAgent[Parent Agent Guardrails]
    ParentAgent -->|Allow| Workflow[Load Tenant Workflow]
    ParentAgent -->|Block| BlockMsg[Send Block Message]
    Workflow --> Executor[Workflow Executor]
    Executor --> SpecializedAgent[Specialized Agents]
    SpecializedAgent --> LLM[LLM API Call]
    LLM --> Response[Generate Response]
    Response --> OpenWAClient[OpenWA Client]
    OpenWAClient --> OpenWA
    OpenWA --> User
    BlockMsg --> OpenWAClient
```

### Code Flow

1. **Webhook Receipt** (`src/webhooks/handler.py`)
   ```python
   @router.post("/webhook")
   async def handle_webhook(request: Request, x_signature: str):
       verify_webhook_signature(raw_body, x_signature)  # HMAC check
       await queue_message(message_data)                # Redis lpush
   ```

2. **Queue Processing** (`src/services/queue_service.py`)
   ```python
   async def start_worker():
       while True:
           message_json = await redis.brpop("whatsapp_messages")
           await process_message(message_data)
   ```

3. **Tenant Resolution** (`src/services/session_service.py`)
   ```python
   tenant_id = await session_service.get_tenant_by_session(session_id)
   ```

4. **Parent Agent Check** (`src/agents/parent_agent.py`)
   ```python
   result = await parent_agent.supervise(message, context)
   if not result.allow:
       return  # Block message
   ```

5. **Workflow Execution** (`src/agents/orchestrator.py`)
   ```python
   orchestrator = AgentOrchestrator()
   response = await orchestrator.process_message(user_id, message, context)
   ```

6. **Response Delivery** (`src/services/openwa_client.py`)
   ```python
   openwa = OpenWAClient()
   await openwa.send_text_message(session_id, to, response["response"])
   ```

---

## API Endpoints

### Webhooks
- `POST /webhook` - Receive WhatsApp messages from OpenWA

### Authentication
- `POST /api/v1/auth/signup` - Register new tenant
- `POST /api/v1/auth/login` - Login with JWT

### Agent Processing
- `POST /agent/process` - Process message (internal)

### Health & Metrics
- `GET /` - Service info
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

---

## Environment Variables

```bash
# Application
ENVIRONMENT=production
PORT=8000
DEBUG=false

# Security
WEBHOOK_SECRET=random-secret-here
JWT_SECRET=random-jwt-secret-here

# OpenWA
OPENWA_API_URL=http://openwa:2785/api
OPENWA_API_KEY=your-api-key

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/whatsapp

# Redis
REDIS_URL=redis://redis:6379
REDIS_QUEUE_NAME=whatsapp_messages

# LLM
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

---

## Testing

### Unit Tests (pytest)

```bash
cd agent-orchestrator
pytest tests/ -v --cov=src
```

**Test Coverage:**
- ✅ `tests/test_auth.py` - JWT & password hashing
- ✅ `tests/test_webhook.py` - HMAC verification & payload validation
- 🚧 `tests/test_parent_agent.py` - Guardrail checks
- 🚧 `tests/test_workflow.py` - Workflow execution
- 🚧 `tests/test_integration.py` - End-to-end flow

---

## Benefits of Consolidation

### Development
- ✅ Single codebase to maintain
- ✅ One programming language (Python)
- ✅ Shared dependencies
- ✅ Easier debugging

### Deployment
- ✅ One Docker image to build
- ✅ Simpler docker-compose.yml
- ✅ Fewer containers to manage
- ✅ Reduced resource usage

### Performance
- ✅ No inter-service HTTP calls
- ✅ Direct function calls
- ✅ Shared memory space
- ✅ Lower latency

### Security
- ✅ Single authentication system
- ✅ Consistent error handling
- ✅ Unified logging

---

## Migration Checklist

- [x] Remove `webhook-handler/` directory
- [x] Create `src/webhooks/` module
- [x] Create `src/auth/` module
- [x] Create `src/database/` module
- [x] Create `src/services/` module
- [x] Update `docker-compose.yml`
- [x] Update `.env.example`
- [x] Create unit tests
- [ ] Run integration tests
- [ ] Build Docker image
- [ ] Test full deployment

---

## Next Steps

1. **Complete Parent Agent Integration**
   - Wire into message pipeline
   - Test all 5 guardrail checks

2. **Workflow Service Layer**
   - CRUD API endpoints
   - Database persistence
   - Execution tracking

3. **Frontend Workflow Builder**
   - React + React Flow
   - Visual node editor
   - Chat simulator

4. **Production Deployment**
   - AWS EC2 setup
   - CI/CD pipeline
   - Monitoring dashboards

---

**Document Version**: 1.0  
**Last Updated**: November 16, 2026  
**Status**: ✅ FastAPI consolidation complete, ready for next phase
