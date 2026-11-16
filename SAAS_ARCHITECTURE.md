# Multi-Tenant SaaS Architecture

## Overview

This document describes the architecture for transforming the WhatsApp Agent system into a **multi-tenant SaaS platform** where multiple customers can onboard, each with their own isolated WhatsApp sessions, workflows, and data.

## Table of Contents
1. [Multi-Tenancy Architecture](#multi-tenancy-architecture)
2. [Workflow Builder System](#workflow-builder-system)
3. [Admin Dashboard](#admin-dashboard)
4. [Database Schema Updates](#database-schema-updates)
5. [API Changes](#api-changes)
6. [Deployment Architecture](#deployment-architecture)

---

## 1. Multi-Tenancy Architecture

### 1.1 Tenant Isolation Model

```
┌─────────────────────────────────────────────────────────────┐
│                    SaaS Platform                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Tenant 1   │  │   Tenant 2   │  │   Tenant 3   │      │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤      │
│  │ WhatsApp #1  │  │ WhatsApp #2  │  │ WhatsApp #3  │      │
│  │ Workflow A   │  │ Workflow C   │  │ Workflow E   │      │
│  │ Workflow B   │  │ Workflow D   │  │ Workflow F   │      │
│  │ Users        │  │ Users        │  │ Users        │      │
│  │ Messages     │  │ Messages     │  │ Messages     │      │
│  │ Analytics    │  │ Analytics    │  │ Analytics    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Tenant Hierarchy

```
Organization (Tenant)
├── Owner User
├── Admin Users
├── Regular Users
├── WhatsApp Sessions (1 or more)
│   ├── Session 1 (Primary)
│   └── Session 2 (Backup)
├── Workflows
│   ├── Workflow 1: Lead Qualification
│   ├── Workflow 2: Customer Support
│   └── Workflow 3: Order Tracking
├── End Users (WhatsApp contacts)
├── Messages
├── API Keys
└── Billing/Subscription

```

### 1.3 Multi-Tenant Database Strategy

**Approach: Shared Database, Shared Schema, Tenant-Scoped Queries**

Every table includes `tenant_id` for isolation:

```sql
-- All queries include: WHERE tenant_id = ?
SELECT * FROM conversations WHERE tenant_id = 'tenant_uuid' AND ...
```

**Benefits:**
- Cost-effective (single database)
- Easy to manage
- Simple backups
- Cross-tenant analytics possible

**Security:**
- Row-level security (RLS) in PostgreSQL
- Application-level tenant filtering
- API middleware enforces tenant scope

---

## 2. Workflow Builder System

### 2.1 Workflow Definition Model

Workflows are **directed graphs** of nodes connected by edges:

```
[Start]
   ↓
[Trigger: User Message]
   ↓
[Classify Intent]
   ↓
[Decision: Intent = ?]
   ├─→ [Product Search]
   │      ↓
   │   [Show Products]
   │      ↓
   │   [Ask: Want to Order?]
   │      ├─→ [Yes] → [Create Order]
   │      └─→ [No] → [Send Thank You]
   │
   ├─→ [Order Status]
   │      ↓
   │   [Ask: Order Number]
   │      ↓
   │   [API: Fetch Order]
   │      ↓
   │   [Send Order Status]
   │
   └─→ [Support]
          ↓
       [FAQ Response]
          ↓
       [Ask: Resolved?]
          ├─→ [Yes] → [End]
          └─→ [No] → [Escalate to Human]
```

### 2.2 Node Types

#### **1. Trigger Nodes**
- `message_received` - User sends message
- `button_clicked` - User clicks button
- `schedule` - Time-based trigger
- `api_webhook` - External API call

#### **2. Action Nodes**
- `send_message` - Send text message
- `send_media` - Send image/video/document
- `send_buttons` - Send interactive buttons
- `send_list` - Send list message
- `api_call` - Call external API
- `database_query` - Query database
- `delay` - Wait for X seconds
- `set_variable` - Store data
- `send_email` - Send email notification

#### **3. Logic Nodes**
- `condition` - If-then-else branching
- `switch` - Multiple branches based on value
- `ai_classifier` - LLM-based classification
- `regex_match` - Pattern matching
- `loop` - Iterate over items

#### **4. Integration Nodes**
- `google_sheets` - Read/write Google Sheets
- `airtable` - Airtable operations
- `stripe` - Payment processing
- `calendar` - Schedule appointments
- `crm_update` - Update CRM (Salesforce, HubSpot)

### 2.3 Workflow JSON Schema

```json
{
  "id": "wf_abc123",
  "tenant_id": "tenant_xyz",
  "name": "Lead Qualification Flow",
  "description": "Qualify leads and route to sales",
  "version": "1.0",
  "status": "active",
  "nodes": [
    {
      "id": "node_1",
      "type": "trigger",
      "subtype": "message_received",
      "config": {
        "trigger_on": "any_message"
      },
      "position": {"x": 100, "y": 100}
    },
    {
      "id": "node_2",
      "type": "action",
      "subtype": "send_message",
      "config": {
        "message": "Hi! What can I help you with today?",
        "buttons": [
          {"id": "btn_1", "text": "Product Info"},
          {"id": "btn_2", "text": "Pricing"},
          {"id": "btn_3", "text": "Talk to Sales"}
        ]
      },
      "position": {"x": 100, "y": 200}
    },
    {
      "id": "node_3",
      "type": "logic",
      "subtype": "condition",
      "config": {
        "variable": "button_clicked",
        "operator": "equals",
        "value": "btn_1",
        "true_branch": "node_4",
        "false_branch": "node_5"
      },
      "position": {"x": 100, "y": 300}
    },
    {
      "id": "node_4",
      "type": "action",
      "subtype": "send_message",
      "config": {
        "message": "Here are our products: ..."
      },
      "position": {"x": 50, "y": 400}
    },
    {
      "id": "node_5",
      "type": "action",
      "subtype": "ai_classifier",
      "config": {
        "model": "gpt-4o-mini",
        "prompt": "Classify user intent: {{user_message}}",
        "categories": ["pricing", "support", "sales"]
      },
      "position": {"x": 150, "y": 400}
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "node_1",
      "target": "node_2"
    },
    {
      "id": "edge_2",
      "source": "node_2",
      "target": "node_3",
      "condition": "button_clicked"
    },
    {
      "id": "edge_3",
      "source": "node_3",
      "target": "node_4",
      "label": "Product Info"
    },
    {
      "id": "edge_4",
      "source": "node_3",
      "target": "node_5",
      "label": "Other"
    }
  ],
  "variables": {
    "user_name": "",
    "user_email": "",
    "intent": "",
    "products_shown": []
  },
  "settings": {
    "timeout_seconds": 300,
    "fallback_message": "Sorry, I didn't understand. Please try again.",
    "enable_ai": true,
    "ai_model": "gpt-4o-mini"
  }
}
```

### 2.4 Workflow Execution Engine

#### **State Machine Execution**

```python
class WorkflowExecutor:
    """Executes workflow for a conversation"""
    
    def __init__(self, workflow: Workflow, conversation: Conversation):
        self.workflow = workflow
        self.conversation = conversation
        self.context = {}  # Runtime variables
        self.current_node = workflow.start_node
        
    async def execute(self, user_input: str):
        """Execute workflow step by step"""
        
        # 1. Update context with user input
        self.context['user_message'] = user_input
        
        # 2. Find current node
        node = self.get_node(self.current_node)
        
        # 3. Execute node
        result = await self.execute_node(node)
        
        # 4. Determine next node based on result
        next_node = self.get_next_node(node, result)
        
        # 5. Save state
        self.current_node = next_node
        await self.save_state()
        
        # 6. Return response to user
        return result
        
    async def execute_node(self, node: Node):
        """Execute specific node type"""
        
        if node.type == 'action':
            return await self.execute_action(node)
        elif node.type == 'logic':
            return await self.execute_logic(node)
        elif node.type == 'trigger':
            return await self.execute_trigger(node)
```

### 2.5 Visual Workflow Builder UI

#### **Technology Stack**
- **Frontend**: React + TypeScript
- **Flow Editor**: React Flow (https://reactflow.dev/)
- **UI Components**: shadcn/ui + Tailwind CSS
- **State Management**: Zustand
- **Backend API**: FastAPI

#### **UI Components**

```
┌─────────────────────────────────────────────────────────────┐
│  Workflow Builder - Lead Qualification                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Save]  [Test]  [Publish]  [Settings]                      │
│                                                              │
│  ┌────────────┐  ┌──────────────────────────────┐           │
│  │ Node Panel │  │  Canvas                      │           │
│  ├────────────┤  │                              │           │
│  │ Triggers   │  │   ┌─────────────┐            │           │
│  │  • Message │  │   │   Start     │            │           │
│  │  • Button  │  │   └──────┬──────┘            │           │
│  │  • Timer   │  │          │                   │           │
│  │            │  │          ▼                   │           │
│  │ Actions    │  │   ┌─────────────┐            │           │
│  │  • Send    │  │   │ Send Message│            │           │
│  │  • API Call│  │   │ "Hello!"    │            │           │
│  │  • Delay   │  │   └──────┬──────┘            │           │
│  │            │  │          │                   │           │
│  │ Logic      │  │          ▼                   │           │
│  │  • If/Else │  │   ┌─────────────┐            │           │
│  │  • Switch  │  │   │  Condition  │            │           │
│  │  • Loop    │  │   │  Intent=?   │            │           │
│  │            │  │   └─┬─────────┬─┘            │           │
│  │ AI         │  │     │         │              │           │
│  │  • Classify│  │     ▼         ▼              │           │
│  │  • Generate│  │  [Order]   [Support]         │           │
│  └────────────┘  │                              │           │
│                  └──────────────────────────────┘           │
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │ Node Properties                              │           │
│  ├──────────────────────────────────────────────┤           │
│  │ Type: Send Message                           │           │
│  │ Message: [Hello! How can I help?           ] │           │
│  │ Add Buttons: [+ Add]                         │           │
│  │ Delay: [0] seconds                           │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

#### **Workflow Builder Features**
1. **Drag-and-drop nodes** from palette to canvas
2. **Connect nodes** by dragging edges
3. **Configure nodes** via properties panel
4. **Test workflows** with simulation mode
5. **Version control** - save and restore versions
6. **Templates** - pre-built flows for common scenarios
7. **Import/Export** - JSON export/import

---

## 3. Admin Dashboard

### 3.1 Dashboard Structure

```
┌─────────────────────────────────────────────────────────────┐
│  WhatsApp SaaS Platform - Admin Dashboard                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Dashboard] [Tenants] [Billing] [Settings] [Support]       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Overview                                           │     │
│  ├────────────────────────────────────────────────────┤     │
│  │  Total Tenants: 145        Active: 132            │     │
│  │  Monthly Revenue: $12,450  MRR Growth: +15%       │     │
│  │  Total Messages: 1.2M      This Month: 345K       │     │
│  │  Active Sessions: 132      Failed: 3              │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Recent Tenants                                     │     │
│  ├────────────────────────────────────────────────────┤     │
│  │ Acme Corp        | Premium  | Active | 5 users    │     │
│  │ TechStart Inc    | Starter  | Active | 2 users    │     │
│  │ Retail Co        | Business | Trial  | 10 users   │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ System Health                                      │     │
│  ├────────────────────────────────────────────────────┤     │
│  │  OpenWA Gateway:     ✅ Healthy                    │     │
│  │  Webhook Handler:    ✅ Healthy                    │     │
│  │  Agent Orchestrator: ✅ Healthy                    │     │
│  │  Database:          ✅ Healthy                    │     │
│  │  Redis:             ✅ Healthy                    │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Tenant Dashboard (Customer View)

```
┌─────────────────────────────────────────────────────────────┐
│  My Dashboard - Acme Corp                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Dashboard] [Workflows] [WhatsApp] [Analytics] [Settings]  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ WhatsApp Connection                                │     │
│  ├────────────────────────────────────────────────────┤     │
│  │  Status: ✅ Connected                              │     │
│  │  Phone: +1 (555) 123-4567                          │     │
│  │  Session: acme-primary                             │     │
│  │  [Reconnect] [Add Backup Number]                   │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Active Workflows                                   │     │
│  ├────────────────────────────────────────────────────┤     │
│  │  ✅ Lead Qualification    | 234 runs | 95% success│     │
│  │  ✅ Customer Support      | 567 runs | 88% success│     │
│  │  ⏸️  Order Tracking       | Paused               │     │
│  │  [+ Create Workflow]                               │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Today's Stats                                      │     │
│  ├────────────────────────────────────────────────────┤     │
│  │  Messages Received: 145                            │     │
│  │  Messages Sent: 287                                │     │
│  │  Unique Users: 89                                  │     │
│  │  Avg Response Time: 2.3s                           │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Database Schema Updates

### 4.1 New Tables for Multi-Tenancy

```sql
-- =============================================
-- TENANTS (ORGANIZATIONS)
-- =============================================
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    
    -- Subscription
    plan VARCHAR(50) DEFAULT 'trial', -- 'trial', 'starter', 'business', 'enterprise'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'suspended', 'cancelled'
    trial_ends_at TIMESTAMP,
    subscription_started_at TIMESTAMP,
    
    -- Limits
    max_whatsapp_sessions INTEGER DEFAULT 1,
    max_workflows INTEGER DEFAULT 5,
    max_users INTEGER DEFAULT 3,
    max_messages_per_month INTEGER DEFAULT 1000,
    
    -- Billing
    stripe_customer_id VARCHAR(255),
    billing_email VARCHAR(255),
    
    -- Settings
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_status ON tenants(status);


-- =============================================
-- TENANT USERS (TEAM MEMBERS)
-- =============================================
CREATE TABLE tenant_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    
    role VARCHAR(50) DEFAULT 'member', -- 'owner', 'admin', 'member', 'viewer'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'invited', 'suspended'
    
    last_login_at TIMESTAMP,
    invited_by UUID REFERENCES tenant_users(id),
    invited_at TIMESTAMP,
    
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_tenant_users_tenant ON tenant_users(tenant_id);
CREATE INDEX idx_tenant_users_email ON tenant_users(email);


-- =============================================
-- WHATSAPP SESSIONS (PER TENANT)
-- =============================================
CREATE TABLE whatsapp_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL, -- OpenWA session ID
    phone_number VARCHAR(50),
    
    status VARCHAR(50) DEFAULT 'disconnected', -- 'connected', 'disconnected', 'qr_scan', 'failed'
    is_primary BOOLEAN DEFAULT FALSE,
    
    connected_at TIMESTAMP,
    last_active_at TIMESTAMP,
    qr_code TEXT,
    
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_whatsapp_sessions_tenant ON whatsapp_sessions(tenant_id);
CREATE INDEX idx_whatsapp_sessions_session_id ON whatsapp_sessions(session_id);


-- =============================================
-- WORKFLOWS
-- =============================================
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Workflow Definition (JSON)
    definition JSONB NOT NULL,
    
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'active', 'paused', 'archived'
    
    -- Stats
    total_runs INTEGER DEFAULT 0,
    successful_runs INTEGER DEFAULT 0,
    failed_runs INTEGER DEFAULT 0,
    avg_completion_time_ms INTEGER,
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    created_by UUID REFERENCES tenant_users(id),
    published_by UUID REFERENCES tenant_users(id),
    published_at TIMESTAMP,
    
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_workflows_tenant ON workflows(tenant_id);
CREATE INDEX idx_workflows_status ON workflows(status);


-- =============================================
-- WORKFLOW EXECUTIONS (RUNS)
-- =============================================
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    conversation_id INTEGER, -- References existing conversations table
    
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed', 'paused'
    
    -- Current State
    current_node_id VARCHAR(255),
    context JSONB DEFAULT '{}', -- Runtime variables
    
    -- Execution Log
    execution_log JSONB DEFAULT '[]', -- Array of executed nodes
    
    -- Timing
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    
    -- Error Info
    error_message TEXT,
    error_node_id VARCHAR(255),
    
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflow_executions_tenant ON workflow_executions(tenant_id);
CREATE INDEX idx_workflow_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_conversation ON workflow_executions(conversation_id);


-- =============================================
-- UPDATE EXISTING TABLES WITH TENANT_ID
-- =============================================

-- Users table - add tenant_id
ALTER TABLE users ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
CREATE INDEX idx_users_tenant ON users(tenant_id);

-- Conversations table - add tenant_id
ALTER TABLE conversations ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
ALTER TABLE conversations ADD COLUMN workflow_id UUID REFERENCES workflows(id);
CREATE INDEX idx_conversations_tenant ON conversations(tenant_id);
CREATE INDEX idx_conversations_workflow ON conversations(workflow_id);

-- Messages table - add tenant_id
ALTER TABLE messages ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
CREATE INDEX idx_messages_tenant ON messages(tenant_id);

-- Agent interactions table - add tenant_id
ALTER TABLE agent_interactions ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
CREATE INDEX idx_agent_interactions_tenant ON agent_interactions(tenant_id);

-- Orders table - add tenant_id
ALTER TABLE orders ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
CREATE INDEX idx_orders_tenant ON orders(tenant_id);


-- =============================================
-- USAGE TRACKING (FOR BILLING)
-- =============================================
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    metric VARCHAR(100) NOT NULL, -- 'messages_sent', 'messages_received', 'workflow_runs', 'ai_tokens'
    quantity INTEGER NOT NULL,
    
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, metric, period_start)
);

CREATE INDEX idx_usage_records_tenant ON usage_records(tenant_id);
CREATE INDEX idx_usage_records_period ON usage_records(period_start, period_end);


-- =============================================
-- API KEYS (PER TENANT)
-- =============================================
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL, -- First 8 chars for display
    
    permissions TEXT[] DEFAULT '{}', -- 'read', 'write', 'admin'
    
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    created_by UUID REFERENCES tenant_users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

CREATE INDEX idx_api_keys_tenant ON api_keys(tenant_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
```

---

## 5. API Changes

### 5.1 Authentication & Tenant Scoping

#### **JWT Token Structure**

```json
{
  "user_id": "user_abc123",
  "tenant_id": "tenant_xyz789",
  "role": "admin",
  "permissions": ["read", "write"],
  "exp": 1700000000
}
```

#### **API Middleware**

```python
from fastapi import Request, HTTPException
from jose import jwt

async def verify_tenant_access(request: Request):
    """Middleware to verify tenant access"""
    
    # 1. Extract JWT token
    token = request.headers.get("Authorization").replace("Bearer ", "")
    
    # 2. Decode token
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    # 3. Extract tenant_id
    tenant_id = payload.get("tenant_id")
    
    # 4. Store in request state
    request.state.tenant_id = tenant_id
    request.state.user_id = payload.get("user_id")
    request.state.role = payload.get("role")
    
    return tenant_id
```

#### **Tenant-Scoped Queries**

```python
# Every query automatically includes tenant_id
from sqlalchemy import select
from models import Conversation

async def get_conversations(tenant_id: str):
    """Get conversations for tenant"""
    stmt = select(Conversation).where(
        Conversation.tenant_id == tenant_id
    )
    return await session.execute(stmt)
```

### 5.2 New API Endpoints

```
# Tenant Management
POST   /api/v1/tenants                    # Create tenant (signup)
GET    /api/v1/tenants/{id}               # Get tenant info
PATCH  /api/v1/tenants/{id}               # Update tenant
DELETE /api/v1/tenants/{id}               # Delete tenant

# Authentication
POST   /api/v1/auth/signup                # Sign up
POST   /api/v1/auth/login                 # Login
POST   /api/v1/auth/logout                # Logout
POST   /api/v1/auth/refresh               # Refresh token
POST   /api/v1/auth/invite                # Invite team member

# WhatsApp Sessions
GET    /api/v1/sessions                   # List sessions
POST   /api/v1/sessions                   # Create session
GET    /api/v1/sessions/{id}              # Get session
GET    /api/v1/sessions/{id}/qr           # Get QR code
POST   /api/v1/sessions/{id}/disconnect   # Disconnect
DELETE /api/v1/sessions/{id}              # Delete session

# Workflows
GET    /api/v1/workflows                  # List workflows
POST   /api/v1/workflows                  # Create workflow
GET    /api/v1/workflows/{id}             # Get workflow
PATCH  /api/v1/workflows/{id}             # Update workflow
DELETE /api/v1/workflows/{id}             # Delete workflow
POST   /api/v1/workflows/{id}/publish     # Publish workflow
POST   /api/v1/workflows/{id}/test        # Test workflow
GET    /api/v1/workflows/{id}/executions  # Get execution history

# Analytics (Tenant-scoped)
GET    /api/v1/analytics/overview         # Dashboard stats
GET    /api/v1/analytics/messages         # Message stats
GET    /api/v1/analytics/workflows        # Workflow stats
GET    /api/v1/analytics/users            # User stats

# Billing
GET    /api/v1/billing/usage              # Current usage
GET    /api/v1/billing/invoices           # Invoice history
POST   /api/v1/billing/upgrade            # Upgrade plan
POST   /api/v1/billing/cancel             # Cancel subscription
```

---

## 6. Deployment Architecture

### 6.1 SaaS Deployment Stack

```
                    [Internet]
                         │
                         ▼
                   [Load Balancer]
                    (HTTPS/SSL)
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    [Web App 1]    [Web App 2]    [Web App 3]
    (Next.js)      (Next.js)      (Next.js)
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
                   [API Gateway]
                         │
         ┌───────────────┼───────────────────────┐
         ▼               ▼                       ▼
[Webhook Handler] [Agent Orch.]         [Workflow Engine]
    (Node.js)        (Python)             (Python)
         │               │                       │
         └───────────────┼───────────────────────┘
                         │
         ┌───────────────┼───────────────────┐
         ▼               ▼                   ▼
   [PostgreSQL]      [Redis]           [OpenWA Gateway]
   (RDS Multi-AZ)  (ElastiCache)      (EC2 Auto-scaling)
         │               │                   │
         └───────────────┼───────────────────┘
                         │
                         ▼
                [Monitoring Stack]
            (Prometheus + Grafana + Loki)
```

### 6.2 Recommended AWS Architecture

```
VPC
├── Public Subnet (ALB, NAT Gateway)
├── Private Subnet 1 (Application Tier)
│   ├── Web App (ECS Fargate)
│   ├── API Gateway (ECS Fargate)
│   ├── Webhook Handler (ECS Fargate)
│   └── Agent Orchestrator (ECS Fargate)
├── Private Subnet 2 (Data Tier)
│   ├── RDS PostgreSQL (Multi-AZ)
│   ├── ElastiCache Redis (Cluster)
│   └── OpenWA (EC2 Auto-scaling Group)
└── Monitoring
    ├── CloudWatch
    ├── Prometheus (ECS)
    └── Grafana (ECS)
```

### 6.3 Scaling Strategy

| Users | Architecture | Monthly Cost |
|-------|-------------|--------------|
| 0-100 | Single EC2 t3.xlarge | $150 |
| 100-1000 | Multi-container ECS | $500 |
| 1000-10000 | ECS + RDS + ElastiCache | $2000 |
| 10000+ | Multi-region, Auto-scaling | $5000+ |

---

## 7. Pricing Tiers

### Starter ($29/month)
- 1 WhatsApp number
- 5 workflows
- 1,000 messages/month
- 3 team members
- Email support

### Business ($99/month)
- 2 WhatsApp numbers
- 20 workflows
- 10,000 messages/month
- 10 team members
- Priority support
- API access

### Enterprise ($299/month)
- 5 WhatsApp numbers
- Unlimited workflows
- 100,000 messages/month
- Unlimited team members
- Dedicated support
- Custom integrations
- SLA guarantee

---

## Next Steps

1. **Implement Multi-Tenancy** - Update database schema and add tenant isolation
2. **Build Workflow Engine** - Implement node execution and state machine
3. **Create Visual Builder** - React Flow-based UI
4. **Build Admin Dashboard** - Tenant management, billing
5. **Add Authentication** - JWT-based auth with tenant scoping
6. **Implement Billing** - Stripe integration
7. **Deploy & Test** - Launch MVP with first customers

---

**Document Version**: 1.0  
**Last Updated**: November 16, 2026  
**Status**: Architecture Design
