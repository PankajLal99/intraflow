# Getting Started Guide

This guide will help you get your WhatsApp Business Agentic Workflow system up and running in **less than 15 minutes**.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Docker** and **Docker Compose** installed ([Get Docker](https://docs.docker.com/get-docker/))
- [ ] **A spare phone number** for WhatsApp (NOT your main business number)
- [ ] **An LLM API key** from one of:
  - [OpenAI](https://platform.openai.com/api-keys) - Recommended for starting ($5/month)
  - [Google AI Studio](https://makersuite.google.com/app/apikey) - Most cost-effective ($1-5/month)
  - [Anthropic](https://console.anthropic.com/) - Best quality ($5-10/month)
- [ ] **8GB RAM minimum** on your machine (16GB recommended)

## Step 1: Clone and Configure (3 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd whatsapp-agent-workflow

# Run the quick start script
./quick-start.sh
```

The script will:
1. Create your `.env` file with a secure webhook secret
2. Prompt you to add your LLM API key

**Edit `.env` and add your API key:**

```bash
nano .env  # or use your favorite editor
```

For OpenAI (recommended):
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-key-here
```

For Google Gemini (cheapest):
```env
LLM_PROVIDER=google
LLM_MODEL=gemini-1.5-flash
GOOGLE_API_KEY=your-key-here
```

Save and close the file.

## Step 2: Start Services (2 minutes)

```bash
# Start all Docker containers
docker-compose up -d

# Check that all services are running
docker-compose ps
```

You should see 8 services running:
- openwa-gateway
- webhook-handler
- agent-orchestrator
- postgres-db
- redis-cache
- prometheus
- grafana
- loki

## Step 3: Connect WhatsApp (5 minutes)

### 3.1 Open OpenWA Dashboard

Navigate to: **http://localhost:2785**

### 3.2 Create a Session

1. Click **"Create Session"**
2. Name it: `main-session`
3. Click **"Start Session"**

### 3.3 Link Your WhatsApp

You'll see a QR code. On your phone:

1. Open **WhatsApp**
2. Go to **Settings → Linked Devices**
3. Tap **"Link a Device"**
4. **Scan the QR code** on your screen

Wait for the status to change to **"Connected"** ✅

### 3.4 Generate API Key

1. In OpenWA dashboard, go to **Settings → API Keys**
2. Click **"Create API Key"**
3. **Copy the generated key** (starts with `owa_k1_...`)
4. Add it to your `.env` file:

```bash
nano .env
# Add this line:
OPENWA_API_KEY=owa_k1_your_actual_key_here
```

5. Restart the webhook handler:

```bash
docker-compose restart webhook-handler
```

## Step 4: Configure Webhook (3 minutes)

### 4.1 Get Your Webhook Secret

```bash
grep WEBHOOK_SECRET .env
# Copy the value
```

### 4.2 Create Webhook in OpenWA

In OpenWA dashboard:

1. Go to **Webhooks** tab
2. Click **"Create Webhook"**
3. Fill in:
   - **URL**: `http://webhook-handler:3000/webhook`
   - **Secret**: (paste the WEBHOOK_SECRET from above)
   - **Events**: Check ☑️ **"message"**
4. Click **"Save"**

## Step 5: Test It! (2 minutes)

### 5.1 Send a Test Message

From another WhatsApp account, send a message to the phone number you connected:

```
Hi, I'm looking for a laptop
```

### 5.2 Watch It Work

You should receive an AI-generated response within 2-3 seconds! 🎉

Example response:
```
I'd be happy to help you find a laptop! We have some great options:

- Dell XPS 13 ($1,299.99) - Ultra-portable with Intel i7
- MacBook Air M2 ($1,199.99) - Apple laptop with M2 chip

Would you like more details on any of these?
```

### 5.3 Try Different Agents

**Product Search:**
```
Show me headphones under $500
```

**Order Management:**
```
I want to check my order status
```

**Customer Support:**
```
What are your business hours?
```

## Step 6: Monitor Your System (Optional)

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f webhook-handler
docker-compose logs -f agent-orchestrator
```

### Access Grafana Dashboard

1. Open: **http://localhost:3001**
2. Login: `admin` / `admin`
3. Explore the metrics and logs

### Check Prometheus Metrics

Open: **http://localhost:9090**

Try these queries:
- `webhook_requests_total` - Total requests
- `agent_response_time_seconds` - Agent latency
- `webhook_processing_duration_seconds` - Processing time

## Common Issues & Solutions

### Issue: QR Code Not Appearing

**Solution:**
```bash
docker-compose logs openwa
# Check for errors
# Try: docker-compose restart openwa
```

### Issue: "Invalid HMAC signature" in logs

**Solution:**
- Ensure WEBHOOK_SECRET matches in both `.env` and OpenWA webhook settings
- Restart webhook-handler: `docker-compose restart webhook-handler`

### Issue: No response from agent

**Solution:**
```bash
# Check agent-orchestrator logs
docker-compose logs agent-orchestrator

# Common issues:
# 1. Invalid API key - verify in .env
# 2. Rate limit exceeded - wait or use different account
# 3. Network issues - check internet connection
```

### Issue: "Connection refused" errors

**Solution:**
```bash
# Ensure all services are running
docker-compose ps

# Restart all services
docker-compose restart
```

### Issue: High memory usage

**Solution:**
- Ensure you have at least 8GB RAM
- Adjust Docker memory limits in Docker Desktop settings
- Stop unused services: `docker-compose stop prometheus grafana loki`

## Next Steps

### 1. Customize Your Agents

Edit the agent prompts in:
- `agent-orchestrator/src/agents/product_search.py`
- `agent-orchestrator/src/agents/order_management.py`
- `agent-orchestrator/src/agents/customer_support.py`

### 2. Connect Your Business APIs

Add your product and order APIs in `.env`:
```env
PRODUCT_API_URL=https://api.yourcompany.com/products
PRODUCT_API_KEY=your-api-key
```

Then implement the API calls in:
- `agent-orchestrator/src/tools/product_api.py`
- `agent-orchestrator/src/tools/order_api.py`

### 3. Add More Agents

Create new agents in `agent-orchestrator/src/agents/` directory.

Example: `shipping_agent.py`, `returns_agent.py`, etc.

### 4. Set Up Production Monitoring

1. Create Grafana dashboards for your metrics
2. Set up alerts for errors and downtime
3. Configure log retention policies

### 5. Deploy to EC2

See [ARCHITECTURE.md](ARCHITECTURE.md) for EC2 deployment guide.

Key steps:
1. Launch t3.large EC2 instance
2. Install Docker and Docker Compose
3. Clone repo and configure `.env`
4. Update security groups (ports 22, 2785, 3001)
5. Run `docker-compose up -d`

## Important Reminders

### ⚠️ WhatsApp Ban Risk

OpenWA uses reverse-engineered protocol. To minimize risk:
- Use a separate phone number (not your main business line)
- Don't send more than 100 messages/hour
- Add natural delays (we do this automatically)
- Have backup numbers ready
- Monitor for warnings from WhatsApp

### 🔒 Security Best Practices

- [ ] Change default database password in `.env`
- [ ] Use strong WEBHOOK_SECRET (auto-generated)
- [ ] Keep API keys secure (never commit to git)
- [ ] Use HTTPS in production
- [ ] Implement rate limiting for your endpoints
- [ ] Regularly update dependencies

### 💰 Cost Management

For 10,000 messages/month:
- **OpenAI GPT-4o-mini**: $5-15
- **Google Gemini Flash**: $1-5
- **Anthropic Claude Haiku**: $5-10

Tips to reduce costs:
- Use smaller models (gpt-4o-mini, gemini-flash)
- Implement response caching
- Reduce max_tokens (currently 500)
- Use Ollama for development (free, local)

## Getting Help

### Check Documentation

- **[RESEARCH.md](RESEARCH.md)** - All research on technologies
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[README.md](README.md)** - Main documentation

### Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart webhook-handler

# Check service status
docker-compose ps

# Rebuild after code changes
docker-compose up -d --build

# Access a service shell
docker-compose exec agent-orchestrator bash
```

### Still Stuck?

1. Check logs: `docker-compose logs -f`
2. Verify all environment variables in `.env`
3. Ensure all services are running: `docker-compose ps`
4. Check [ARCHITECTURE.md](ARCHITECTURE.md) for detailed troubleshooting

---

**Congratulations! 🎉** You now have a working WhatsApp Business AI agent system!

Start experimenting with different prompts, customize your agents, and integrate your business APIs.

For production deployment and scaling, refer to [ARCHITECTURE.md](ARCHITECTURE.md).
