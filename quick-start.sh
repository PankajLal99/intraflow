#!/bin/bash

set -e

echo "=========================================="
echo "WhatsApp Business Agentic Workflow Setup"
echo "=========================================="
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    WEBHOOK_SECRET=$(openssl rand -hex 32)
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/change-this-to-a-random-secret-string/$WEBHOOK_SECRET/" .env
    else
        sed -i "s/change-this-to-a-random-secret-string/$WEBHOOK_SECRET/" .env
    fi
    
    echo "✅ .env file created with random webhook secret"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your LLM API key!"
    echo "   - For OpenAI: Add OPENAI_API_KEY"
    echo "   - For Anthropic: Add ANTHROPIC_API_KEY"
    echo "   - For Google: Add GOOGLE_API_KEY"
    echo ""
    read -p "Press Enter after you've added your API key..."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ All services are starting!"
echo ""
echo "=========================================="
echo "📋 Next Steps:"
echo "=========================================="
echo ""
echo "1. Open OpenWA Dashboard: http://localhost:2785"
echo "   - Create a session named 'main-session'"
echo "   - Scan the QR code with WhatsApp"
echo ""
echo "2. Generate API Key in OpenWA:"
echo "   - Go to Settings → API Keys"
echo "   - Create new key and copy it"
echo "   - Add to .env as OPENWA_API_KEY"
echo "   - Run: docker-compose restart webhook-handler"
echo ""
echo "3. Configure Webhook in OpenWA:"
echo "   - Go to Webhooks → Create new"
echo "   - URL: http://webhook-handler:3000/webhook"
echo "   - Secret: (copy from .env WEBHOOK_SECRET)"
echo "   - Enable 'message' events"
echo ""
echo "4. Test by sending WhatsApp message:"
echo "   'Hi, I need help finding a laptop'"
echo ""
echo "=========================================="
echo "📊 Service URLs:"
echo "=========================================="
echo ""
echo "OpenWA Dashboard:    http://localhost:2785"
echo "Webhook Handler:     http://localhost:3000"
echo "Agent Orchestrator:  http://localhost:8000"
echo "Grafana:            http://localhost:3001 (admin/admin)"
echo "Prometheus:         http://localhost:9090"
echo ""
echo "=========================================="
echo "📚 Documentation:"
echo "=========================================="
echo ""
echo "Research:       cat RESEARCH.md"
echo "Architecture:   cat ARCHITECTURE.md"
echo "Logs:          docker-compose logs -f"
echo ""
echo "=========================================="
echo "To stop all services: docker-compose down"
echo "=========================================="
