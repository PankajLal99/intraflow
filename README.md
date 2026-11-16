# IntraFlow

> **Automate Your Internal Communications with AI**

A comprehensive, multi-tenant SaaS platform for WhatsApp Business automation with visual workflow builder, AI-powered agents, and enterprise-grade monitoring. Built with OpenWA, LangChain, LangGraph, and modern observability tools.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

## 🎯 Project Overview

This system enables businesses to automate WhatsApp customer interactions using intelligent AI agents that can:
- Search products and provide recommendations
- Manage orders (create, track, cancel)
- Provide customer support and answer FAQs
- Call external APIs for real-time data
- Log all interactions and provide analytics

## 📋 Features

### Core Features
- ✅ **WhatsApp Integration** via OpenWA (reverse-engineered WhatsApp Web API)
- ✅ **Multi-Agent System** using LangGraph for intelligent routing
- ✅ **LLM Support** - OpenAI, Anthropic Claude, Google Gemini, or local Ollama
- ✅ **Webhook Handler** with HMAC signature verification
- ✅ **Message Queue** using Redis and Bull for reliable processing
- ✅ **PostgreSQL Database** for conversation history and analytics
- ✅ **Monitoring Stack** - Prometheus, Grafana, and Loki
- ✅ **Docker Compose** deployment for easy setup

### Specialized Agents
1. **Product Search Agent** - Handles product queries and recommendations
2. **Order Management Agent** - Creates/tracks orders
3. **Customer Support Agent** - Handles FAQs and escalations

## 🏗️ Architecture

```
WhatsApp User
      ↓
OpenWA Gateway (WhatsApp API)
      ↓
Webhook Handler (Node.js)
      ↓
Message Queue (Redis + Bull)
      ↓
Agent Orchestrator (Python + LangGraph)
      ↓
Specialized Agents (LangChain)
      ↓
[PostgreSQL + Redis + External APIs]
      ↓
Monitoring (Prometheus + Grafana + Loki)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## 📚 Documentation

- **[RESEARCH.md](RESEARCH.md)** - Comprehensive research on WhatsApp APIs, OpenWA, OpenBot, and agentic frameworks
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture, data flows, and component specifications
- **[.env.example](.env.example)** - Environment configuration template

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- A spare phone number for WhatsApp (not your main business number)
- LLM API key (OpenAI, Anthropic, or Google)
- 8GB RAM minimum (16GB recommended)
- Linux or macOS (Windows with WSL2)

### Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd whatsapp-agent-workflow
```

2. **Configure environment variables**

```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

Required variables:
- `WEBHOOK_SECRET` - Generate with `openssl rand -hex 32`
- `OPENAI_API_KEY` - Your OpenAI API key (or other LLM provider)
- `OPENWA_API_KEY` - Will be generated in OpenWA dashboard after first start

3. **Start all services**

```bash
docker-compose up -d
```

This will start:
- OpenWA Gateway (port 2785)
- Webhook Handler (port 3000)
- Agent Orchestrator (port 8000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Prometheus (port 9090)
- Grafana (port 3001)
- Loki (port 3100)

4. **Setup WhatsApp Connection**

Open the OpenWA dashboard:

```
http://localhost:2785
```

- Create a new session (e.g., "main-session")
- Scan the QR code with your WhatsApp phone
- Wait for "Connected" status

5. **Generate API Key**

In OpenWA dashboard:
- Go to Settings → API Keys
- Create a new API key
- Copy it to your `.env` file as `OPENWA_API_KEY`
- Restart webhook-handler: `docker-compose restart webhook-handler`

6. **Configure Webhook**

In OpenWA dashboard:
- Go to Webhooks
- Create new webhook:
  - URL: `http://webhook-handler:3000/webhook`
  - Secret: (same as `WEBHOOK_SECRET` in `.env`)
  - Events: Select "message" events

7. **Test the System**

Send a WhatsApp message to your connected number:

```
"Hi, I'm looking for a laptop"
```

You should receive an AI-generated response!

## 🔍 Monitoring & Observability

### Grafana Dashboard

Access at: `http://localhost:3001`
- Username: `admin`
- Password: (from `GRAFANA_PASSWORD` in `.env`, default: `admin`)

**Available Dashboards:**
- System Health (CPU, memory, request rates)
- Business Metrics (users, conversations, conversions)
- Agent Performance (response times, token usage)

### Prometheus Metrics

Access at: `http://localhost:9090`

**Key Metrics:**
- `webhook_requests_total` - Total webhook requests
- `agent_requests_total` - Agent requests by type
- `agent_response_time_seconds` - Agent latency
- `webhook_processing_duration_seconds` - Processing time

### Logs (Loki)

Logs are automatically collected from all Docker containers and sent to Loki. View them in Grafana:

1. Go to Explore
2. Select Loki datasource
3. Query: `{container="webhook-handler"}`

