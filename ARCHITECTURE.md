# System Architecture - WhatsApp Business Agentic Workflow

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Data Flow](#data-flow)
4. [Component Specifications](#component-specifications)
5. [Database Schema](#database-schema)
6. [API Specifications](#api-specifications)
7. [Deployment Architecture](#deployment-architecture)
8. [Scaling Strategy](#scaling-strategy)

## System Overview

### High-Level Architecture

```
                                    ┌──────────────────┐
                                    │   WhatsApp User  │
                                    └────────┬─────────┘
                                             │
                                             │ Messages
                                             ▼
                      ┌──────────────────────────────────────┐
                      │         OpenWA Gateway               │
                      │  (WhatsApp Web API - Port 2785)      │
                      │  - Session Management                │
                      │  - QR Code Auth                      │
                      │  - Message Send/Receive              │
                      └────────┬─────────────────────────────┘
                               │
                               │ Webhooks (HTTP POST)
                               ▼
                      ┌─────────────────────────────────────┐
                      │     Webhook Handler Service          │
                      │      (Node.js - Port 3000)           │
                      │  - HMAC Verification                 │
                      │  - Message Validation                │
                      │  - Request Routing                   │
                      └────────┬────────────────────────────┘
                               │
                               │ Internal API
                               ▼
                      ┌─────────────────────────────────────┐
                      │   Agent Orchestrator Service         │
                      │   (LangGraph + LangChain)            │
                      │  ┌───────────────────────────────┐   │
                      │  │ Intent Classifier             │   │
                      │  └───────────┬───────────────────┘   │
                      │              │                       │
                      │  ┌───────────▼───────────────────┐   │
                      │  │ Router (State Machine)        │   │
                      │  └───┬───────┬───────┬───────────┘   │
                      │      │       │       │               │
                      │  ┌───▼───┐ ┌▼────┐ ┌▼─────────┐     │
                      │  │Product│ │Order│ │ Support  │     │
                      │  │Search │ │ Mgmt│ │  Agent   │     │
                      │  │Agent  │ │Agent│ │          │     │
                      │  └───────┘ └─────┘ └──────────┘     │
                      └────────┬────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────────┐ ┌─────────────┐ ┌──────────────┐
    │  PostgreSQL DB  │ │   Redis     │ │  External    │
    │   (Port 5432)   │ │ (Port 6379) │ │     APIs     │
    │                 │ │             │ │  - Products  │
    │ - Conversations │ │ - Sessions  │ │  - Orders    │
    │ - Messages      │ │ - Cache     │ │  - Inventory │
    │ - Users         │ │ - Locks     │ │              │
    │ - Logs          │ │             │ │              │
    └─────────────────┘ └─────────────┘ └──────────────┘
              │
              ▼
    ┌─────────────────────────────────────────────┐
    │       Monitoring & Observability            │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
    │  │Prometheus│  │ Grafana  │  │   Loki   │  │
    │  │(Port     │  │(Port     │  │(Port     │  │
    │  │ 9090)    │  │ 3001)    │  │ 3100)    │  │
    │  └──────────┘  └──────────┘  └──────────┘  │
    └─────────────────────────────────────────────┘
```

## Architecture Layers

### Layer 1: Communication Layer (OpenWA Gateway)

**Purpose**: Handle WhatsApp connection and message transport

**Responsibilities**:
- Maintain WhatsApp session via reverse-engineered protocol
- Send and receive WhatsApp messages
- Manage authentication (QR code, pairing code)
- Deliver webhooks to application services
- Store session data and media

**Technology Stack**:
- OpenWA (Docker container)
- Baileys or whatsapp-web.js engine
- SQLite or PostgreSQL for session storage
- Local filesystem or S3 for media

**Configuration**:
```yaml
Environment Variables:
  - DATABASE_TYPE: postgresql
  - DATABASE_URL: postgresql://user:pass@db:5432/openwa
  - STORAGE_TYPE: local
  - REDIS_ENABLED: true
  - REDIS_URL: redis://redis:6379
  - WEBHOOK_URL: http://webhook-handler:3000/webhook
  - WEBHOOK_SECRET: <random-hmac-secret>
```

### Layer 2: Webhook Handler Service

**Purpose**: Receive and process incoming webhooks from OpenWA

**Responsibilities**:
- Validate HMAC signatures
- Parse and validate message payloads
- Implement rate limiting
- Forward to agent orchestrator
- Handle retries and dead letter queue

**Technology Stack**:
- Node.js with Express
- TypeScript
- Joi for validation
- Bull for job queues (backed by Redis)

**API Endpoints**:
```
POST /webhook - Receive webhooks from OpenWA
GET  /health  - Health check endpoint
GET  /metrics - Prometheus metrics
```

### Layer 3: Agent Orchestrator Service

**Purpose**: Manage conversation state and route to specialized agents

**Responsibilities**:
- Classify user intent
- Maintain conversation context and memory
- Route to appropriate specialized agents
- Orchestrate multi-step workflows
- Generate responses using LLMs
- Track agent performance

**Technology Stack**:
- Python 3.11+
- LangChain + LangGraph
- OpenAI API or Anthropic Claude
- FastAPI for HTTP endpoints
- PostgreSQL for state persistence
- Redis for session management

**Agent Types**:

1. **Product Search Agent**
   - Handles product queries
   - Searches product catalog
   - Provides recommendations
   - Tools: product_search, get_product_details, filter_products

2. **Order Management Agent**
   - Creates new orders
   - Tracks order status
   - Handles modifications and cancellations
   - Tools: create_order, get_order_status, cancel_order

3. **Customer Support Agent**
   - Answers FAQs
   - Handles complaints
   - Escalates to human agents
   - Tools: search_kb, create_ticket, escalate

4. **API Integration Agent**
   - Calls external APIs for data
   - Handles authentication
   - Transforms responses
   - Tools: call_external_api, transform_data

### Layer 4: Data Layer

#### PostgreSQL Database

**Schemas**:

**users** table:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    whatsapp_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

**conversations** table:
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    metadata JSONB
);
```

**messages** table:
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    message_id VARCHAR(255) UNIQUE,
    direction VARCHAR(20) NOT NULL, -- 'inbound' or 'outbound'
    content TEXT,
    message_type VARCHAR(50), -- 'text', 'image', 'audio', 'video'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

**agent_interactions** table:
```sql
CREATE TABLE agent_interactions (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    agent_type VARCHAR(100),
    intent VARCHAR(255),
    confidence DECIMAL(5,2),
    tools_used JSONB,
    llm_tokens_used INTEGER,
    response_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**orders** table (example business logic):
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_number VARCHAR(100) UNIQUE,
    status VARCHAR(50), -- 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled'
    total_amount DECIMAL(10,2),
    items JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Redis Cache

**Key Patterns**:
```
session:{user_id}:state        -> Conversation state
session:{user_id}:context      -> Conversation context
session:{user_id}:memory       -> Short-term memory
rate_limit:{user_id}:{window}  -> Rate limiting counters
agent_lock:{conversation_id}   -> Distributed locks
```

**TTL Configuration**:
- Session state: 1 hour
- Context: 24 hours
- Memory: 7 days
- Rate limit: 1 minute/hour
- Locks: 30 seconds

### Layer 5: Monitoring & Observability

#### Prometheus Metrics

**Application Metrics**:
```
# Webhook Handler
webhook_requests_total{status}
webhook_processing_duration_seconds
webhook_validation_failures_total

# Agent Orchestrator
agent_requests_total{agent_type, intent}
agent_response_time_seconds{agent_type}
agent_llm_tokens_used{agent_type, model}
agent_errors_total{agent_type, error_type}

# OpenWA
openwa_messages_sent_total
openwa_messages_received_total
openwa_session_status{session_id}
openwa_webhook_delivery_failures_total
```

**Business Metrics**:
```
conversations_started_total
conversations_completed_total{outcome}
user_satisfaction_score
order_conversion_rate
average_conversation_length
```

#### Grafana Dashboards

**Dashboard 1: System Health**
- Service uptime
- Request rates
- Error rates
- Response times
- Resource utilization (CPU, memory, disk)

**Dashboard 2: Business Metrics**
- Active users (hourly/daily/weekly)
- Message volume
- Conversation funnel
- Top intents
- Agent performance

**Dashboard 3: Agent Performance**
- Intent classification accuracy
- Agent routing distribution
- Average response time per agent
- LLM token usage and costs
- Tool usage statistics

## Data Flow

### Inbound Message Flow

```
1. User sends WhatsApp message
   ↓
2. OpenWA receives message via WhatsApp Web protocol
   ↓
3. OpenWA stores message in database
   ↓
4. OpenWA sends webhook to Webhook Handler
   POST /webhook with HMAC signature
   {
     "event": "message",
     "sessionId": "main-session",
     "message": {
       "id": "msg_123",
       "from": "628123456789@c.us",
       "body": "I want to search for a product",
       "timestamp": 1700000000,
       "type": "text"
     }
   }
   ↓
5. Webhook Handler verifies HMAC signature
   ↓
6. Webhook Handler validates payload schema
   ↓
7. Webhook Handler creates job in Bull queue
   ↓
8. Job processor calls Agent Orchestrator API
   POST /agent/process
   {
     "userId": "628123456789",
     "message": "I want to search for a product",
     "context": {...}
   }
   ↓
9. Agent Orchestrator loads conversation state from Redis
   ↓
10. Intent Classifier (LLM) determines intent: "product_search"
   ↓
11. Router directs to Product Search Agent
   ↓
12. Product Search Agent uses tools:
    - product_search("laptop")
    - get_product_details(product_id)
   ↓
13. Agent generates response using LLM
   ↓
14. Response saved to database
   ↓
15. State updated in Redis
   ↓
16. Agent Orchestrator returns response to Webhook Handler
   {
     "response": "I found 5 laptops. Here are the top 3...",
     "buttons": [...],
     "nextAction": "await_user_selection"
   }
   ↓
17. Webhook Handler calls OpenWA API to send message
   POST http://openwa:2785/api/messages/text
   {
     "sessionId": "main-session",
     "chatId": "628123456789@c.us",
     "text": "I found 5 laptops. Here are the top 3...",
   }
   ↓
18. OpenWA sends message to user
   ↓
19. User receives message on WhatsApp
```

### Outbound Message Flow (Proactive)

```
1. System event triggers (e.g., order shipped)
   ↓
2. Background service creates notification job
   ↓
3. Job processor formats message
   ↓
4. Calls OpenWA API to send message
   POST /api/messages/text
   ↓
5. OpenWA sends message to user
   ↓
6. Message logged in database
```

## Component Specifications

### Webhook Handler Service

**File Structure**:
```
webhook-handler/
├── src/
│   ├── index.ts              # Entry point
│   ├── routes/
│   │   ├── webhook.ts        # Webhook endpoint
│   │   ├── health.ts         # Health check
│   │   └── metrics.ts        # Prometheus metrics
│   ├── services/
│   │   ├── hmacVerifier.ts   # Signature verification
│   │   ├── messageValidator.ts
│   │   ├── queueService.ts   # Bull queue
│   │   └── agentClient.ts    # Calls Agent Orchestrator
│   ├── processors/
│   │   └── messageProcessor.ts
│   └── config/
│       └── config.ts
├── package.json
├── tsconfig.json
└── Dockerfile
```

**Key Configuration**:
```typescript
interface Config {
  port: number;
  openwaWebhookSecret: string;
  agentOrchestratorUrl: string;
  redisUrl: string;
  maxRetries: number;
  rateLimitPerMinute: number;
}
```

### Agent Orchestrator Service

**File Structure**:
```
agent-orchestrator/
├── src/
│   ├── main.py                    # FastAPI entry point
│   ├── api/
│   │   └── routes.py              # HTTP endpoints
│   ├── agents/
│   │   ├── base_agent.py          # Base agent class
│   │   ├── orchestrator.py        # Main orchestrator
│   │   ├── product_search.py      # Product search agent
│   │   ├── order_management.py    # Order management agent
│   │   └── customer_support.py    # Support agent
│   ├── tools/
│   │   ├── product_api.py         # Product API tools
│   │   ├── order_api.py           # Order API tools
│   │   └── knowledge_base.py      # KB search tools
│   ├── llm/
│   │   ├── chat_models.py         # LLM configurations
│   │   └── prompts.py             # Prompt templates
│   ├── state/
│   │   ├── conversation_state.py  # State management
│   │   └── memory.py              # Conversation memory
│   └── config/
│       └── settings.py
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

**LangGraph State Machine**:
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(ConversationState)

workflow.add_node("classify_intent", classify_intent)
workflow.add_node("product_search", product_search_agent)
workflow.add_node("order_management", order_management_agent)
workflow.add_node("customer_support", customer_support_agent)
workflow.add_node("generate_response", generate_response)

workflow.add_edge("classify_intent", "route")
workflow.add_conditional_edges(
    "route",
    route_to_agent,
    {
        "product_search": "product_search",
        "order_management": "order_management",
        "customer_support": "customer_support",
    }
)
workflow.add_edge("product_search", "generate_response")
workflow.add_edge("order_management", "generate_response")
workflow.add_edge("customer_support", "generate_response")
workflow.add_edge("generate_response", END)

app = workflow.compile()
```

## Deployment Architecture

### Docker Compose Setup

**Services**:
1. **openwa** - WhatsApp Gateway (port 2785)
2. **webhook-handler** - Node.js service (port 3000)
3. **agent-orchestrator** - Python service (port 8000)
4. **postgres** - Database (port 5432)
5. **redis** - Cache (port 6379)
6. **prometheus** - Metrics (port 9090)
7. **grafana** - Dashboards (port 3001)
8. **loki** - Logs (port 3100)

**Network**:
- All services on `whatsapp-net` bridge network
- Only webhook-handler and openwa exposed to host

**Volumes**:
- postgres-data: Database persistence
- redis-data: Redis persistence
- openwa-sessions: WhatsApp session data
- grafana-data: Dashboard configurations
- prometheus-data: Metrics storage

### EC2 Deployment

**Instance Specifications**:
```
Type: t3.large (2 vCPU, 8GB RAM)
OS: Amazon Linux 2023 or Ubuntu 22.04
Disk: 100GB gp3 SSD
Network: VPC with public subnet
Security Group:
  - SSH (22) from your IP
  - HTTP (80) for dashboard (optional)
  - HTTPS (443) for dashboard (optional)
  - OpenWA (2785) from localhost only
  - Grafana (3001) from your IP
```

**Setup Steps**:
1. Install Docker and Docker Compose
2. Clone repository
3. Configure environment variables
4. Run `docker-compose up -d`
5. Scan QR code to authenticate WhatsApp
6. Configure webhooks
7. Test with sample messages

## Scaling Strategy

### Vertical Scaling (Phase 1: < 1000 users)
- Upgrade EC2 instance (t3.large → t3.xlarge → t3.2xlarge)
- Increase PostgreSQL resources
- Add read replicas for database

### Horizontal Scaling (Phase 2: 1000-10000 users)
- Multiple webhook-handler instances (load balanced)
- Multiple agent-orchestrator instances
- Separate database server
- Redis cluster for high availability
- Message queue (RabbitMQ or AWS SQS) for decoupling

### Cloud-Native Scaling (Phase 3: 10000+ users)
- Kubernetes cluster (EKS)
- Managed services:
  - RDS PostgreSQL (multi-AZ)
  - ElastiCache Redis (cluster mode)
  - Application Load Balancer
  - CloudWatch for monitoring
- Auto-scaling based on metrics
- Multi-region deployment for DR

### Cost Optimization
- Use spot instances for non-critical services
- Implement request caching aggressively
- Optimize LLM token usage:
  - Use smaller models for simple intents
  - Cache common responses
  - Implement smart context pruning
- Archive old messages to S3 Glacier

---

**Document Version**: 1.0  
**Last Updated**: November 16, 2026  
**Next Review**: After Phase 1 implementation
