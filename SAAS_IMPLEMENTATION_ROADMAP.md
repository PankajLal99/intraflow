# SaaS Implementation Roadmap

## Overview

This document provides a step-by-step roadmap for converting the WhatsApp Agent system into a **multi-tenant SaaS platform** with visual workflow builder.

## Current Status ✅

You now have:
- ✅ Complete research and architecture documentation
- ✅ Working single-tenant WhatsApp automation
- ✅ Agent orchestration system
- ✅ Multi-tenant database schema
- ✅ Workflow execution engine
- ✅ Workflow builder implementation guide

## What's Next: 8-Week Implementation Plan

---

## Phase 1: Multi-Tenancy Foundation (Weeks 1-2)

### Week 1: Database & Authentication

**Tasks:**
1. **Run database migration** for multi-tenancy
   ```bash
   cd database/migrations
   psql $DATABASE_URL -f 002_multi_tenant_workflows.sql
   ```

2. **Implement JWT authentication**
   - Create `/api/v1/auth/signup` endpoint
   - Create `/api/v1/auth/login` endpoint
   - Create `/api/v1/auth/refresh` endpoint
   - Add JWT middleware for tenant scoping

3. **Update existing APIs** to include `tenant_id`
   - Modify webhook handler to extract tenant from session
   - Update agent orchestrator to use tenant-scoped queries
   - Add tenant_id to all database operations

**Files to create:**
```
agent-orchestrator/src/
├── auth/
│   ├── jwt.py              # JWT token generation/validation
│   ├── password.py         # Password hashing
│   └── middleware.py       # Auth middleware
├── models/
│   ├── tenant.py           # Tenant model
│   └── tenant_user.py      # TenantUser model
└── api/
    └── auth_routes.py      # Auth endpoints
```

**Deliverable:** Users can sign up, log in, and access tenant-scoped data

### Week 2: WhatsApp Session Management

**Tasks:**
1. **Multi-session support in OpenWA**
   - Each tenant gets their own session ID
   - Update webhook handler to route by tenant

2. **Session management API**
   - Create `/api/v1/sessions` endpoints
   - QR code generation per session
   - Session status monitoring

3. **Update webhook routing**
   - Map WhatsApp session → tenant
   - Route messages to correct tenant's workflows

**Files to create:**
```
agent-orchestrator/src/
├── services/
│   ├── session_service.py    # WhatsApp session management
│   └── openwa_client.py      # OpenWA API client
└── api/
    └── session_routes.py      # Session endpoints
```

**Deliverable:** Each tenant can connect their own WhatsApp number

---

## Phase 2: Workflow System (Weeks 3-4)

### Week 3: Backend Workflow Engine

**Tasks:**
1. **Integrate workflow executor** into agent orchestrator
   - Replace hard-coded agents with workflow execution
   - Add workflow loading from database
   - Implement state persistence

2. **Workflow API endpoints**
   - CRUD operations for workflows
   - Workflow publishing
   - Version control

3. **Testing infrastructure**
   - Test mode execution
   - Execution logging
   - Error handling

**Files to update/create:**
```
agent-orchestrator/src/
├── workflow/
│   ├── __init__.py           # ✅ Already created
│   ├── executor.py           # ✅ Already created
│   ├── validators.py         # NEW: Validate workflow definitions
│   └── test_executor.py      # NEW: Test utilities
├── services/
│   └── workflow_service.py   # NEW: Workflow CRUD operations
└── api/
    └── workflow_routes.py    # NEW: Workflow API endpoints
```

**Deliverable:** Workflows can be created, saved, and executed via API

### Week 4: Workflow Templates

**Tasks:**
1. **Pre-built templates**
   - Lead qualification
   - Customer support
   - Order tracking
   - Appointment booking

2. **Template marketplace**
   - Browse templates
   - Clone template to tenant
   - Customize cloned workflow

3. **Documentation**
   - Node type reference
   - Example workflows
   - Best practices guide

**Deliverable:** Users can start from templates instead of scratch

---

## Phase 3: Frontend Development (Weeks 5-6)

### Week 5: Visual Workflow Builder

**Tasks:**
1. **Set up React app**
   ```bash
   cd workflow-builder/frontend
   npm create vite@latest . -- --template react-ts
   npm install reactflow zustand axios react-hook-form
   ```

