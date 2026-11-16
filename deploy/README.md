# IntraFlow Deployment Files

This directory contains all deployment scripts and documentation for IntraFlow.

## 📁 Contents

- **deploy.sh** - Automated deployment script for production
- **AWS_DEPLOYMENT.md** - Complete AWS/Azure deployment guide with external PostgreSQL
- **QUICK_DEPLOY.md** - Quick 15-minute deployment guide

## 🚀 Quick Start

### Option 1: Manual Deployment (Recommended for first time)

```bash
# Follow the step-by-step guide
cat deploy/QUICK_DEPLOY.md
```

### Option 2: Automated Deployment Script

```bash
# Run deployment script (after initial setup)
./deploy/deploy.sh production
```

## 📚 Documentation

| File | Purpose | When to Use |
|------|---------|-------------|
| **QUICK_DEPLOY.md** | 15-minute quick start | First deployment |
| **AWS_DEPLOYMENT.md** | Complete deployment guide | Full production setup |
| **deploy.sh** | Automated deployment script | Updates and redeployments |

## 🎯 Deployment Scenarios

### Scenario 1: AWS EC2 with External RDS PostgreSQL

```bash
# 1. Launch EC2 instance (t3.medium, Ubuntu 22.04)
# 2. Create RDS PostgreSQL instance (or use existing)
# 3. Follow QUICK_DEPLOY.md
# 4. Configure .env with RDS credentials
# 5. Run: docker-compose up -d
```

### Scenario 2: Azure VM with Azure Database for PostgreSQL

```bash
# 1. Create Azure VM (Standard_B2s, Ubuntu 22.04)
# 2. Create Azure Database for PostgreSQL (or use existing)
# 3. Follow QUICK_DEPLOY.md
# 4. Configure .env with Azure DB credentials
# 5. Run: docker-compose up -d
```

### Scenario 3: Any VPS with External PostgreSQL

```bash
# Works with any VPS provider (DigitalOcean, Linode, etc.)
# 1. Ubuntu 20.04+ server with Docker
# 2. Existing PostgreSQL instance (cloud or on-premise)
# 3. Follow QUICK_DEPLOY.md
# 4. Configure .env with PostgreSQL credentials
# 5. Run: docker-compose up -d
```

## 🔧 Prerequisites

### Server Requirements

- **OS**: Ubuntu 20.04+ (or similar Linux)
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Disk**: 30GB+ SSD
- **Network**: Public IP address

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- PostgreSQL client (psql)

### External Services

- **PostgreSQL Database**: 
  - AWS RDS PostgreSQL 15
  - Azure Database for PostgreSQL
  - Self-hosted PostgreSQL 15+
  
- **LLM Provider** (one of):
  - OpenAI API key
  - Anthropic API key
  - Google AI API key

## 📋 Deployment Steps Overview

1. **Server Setup** (5 min)
   - Launch server (EC2/Azure/VPS)
   - Install Docker and Docker Compose
   - Install basic tools

2. **Database Setup** (3 min)
   - Create database (if not exists)
   - Run migrations
   - Verify tables created

3. **Application Setup** (5 min)
   - Clone repository
   - Configure .env file
   - Update docker-compose.yml

4. **Deploy** (2 min)
   - Start services: `docker-compose up -d`
   - Verify health: `curl http://localhost:8000/health`

**Total Time: ~15 minutes**

## 🔐 Environment Configuration

### Required Environment Variables

```bash
# Database (External PostgreSQL)
DB_HOST=your-postgres-host
DB_PORT=5432
DB_NAME=intraflow_production
DB_USER=postgres
DB_PASSWORD=your_password
DATABASE_URL=postgresql+asyncpg://...

# Secrets (Generate with: openssl rand -hex 32)
JWT_SECRET=<secure_random_string>
WEBHOOK_SECRET=<secure_random_string>

# LLM Provider
OPENAI_API_KEY=sk-your-key

# Application
ENVIRONMENT=production
DEBUG=false
```

See `.env.example` in repository root for complete configuration.

## 🚦 Health Checks

After deployment, verify:

```bash
# API Health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Database Connection
docker-compose exec agent-orchestrator python -c "
from src.database.connection import engine
print('DB connected')
"

# Services Status
docker-compose ps
# All services should show "Up"

# Logs
docker-compose logs -f agent-orchestrator
# Should show no errors
```

## 🔄 CI/CD with GitHub Actions

GitHub Actions workflows are configured in `.github/workflows/`:

- **test.yml** - Runs on every push/PR
  - Linting, tests, code quality checks
  
- **deploy.yml** - Runs on push to main
  - Build Docker images
  - Deploy to server via SSH
  - Restart services

### Setup GitHub Actions

1. Add secrets in GitHub repository settings:
   ```
   DEPLOY_HOST = your-server-ip
   DEPLOY_USER = ubuntu
   DEPLOY_SSH_KEY = <private-ssh-key>
   ```

2. Push to main branch:
   ```bash
   git push origin main
   ```

3. GitHub Actions will automatically:
   - Run tests
   - Build images
   - Deploy to server

## 📊 Monitoring

### Built-in Monitoring

- **Prometheus**: http://your-server-ip:9090
- **Grafana**: http://your-server-ip:3001 (admin/admin)
- **Metrics Endpoint**: http://your-server-ip:8000/metrics

### Setup Grafana Dashboard

```bash
# 1. Access Grafana: http://your-server-ip:3001
# 2. Login: admin/admin
# 3. Add data source: Prometheus (http://prometheus:9090)
# 4. Import dashboard from monitoring/grafana/dashboards/
```

## 🆘 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Database connection failed | Check Security Group/NSG allows EC2/VM IP |
| Service won't start | Check logs: `docker-compose logs -f` |
| Health check fails | Verify .env configuration |
| Permission denied | Run with sudo or add user to docker group |

See `deploy/QUICK_DEPLOY.md` for detailed troubleshooting.

## 🔒 Security Checklist

- [ ] PostgreSQL not exposed to public internet
- [ ] Strong database password used
- [ ] JWT_SECRET and WEBHOOK_SECRET are random (not defaults)
- [ ] DEBUG=false in production
- [ ] CORS_ORIGINS restricted to your domain
- [ ] Firewall configured (only ports 22, 80, 443 open)
- [ ] SSL certificate installed (use certbot)
- [ ] Regular database backups configured
- [ ] Logs monitored for suspicious activity

## 📞 Support

- **Quick Issues**: See `deploy/QUICK_DEPLOY.md` troubleshooting section
- **Complete Guide**: See `deploy/AWS_DEPLOYMENT.md`
- **GitHub Issues**: https://github.com/PankajLal99/intraflow/issues

## 📝 License

MIT License - See LICENSE file in repository root

---

**Ready to deploy?** Start with `deploy/QUICK_DEPLOY.md` for fastest results!
