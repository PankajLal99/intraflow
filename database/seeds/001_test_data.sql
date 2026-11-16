-- Seed data for testing IntraFlow

-- Insert test tenants
INSERT INTO tenants (id, name, slug, email, plan, status, max_whatsapp_sessions, max_workflows, max_messages_per_month, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Acme Corporation', 'acme-corp', 'admin@acme.com', 'business', 'active', 2, 50, 10000, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222', 'TechStart Inc', 'techstart', 'admin@techstart.com', 'starter', 'active', 1, 10, 1000, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333', 'RetailWorld', 'retailworld', 'admin@retailworld.com', 'enterprise', 'active', 5, 100, 100000, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert test tenant users (password is "password123" hashed with bcrypt)
INSERT INTO tenant_users (id, tenant_id, email, password_hash, full_name, role, status, created_at, updated_at)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 'admin@acme.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCJZZ5iXWu', 'John Doe', 'owner', 'active', NOW(), NOW()),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222', 'admin@techstart.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCJZZ5iXWu', 'Jane Smith', 'owner', 'active', NOW(), NOW()),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '33333333-3333-3333-3333-333333333333', 'admin@retailworld.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYCJZZ5iXWu', 'Bob Johnson', 'owner', 'active', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert test WhatsApp sessions
INSERT INTO whatsapp_sessions (id, tenant_id, session_id, phone_number, status, created_at, updated_at)
VALUES
    ('88888888-8888-8888-8888-888888888888', '11111111-1111-1111-1111-111111111111', 'acme-session-1', '+1234567890', 'connected', NOW(), NOW()),
    ('99999999-9999-9999-9999-999999999999', '22222222-2222-2222-2222-222222222222', 'techstart-session-1', '+1987654321', 'connected', NOW(), NOW()),
    ('77777777-7777-7777-7777-777777777777', '33333333-3333-3333-3333-333333333333', 'retail-session-1', '+1555123456', 'connected', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert test workflows
INSERT INTO workflows (id, tenant_id, name, description, definition, version, status, is_default, created_by, created_at, updated_at)
VALUES
    (
        '44444444-4444-4444-4444-444444444444',
        '11111111-1111-1111-1111-111111111111',
        'Customer Support Bot',
        'Handles customer inquiries and support tickets',
        '{
            "nodes": [
                {
                    "id": "start",
                    "type": "trigger",
                    "data": {"label": "Start"}
                },
                {
                    "id": "welcome",
                    "type": "action",
                    "data": {
                        "label": "Send Welcome",
                        "action": "send_message",
                        "message": "Welcome to Acme Corp! How can I help you today?"
                    }
                },
                {
                    "id": "classify",
                    "type": "logic",
                    "data": {
                        "label": "Classify Intent",
                        "logic": "ai_classifier",
                        "categories": ["product_inquiry", "order_status", "support"]
                    }
                }
            ],
            "edges": [
                {"source": "start", "target": "welcome"},
                {"source": "welcome", "target": "classify"}
            ],
            "variables": {}
        }',
        1,
        'active',
        true,
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        NOW(),
        NOW()
    ),
    (
        '55555555-5555-5555-5555-555555555555',
        '22222222-2222-2222-2222-222222222222',
        'Lead Qualification',
        'Qualifies and routes sales leads',
        '{
            "nodes": [
                {
                    "id": "start",
                    "type": "trigger",
                    "data": {"label": "Start"}
                },
                {
                    "id": "greet",
                    "type": "action",
                    "data": {
                        "label": "Greet User",
                        "action": "send_message",
                        "message": "Hi! Thanks for reaching out to TechStart. What brings you here today?"
                    }
                }
            ],
            "edges": [
                {"source": "start", "target": "greet"}
            ],
            "variables": {}
        }',
        1,
        'active',
        true,
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        NOW(),
        NOW()
    ),
    (
        '66666666-6666-6666-6666-666666666666',
        '33333333-3333-3333-3333-333333333333',
        'Order Tracking Bot',
        'Helps customers track their orders',
        '{
            "nodes": [
                {
                    "id": "start",
                    "type": "trigger",
                    "data": {"label": "Start"}
                },
                {
                    "id": "ask_order",
                    "type": "action",
                    "data": {
                        "label": "Ask for Order Number",
                        "action": "send_message",
                        "message": "Please provide your order number to track your shipment."
                    }
                },
                {
                    "id": "lookup",
                    "type": "integration",
                    "data": {
                        "label": "Lookup Order",
                        "integration": "order_api",
                        "endpoint": "/orders/{{order_number}}"
                    }
                }
            ],
            "edges": [
                {"source": "start", "target": "ask_order"},
                {"source": "ask_order", "target": "lookup"}
            ],
            "variables": {
                "order_number": ""
            }
        }',
        1,
        'active',
        true,
        'cccccccc-cccc-cccc-cccc-cccccccccccc',
        NOW(),
        NOW()
    )
ON CONFLICT (id) DO NOTHING;

-- Success message
SELECT 'Seed data inserted successfully!' as status;
SELECT 
    COUNT(*) as tenant_count 
FROM tenants 
WHERE id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '33333333-3333-3333-3333-333333333333'
);