2. **Implement core components**
   - Canvas with React Flow
   - Node palette (drag-and-drop)
   - Properties panel
   - Toolbar (save, test, publish)

3. **Custom node components**
   - Send Message node
   - Condition node
   - AI Classifier node
   - Button/List nodes

**Files to create:**
```
workflow-builder/frontend/src/
├── App.tsx
├── components/
│   └── WorkflowBuilder/
│       ├── Canvas.tsx
│       ├── NodePalette.tsx
│       ├── PropertiesPanel.tsx
│       ├── Toolbar.tsx
│       └── nodes/
│           ├── SendMessageNode.tsx
│           ├── ConditionNode.tsx
│           └── AIClassifierNode.tsx
├── stores/
│   └── workflowStore.ts
├── api/
│   └── workflows.ts
└── types/
    └── workflow.ts
```

**Deliverable:** Users can visually build workflows in browser

### Week 6: Testing & Dashboard

**Tasks:**
1. **Test simulator**
   - Chat UI for testing workflows
   - Execution log viewer
   - Variable inspector

2. **Tenant dashboard**
   - Workflow list
   - Analytics overview
   - WhatsApp session status
   - Usage metrics

3. **Settings pages**
   - Team management
   - API keys
   - Billing (UI only for now)

**Deliverable:** Complete UI for managing workflows and sessions

---

## Phase 4: Production Ready (Weeks 7-8)

### Week 7: Billing & Limits

**Tasks:**
1. **Stripe integration**
   - Subscription plans (Starter, Business, Enterprise)
   - Payment methods
   - Invoicing

2. **Usage tracking**
   - Message counting
   - Workflow execution tracking
   - Quota enforcement

3. **Limit enforcement**
   - Max workflows per plan
   - Max messages per month
   - Max team members

**Files to create:**
```
agent-orchestrator/src/
├── billing/
│   ├── stripe_client.py      # Stripe API
│   ├── subscription.py       # Subscription management
│   └── usage_tracker.py      # Track usage
└── api/
    └── billing_routes.py      # Billing endpoints
```

**Deliverable:** Paid subscription system with usage limits

### Week 8: Deployment & Launch

**Tasks:**
1. **Production deployment**
   - Set up AWS/GCP infrastructure
   - Docker images for all services
   - CI/CD pipeline
   - Database backups

2. **Monitoring & Alerts**
   - Error tracking (Sentry)
   - Uptime monitoring
   - Performance dashboards
   - Slack alerts

3. **Documentation**
   - User onboarding guide
   - Video tutorials
   - API documentation
   - Help center

4. **Beta launch**
   - Invite first 10 customers
   - Collect feedback
   - Fix critical issues

**Deliverable:** Production-ready SaaS platform with paying customers

---

## Technical Architecture Evolution

### Before (Single Tenant)
```
User WhatsApp → OpenWA → Webhook → Agent → LLM → Response
```

### After (Multi-Tenant SaaS)
```
Tenant 1 WhatsApp → OpenWA Session 1 ┐
Tenant 2 WhatsApp → OpenWA Session 2 ├→ Webhook Handler
Tenant 3 WhatsApp → OpenWA Session 3 ┘       ↓
                                    (Extract tenant_id)
                                             ↓
                                    Workflow Executor
                                    (Load tenant workflow)
                                             ↓
                                    Execute Nodes
                                    (Tenant-scoped DB queries)
                                             ↓
                                    Response to User
```

---

## Key Implementation Points

### 1. Tenant Isolation

**Every database query must include tenant_id:**

```python
# BAD - Not tenant-scoped
conversations = await db.query("SELECT * FROM conversations")

# GOOD - Tenant-scoped
conversations = await db.query(
    "SELECT * FROM conversations WHERE tenant_id = ?",
    tenant_id
)
```

**Use middleware to enforce:**

```python
@app.middleware("http")
async def enforce_tenant_scope(request: Request, call_next):
    tenant_id = extract_tenant_from_jwt(request)
    request.state.tenant_id = tenant_id
    return await call_next(request)
```

### 2. Session Mapping

**Map WhatsApp sessions to tenants:**

