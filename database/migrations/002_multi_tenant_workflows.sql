-- ==============================================
-- Multi-Tenant SaaS Migration
-- Adds tenants, workflows, and tenant isolation
-- ==============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================
-- TENANTS (ORGANIZATIONS)
-- ==============================================
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    
    -- Subscription
    plan VARCHAR(50) DEFAULT 'trial',
    status VARCHAR(50) DEFAULT 'active',
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

CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status);


-- ==============================================
-- TENANT USERS (TEAM MEMBERS)
-- ==============================================
CREATE TABLE IF NOT EXISTS tenant_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    
    role VARCHAR(50) DEFAULT 'member',
    status VARCHAR(50) DEFAULT 'active',
    
    last_login_at TIMESTAMP,
    invited_by UUID REFERENCES tenant_users(id),
    invited_at TIMESTAMP,
    
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, email)
);

CREATE INDEX IF NOT EXISTS idx_tenant_users_tenant ON tenant_users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_users_email ON tenant_users(email);


-- ==============================================
-- WHATSAPP SESSIONS (PER TENANT)
-- ==============================================
CREATE TABLE IF NOT EXISTS whatsapp_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50),
    
    status VARCHAR(50) DEFAULT 'disconnected',
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

CREATE INDEX IF NOT EXISTS idx_whatsapp_sessions_tenant ON whatsapp_sessions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_sessions_session_id ON whatsapp_sessions(session_id);


-- ==============================================
-- WORKFLOWS
-- ==============================================
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Workflow Definition (JSON)
    definition JSONB NOT NULL,
    
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'draft',
    
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

CREATE INDEX IF NOT EXISTS idx_workflows_tenant ON workflows(tenant_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);


-- ==============================================
-- WORKFLOW EXECUTIONS (RUNS)
-- ==============================================
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    conversation_id INTEGER REFERENCES conversations(id),
    
    status VARCHAR(50) DEFAULT 'running',
    
    -- Current State
    current_node_id VARCHAR(255),
    context JSONB DEFAULT '{}',
    
    -- Execution Log
    execution_log JSONB DEFAULT '[]',
    
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

CREATE INDEX IF NOT EXISTS idx_workflow_executions_tenant ON workflow_executions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_conversation ON workflow_executions(conversation_id);


-- ==============================================
-- UPDATE EXISTING TABLES WITH TENANT_ID
-- ==============================================

-- Users table - add tenant_id
ALTER TABLE users ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);

-- Conversations table - add tenant_id and workflow_id
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS workflow_id UUID REFERENCES workflows(id);
CREATE INDEX IF NOT EXISTS idx_conversations_tenant ON conversations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_conversations_workflow ON conversations(workflow_id);

-- Messages table - add tenant_id
ALTER TABLE messages ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_messages_tenant ON messages(tenant_id);

-- Agent interactions table - add tenant_id
ALTER TABLE agent_interactions ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_agent_interactions_tenant ON agent_interactions(tenant_id);

-- Orders table - add tenant_id
ALTER TABLE orders ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_orders_tenant ON orders(tenant_id);


-- ==============================================
-- USAGE TRACKING (FOR BILLING)
-- ==============================================
CREATE TABLE IF NOT EXISTS usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    metric VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, metric, period_start)
);

CREATE INDEX IF NOT EXISTS idx_usage_records_tenant ON usage_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_usage_records_period ON usage_records(period_start, period_end);


-- ==============================================
-- API KEYS (PER TENANT)
-- ==============================================
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    
    permissions TEXT[] DEFAULT '{}',
    
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    created_by UUID REFERENCES tenant_users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_api_keys_tenant ON api_keys(tenant_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);


-- ==============================================
-- WORKFLOW TEMPLATES (PRE-BUILT FLOWS)
-- ==============================================
CREATE TABLE IF NOT EXISTS workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- 'sales', 'support', 'marketing', 'e-commerce'
    
    definition JSONB NOT NULL,
    
    is_public BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    
    thumbnail_url TEXT,
    tags TEXT[] DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow_templates_category ON workflow_templates(category);


-- ==============================================
-- INSERT SAMPLE DATA
-- ==============================================

-- Create a demo tenant
INSERT INTO tenants (id, name, slug, email, plan, status, max_whatsapp_sessions, max_workflows, max_users)
VALUES (
    gen_random_uuid(),
    'Demo Company',
    'demo-company',
    'demo@example.com',
    'business',
    'active',
    2,
    20,
    10
) ON CONFLICT DO NOTHING;

-- Create sample workflow templates
INSERT INTO workflow_templates (name, description, category, definition) VALUES
(
    'Lead Qualification',
    'Qualify leads and collect contact information',
    'sales',
    '{
      "nodes": [
        {"id": "start", "type": "trigger", "subtype": "message_received"},
        {"id": "greet", "type": "action", "subtype": "send_message", "config": {"message": "Hi! What brings you here today?"}},
        {"id": "classify", "type": "logic", "subtype": "ai_classifier"}
      ],
      "edges": [
        {"source": "start", "target": "greet"},
        {"source": "greet", "target": "classify"}
      ]
    }'::jsonb
),
(
    'Customer Support',
    '24/7 automated customer support with FAQ',
    'support',
    '{
      "nodes": [
        {"id": "start", "type": "trigger", "subtype": "message_received"},
        {"id": "menu", "type": "action", "subtype": "send_buttons", "config": {"message": "How can I help?", "buttons": ["Track Order", "Returns", "Other"]}}
      ],
      "edges": [
        {"source": "start", "target": "menu"}
      ]
    }'::jsonb
),
(
    'Order Tracking',
    'Let customers check their order status',
    'e-commerce',
    '{
      "nodes": [
        {"id": "start", "type": "trigger", "subtype": "message_received"},
        {"id": "ask_order", "type": "action", "subtype": "send_message", "config": {"message": "Please provide your order number"}},
        {"id": "fetch_order", "type": "action", "subtype": "api_call"}
      ],
      "edges": [
        {"source": "start", "target": "ask_order"},
        {"source": "ask_order", "target": "fetch_order"}
      ]
    }'::jsonb
)
ON CONFLICT DO NOTHING;


-- ==============================================
-- DONE
-- ==============================================
SELECT 'Multi-tenant SaaS migration completed successfully!' as status;