## 🛠️ Development

### Local Development (without Docker)

**Webhook Handler:**

```bash
cd webhook-handler
npm install
cp ../.env .env
npm run dev
```

**Agent Orchestrator:**

```bash
cd agent-orchestrator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env .env
uvicorn src.main:app --reload
```

### Running Tests

```bash
# Webhook handler tests
cd webhook-handler
npm test

# Agent orchestrator tests
cd agent-orchestrator
pytest
```

## 📊 Database Schema

The PostgreSQL database includes:
- `users` - WhatsApp users
- `conversations` - Conversation sessions
- `messages` - All messages (inbound/outbound)
- `agent_interactions` - Agent performance logs
- `orders` - Sample business logic (orders)
- `products` - Sample product catalog

See [database/init.sql](database/init.sql) for full schema.

## 🔧 Configuration

### LLM Providers

**OpenAI (Recommended for starting):**
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
```

**Anthropic Claude:**
```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-haiku-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

**Google Gemini (Most cost-effective):**
```env
LLM_PROVIDER=google
LLM_MODEL=gemini-1.5-flash
GOOGLE_API_KEY=...
```

### External APIs

Configure your business APIs in `.env`:

```env
PRODUCT_API_URL=https://api.yourcompany.com/products
PRODUCT_API_KEY=your-api-key
ORDER_API_URL=https://api.yourcompany.com/orders
ORDER_API_KEY=your-api-key
```

Then implement API calls in:
- `agent-orchestrator/src/tools/product_api.py`
- `agent-orchestrator/src/tools/order_api.py`

## 🚨 Important Security Considerations

### WhatsApp Ban Risk

⚠️ **IMPORTANT:** OpenWA uses a reverse-engineered WhatsApp Web protocol, which violates WhatsApp's Terms of Service.

**Mitigation strategies:**
1. Use a separate phone number (not your main business line)
2. Limit message frequency (< 100 messages/hour)
3. Add delays to mimic human behavior
4. Have backup numbers ready
5. Monitor for warning signs

**For production:** Consider migrating to Meta's official WhatsApp Business API via [OpenBSP](https://openbsp.dev/) after validating ROI.

### Data Security

- All webhook payloads are HMAC-verified
- API keys stored as environment variables
- Database credentials should be changed from defaults
- Use HTTPS in production
- Implement rate limiting

## 💰 Cost Estimates

### EC2 Deployment (Monthly)

| Component | Size | Cost |
|-----------|------|------|
| EC2 t3.large | 2 vCPU, 8GB RAM | $60 |
| EBS Storage | 100GB | $10 |
| **LLM API (10k messages)** | | |
| OpenAI GPT-4o-mini | ~50k tokens | $5-15 |
| Google Gemini Flash | ~50k tokens | $1-5 |
| **Total** | | **$70-85/month** |

See [RESEARCH.md](RESEARCH.md) for detailed cost analysis.

## 🔄 Scaling

### Vertical Scaling (< 1000 users)
- Upgrade EC2 instance (t3.large → t3.xlarge)
- Increase PostgreSQL resources

### Horizontal Scaling (1000-10000 users)
- Multiple webhook-handler instances (load balanced)
- Separate database server
- Redis cluster

### Cloud-Native (10000+ users)
- Kubernetes (EKS/GKE)
- Managed services (RDS, ElastiCache)
- Multi-region deployment

See [ARCHITECTURE.md](ARCHITECTURE.md) for scaling strategies.

## 🐛 Troubleshooting

### OpenWA not connecting
- Check QR code expiration (refresh every 60 seconds)
- Ensure phone has internet connection
- Try pairing code method instead

### Webhook not receiving messages
- Verify webhook URL in OpenWA dashboard
- Check HMAC secret matches in both places
- Look at webhook-handler logs: `docker-compose logs webhook-handler`

### Agent not responding
- Check LLM API key is valid
- Verify agent-orchestrator is running: `docker-compose ps`
- Check logs: `docker-compose logs agent-orchestrator`
- Ensure LLM provider quota is not exceeded

### High LLM costs
- Switch to smaller model (gpt-4o-mini or gemini-flash)
- Implement response caching
- Reduce max_tokens setting
- Use local Ollama for development

## 📖 Additional Resources

- [OpenWA Documentation](https://docs.open-wa.org/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

This is a research and exploration project. Feel free to:
- Fork and customize for your business needs
- Add new agents for specific use cases
- Improve monitoring and observability
- Add tests and documentation

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This project uses reverse-engineered WhatsApp Web protocol via OpenWA, which is not affiliated with or endorsed by WhatsApp or Meta. Use at your own risk. For production deployments, consider using Meta's official WhatsApp Business API.

---

**Built with ❤️ for exploring agentic workflows on WhatsApp**

For questions or issues, please open a GitHub issue.
