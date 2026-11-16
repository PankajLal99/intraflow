-- ==============================================
-- WhatsApp Business Agentic Workflow Database Schema
-- ==============================================

-- Create database for OpenWA
CREATE DATABASE IF NOT EXISTS openwa;

-- Use the main whatsapp database
\c whatsapp;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- Users Table
-- ==============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    whatsapp_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50),
    name VARCHAR(255),
    email VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP,
    is_blocked BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_users_whatsapp_id ON users(whatsapp_id);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_last_active ON users(last_active_at);

-- ==============================================
-- Conversations Table
-- ==============================================
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'abandoned', 'escalated'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    agent_types_used TEXT[] DEFAULT '{}',
    outcome VARCHAR(100), -- 'resolved', 'converted', 'escalated', 'abandoned'
    satisfaction_score INTEGER, -- 1-5 rating
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_started_at ON conversations(started_at);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);

-- ==============================================
-- Messages Table
-- ==============================================
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    direction VARCHAR(20) NOT NULL, -- 'inbound' or 'outbound'
    content TEXT,
    message_type VARCHAR(50) DEFAULT 'text', -- 'text', 'image', 'audio', 'video', 'document'
    media_url TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_message_id ON messages(message_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_direction ON messages(direction);

-- ==============================================
-- Agent Interactions Table
-- ==============================================
CREATE TABLE IF NOT EXISTS agent_interactions (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL, -- 'product_search', 'order_management', 'customer_support'
    intent VARCHAR(255),
    confidence DECIMAL(5,2),
    user_message TEXT,
    agent_response TEXT,
    tools_used JSONB DEFAULT '[]',
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    llm_tokens_used INTEGER,
    llm_cost DECIMAL(10,6),
    response_time_ms INTEGER,
    was_successful BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_agent_interactions_conversation_id ON agent_interactions(conversation_id);
CREATE INDEX idx_agent_interactions_agent_type ON agent_interactions(agent_type);
CREATE INDEX idx_agent_interactions_intent ON agent_interactions(intent);
CREATE INDEX idx_agent_interactions_timestamp ON agent_interactions(timestamp);

-- ==============================================
-- Orders Table (Example Business Logic)
-- ==============================================
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    conversation_id INTEGER REFERENCES conversations(id),
    order_number VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    items JSONB NOT NULL,
    shipping_address JSONB,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ==============================================
-- Products Table (Example - for demo purposes)
-- ==============================================
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    stock_quantity INTEGER DEFAULT 0,
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_is_active ON products(is_active);

-- Insert some sample products
INSERT INTO products (sku, name, description, category, price, stock_quantity, image_url) VALUES
('LAPTOP-001', 'Dell XPS 13', 'Ultra-portable laptop with Intel i7 processor and 16GB RAM', 'Electronics', 1299.99, 50, 'https://example.com/dell-xps-13.jpg'),
('LAPTOP-002', 'MacBook Air M2', 'Apple MacBook Air with M2 chip and 8GB RAM', 'Electronics', 1199.99, 30, 'https://example.com/macbook-air.jpg'),
('PHONE-001', 'iPhone 15 Pro', 'Latest iPhone with A17 Pro chip and 256GB storage', 'Electronics', 999.99, 100, 'https://example.com/iphone-15.jpg'),
('PHONE-002', 'Samsung Galaxy S24', 'Android flagship with 12GB RAM and 256GB storage', 'Electronics', 899.99, 75, 'https://example.com/galaxy-s24.jpg'),
('HEADPHONE-001', 'Sony WH-1000XM5', 'Premium noise-cancelling headphones', 'Audio', 399.99, 200, 'https://example.com/sony-wh1000xm5.jpg')
ON CONFLICT (sku) DO NOTHING;

-- ==============================================
-- System Logs Table
-- ==============================================
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    log_level VARCHAR(20) NOT NULL, -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    service VARCHAR(100), -- 'webhook-handler', 'agent-orchestrator', 'openwa'
    message TEXT NOT NULL,
    stack_trace TEXT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE SET NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_system_logs_log_level ON system_logs(log_level);
CREATE INDEX idx_system_logs_service ON system_logs(service);
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);

-- ==============================================
-- Analytics View - Daily Metrics
-- ==============================================
CREATE OR REPLACE VIEW daily_metrics AS
SELECT
    DATE(c.started_at) as date,
    COUNT(DISTINCT c.user_id) as unique_users,
    COUNT(c.id) as total_conversations,
    SUM(c.message_count) as total_messages,
    AVG(c.message_count) as avg_messages_per_conversation,
    COUNT(CASE WHEN c.status = 'completed' THEN 1 END) as completed_conversations,
    COUNT(CASE WHEN c.outcome = 'resolved' THEN 1 END) as resolved_conversations,
    COUNT(CASE WHEN c.outcome = 'escalated' THEN 1 END) as escalated_conversations,
    AVG(c.satisfaction_score) as avg_satisfaction_score
FROM conversations c
GROUP BY DATE(c.started_at)
ORDER BY date DESC;

-- ==============================================
-- Analytics View - Agent Performance
-- ==============================================
CREATE OR REPLACE VIEW agent_performance AS
SELECT
    ai.agent_type,
    ai.intent,
    COUNT(*) as total_requests,
    AVG(ai.confidence) as avg_confidence,
    AVG(ai.response_time_ms) as avg_response_time_ms,
    SUM(ai.llm_tokens_used) as total_tokens_used,
    SUM(ai.llm_cost) as total_cost,
    COUNT(CASE WHEN ai.was_successful = TRUE THEN 1 END) as successful_requests,
    COUNT(CASE WHEN ai.was_successful = FALSE THEN 1 END) as failed_requests,
    DATE(ai.timestamp) as date
FROM agent_interactions ai
GROUP BY ai.agent_type, ai.intent, DATE(ai.timestamp)
ORDER BY date DESC, total_requests DESC;

-- ==============================================
-- Function: Update updated_at timestamp
-- ==============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for auto-updating updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- Grant Permissions
-- ==============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO whatsapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO whatsapp;

-- ==============================================
-- Done!
-- ==============================================
SELECT 'Database schema initialized successfully!' as status;
