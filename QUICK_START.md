# IntraFlow Quick Start Guide

Get IntraFlow up and running in minutes!

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Git

## 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/PankajLal99/intraflow.git
cd intraflow

# Copy environment template
cp .env.example .env

# Generate secure secrets (or edit .env manually)
# Update these values in .env:
# - JWT_SECRET (random 32+ character string)
# - WEBHOOK_SECRET (random 32+ character string)
# - OPENAI_API_KEY (your OpenAI API key)
```

## 2. Start the Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

Expected services:
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ Agent Orchestrator API (port 8000)
- ✅ OpenWA (port 2785)
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3001)

## 3. Initialize Database

```bash
# Run database migrations
docker exec -i intraflow-postgres-1 psql -U whatsapp -d whatsapp < database/init.sql
docker exec -i intraflow-postgres-1 psql -U whatsapp -d whatsapp < database/migrations/002_multi_tenant_workflows.sql

# Seed test data (optional)
docker exec -i intraflow-postgres-1 psql -U whatsapp -d whatsapp < database/seeds/001_test_data.sql

# Verify tables
docker exec intraflow-postgres-1 psql -U whatsapp -d whatsapp -c "\dt"
```

## 4. Start Frontend (Development)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

## 5. Validate Deployment

```bash
# Run automated validation
./scripts/validate-deployment.sh

# Run end-to-end tests
./scripts/e2e-test.sh
```

## 6. Access the Application

### Frontend
- Landing Page: http://localhost:3000
- Sign Up: http://localhost:3000/signup
- Login: http://localhost:3000/login
- Dashboard: http://localhost:3000/dashboard

### Backend API
- API Root: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

### Monitoring
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

### OpenWA Dashboard
- URL: http://localhost:2785
- Scan QR code to connect WhatsApp

## 7. Create Your First Workflow

1. **Sign Up**: Go to http://localhost:3000/signup
   - Email: your-email@example.com
   - Password: SecurePassword123!
   - Tenant Name: Your Company

2. **Login**: Use your credentials to log in

3. **Navigate to Workflows**: Click "Workflows" in the sidebar

4. **Create Workflow**: Click "Create Workflow"
   - Add nodes from the left panel
   - Configure each node's properties
   - Connect nodes in sequence
   - Save your workflow

5. **Test Workflow**: Send a WhatsApp message to your connected number

## Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs -f agent-orchestrator

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose up -d --build
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker exec intraflow-postgres-1 psql -U whatsapp -d whatsapp -c "SELECT 1"

# View database logs
docker-compose logs postgres
```

### API Not Responding
```bash
# Check health endpoint
curl http://localhost:8000/health

# Check container status
docker-compose ps agent-orchestrator

# View API logs
docker-compose logs -f agent-orchestrator
```

### Frontend Build Issues
```bash
cd frontend

# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000
```

## Next Steps

1. **Configure LLM Provider**: Add your API keys to `.env`
   - `OPENAI_API_KEY` for OpenAI
   - `ANTHROPIC_API_KEY` for Anthropic
   - `GOOGLE_API_KEY` for Google

2. **Connect WhatsApp**: Open http://localhost:2785 and scan QR code

3. **Create Workflows**: Build your automation workflows in the visual builder

4. **Monitor Performance**: Check Prometheus/Grafana dashboards

5. **Deploy to Production**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Support

- Documentation: See `docs/` directory
- Issues: https://github.com/PankajLal99/intraflow/issues
- Architecture: See [ARCHITECTURE.md](ARCHITECTURE.md)

## Production Deployment

For production deployment on AWS/GCP/Azure, see:
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md)
- [SECURITY.md](docs/SECURITY.md)