```python
# Store mapping: session_id → tenant_id
SESSION_TENANT_MAP = {
    "session_acme": "tenant_acme_uuid",
    "session_techco": "tenant_techco_uuid"
}

# In webhook handler:
def handle_webhook(session_id, message):
    tenant_id = SESSION_TENANT_MAP[session_id]
    # Route to tenant's workflow
```

### 3. Workflow Execution

**Replace hard-coded agents with workflow engine:**

```python
# OLD: Hard-coded agent
if intent == "product_search":
    response = product_search_agent.process(message)

# NEW: Workflow-based
workflow = await load_active_workflow(tenant_id, conversation_id)
executor = WorkflowExecutor(workflow, conversation_id, tenant_id)
response = await executor.execute(message)
```

---

## Testing Strategy

### Unit Tests
- Workflow executor node execution
- Tenant isolation (verify no cross-tenant data leaks)
- JWT token generation/validation
- Stripe webhook handling

### Integration Tests
- End-to-end message flow
- Workflow creation → execution → response
- Multi-tenant session isolation
- Billing and quota enforcement

### Load Tests
- 100+ concurrent tenants
- 10,000 messages/minute
- Database query performance
- OpenWA session stability

---

## Security Checklist

- [ ] All API endpoints require authentication
- [ ] JWT tokens expire after 24 hours
- [ ] Passwords hashed with bcrypt (min 12 rounds)
- [ ] Tenant_id extracted from JWT, never from request body
- [ ] Row-level security enforced in PostgreSQL
- [ ] API rate limiting (100 requests/minute per tenant)
- [ ] CORS configured properly
- [ ] All secrets in environment variables
- [ ] Database backups automated
- [ ] Audit logging for sensitive operations

---

## Pricing Strategy

### Freemium Model

**Free Tier** (Limited)
- 1 WhatsApp number
- 3 workflows
- 100 messages/month
- Community support

**Starter** ($29/month)
- 1 WhatsApp number
- 10 workflows
- 1,000 messages/month
- 3 team members
- Email support

**Business** ($99/month)
- 2 WhatsApp numbers
- 50 workflows
- 10,000 messages/month
- 10 team members
- Priority support
- API access

**Enterprise** ($299/month)
- 5 WhatsApp numbers
- Unlimited workflows
- 100,000 messages/month
- Unlimited team members
- Dedicated support
- Custom integrations
- SLA

---

## Success Metrics

### Technical Metrics
- 99.9% uptime
- < 2s average response time
- < 1% error rate
- < 5 minutes to onboard new tenant

### Business Metrics
- 100 tenants by month 3
- $5,000 MRR by month 6
- < 10% churn rate
- > 80% workflow completion rate

---

## Resources Needed

### Team
- 1 Full-stack developer (React + Python)
- 1 Backend developer (Python + PostgreSQL)
- 1 DevOps engineer (AWS/Docker)
- 1 Designer (UI/UX)

### Budget (Monthly)
- Infrastructure: $500-1000
- Tools (Sentry, monitoring): $200
- Email service: $50
- SMS verification: $100
- **Total**: ~$1,000/month

---

## Next Immediate Steps

**This Week:**
1. Run the multi-tenant database migration
2. Implement JWT authentication
3. Test tenant isolation

**Next Week:**
1. Set up React app for workflow builder
2. Implement first 3 node types
3. Build test simulator

**This Month:**
1. Complete workflow builder UI
2. Deploy to staging environment
3. Invite 5 beta users

---

## Questions to Answer

Before starting implementation:

1. **Hosting**: AWS, GCP, or DigitalOcean?
2. **Domain**: What's the product name and domain?
3. **Payment**: Stripe or other payment processor?
4. **Support**: Email, chat, or ticketing system?
5. **Marketing**: How will you acquire first customers?

---

## Summary

You have a **solid foundation** to build a multi-tenant WhatsApp SaaS platform:

✅ Architecture designed  
✅ Database schema ready  
✅ Workflow engine built  
✅ Implementation guide created  

**Estimated timeline**: 8-10 weeks to MVP  
**Estimated cost**: $1,000-2,000/month  
**Target**: 100 paying customers in 6 months  

Ready to start building!

---

**Document Version**: 1.0  
**Last Updated**: November 16, 2026
