# AWS/Azure Deployment Guide for IntraFlow

Complete guide for deploying IntraFlow to AWS EC2 or Azure VM with external PostgreSQL database.

## Prerequisites

- AWS EC2 instance or Azure VM (Ubuntu 20.04+ or similar)
- PostgreSQL database (AWS RDS, Azure Database for PostgreSQL, or self-hosted)
- Domain name (optional, for SSL)
- GitHub account (for CI/CD)

## Architecture Overview

```
┌─────────────────────┐
│   Load Balancer     │ (Optional: AWS ALB / Azure LB)
│   + SSL/TLS         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   EC2 / Azure VM    │
│                     │
│  ┌───────────────┐  │
│  │ IntraFlow     │  │
│  │ Docker Stack  │  │
│  │  - API        │  │
│  │  - Redis      │  │
│  │  - OpenWA     │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ External PostgreSQL │ (AWS RDS / Azure Database)
│  (Already Exists)   │
└─────────────────────┘
```

---

## Part 1: Server Setup

### 1.1 Launch EC2 Instance (AWS)

```bash
# Recommended instance type: t3.medium or t3.large
# OS: Ubuntu 22.04 LTS
# Storage: 30GB+ SSD

# Security Group Rules:
# - Port 22 (SSH) - Your IP only
# - Port 80 (HTTP) - 0.0.0.0/0
# - Port 443 (HTTPS) - 0.0.0.0/0
# - Port 8000 (API) - Internal only or Your IP (for testing)
```

**Or Azure VM:**

```bash
# Recommended size: Standard_B2s or Standard_B2ms
# OS: Ubuntu 22.04 LTS
# Disk: Standard SSD 30GB+

# NSG Rules:
# - Port 22 (SSH) - Your IP
# - Port 80 (HTTP) - Internet
# - Port 443 (HTTPS) - Internet
```

### 1.2 Connect to Server

```bash
# AWS EC2
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Azure VM
ssh azureuser@your-vm-public-ip
```

### 1.3 Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Logout and login again for group changes to take effect
exit
```

### 1.4 Install Additional Tools

```bash
# Reconnect to server
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Git, Nginx, and utilities
sudo apt install -y git nginx certbot python3-certbot-nginx htop curl

# Verify Git
git --version
```

---

## Part 2: Database Setup (PostgreSQL)

### 2.1 Option A: Use Existing AWS RDS PostgreSQL

```bash
# Your PostgreSQL is already running on AWS
# Note down these details:
# - Endpoint: your-db.xxxxx.us-east-1.rds.amazonaws.com
# - Port: 5432
# - Database Name: intraflow_production
# - Username: postgres (or your username)
# - Password: your-password

# Test connection from EC2 (install psql client)
sudo apt install -y postgresql-client

# Test connection
psql -h your-db.xxxxx.us-east-1.rds.amazonaws.com \
     -U postgres \
     -d postgres \
     -c "SELECT version();"
```

### 2.2 Option B: Use Azure Database for PostgreSQL

```bash
# Azure PostgreSQL connection string format:
# Host: your-db.postgres.database.azure.com
# Port: 5432
# Database: intraflow_production
# Username: adminuser@your-db
# Password: your-password

# Test connection
psql "host=your-db.postgres.database.azure.com port=5432 dbname=postgres user=adminuser@your-db password=your-password sslmode=require"
```

### 2.3 Create Database and Run Migrations

```bash
# Create database (if not exists)
psql -h your-db-host -U your-username -d postgres -c "CREATE DATABASE intraflow_production;"

# Download migration files to server
cd /tmp
git clone https://github.com/PankajLal99/intraflow.git
cd intraflow

# Run base schema
psql -h your-db-host -U your-username -d intraflow_production -f database/init.sql

# Run multi-tenant migration
psql -h your-db-host -U your-username -d intraflow_production -f database/migrations/002_multi_tenant_workflows.sql

# Verify tables
psql -h your-db-host -U your-username -d intraflow_production -c "\dt"

# You should see: tenants, workflows, users, conversations, messages, etc.
```

---

## Part 3: Application Deployment

### 3.1 Clone Repository

```bash
# Create deployment directory
sudo mkdir -p /opt/intraflow
sudo chown $USER:$USER /opt/intraflow

# Clone repository
cd /opt
git clone https://github.com/PankajLal99/intraflow.git
cd intraflow
```

### 3.2 Configure Environment Variables

```bash
# Copy .env template
cp .env.example .env

# Edit .env file
nano .env
```

**Configure these critical values:**

```bash
# Database Configuration (YOUR EXTERNAL POSTGRESQL)
DB_HOST=your-db.xxxxx.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=intraflow_production
DB_USER=postgres
DB_PASSWORD=your_actual_database_password

DATABASE_URL=postgresql+asyncpg://postgres:your_actual_database_password@your-db.xxxxx.us-east-1.rds.amazonaws.com:5432/intraflow_production

# Redis (local on same server)
REDIS_URL=redis://localhost:6379/0

# Generate secure secrets (run: openssl rand -hex 32)
JWT_SECRET=<generate_secure_random_32_char_string>
WEBHOOK_SECRET=<generate_secure_random_32_char_string>

# LLM Provider (add your API key)
OPENAI_API_KEY=sk-your-actual-openai-api-key
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4o-mini

# Application Settings
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS (add your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=INFO
```

**Generate secure secrets:**

```bash
# Generate JWT_SECRET
openssl rand -hex 32

# Generate WEBHOOK_SECRET
openssl rand -hex 32

# Add these to your .env file
```

### 3.3 Update Docker Compose for External DB

```bash
# Edit docker-compose.yml to comment out local PostgreSQL
nano docker-compose.yml
```

**Comment out the postgres service** (since you're using external DB):

```yaml
# Comment out or remove this section:
# postgres:
#   image: postgres:15
#   ...
```

**Keep these services active:**
- redis
- agent-orchestrator
- openwa
- prometheus
- grafana

### 3.4 Deploy Application

```bash
# Pull Docker images
docker-compose pull

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agent-orchestrator
```

### 3.5 Verify Deployment

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected output: {"status":"healthy"}

# Check API docs
curl http://localhost:8000/docs

# Check metrics
curl http://localhost:8000/metrics

# Run validation script
./scripts/validate-deployment.sh
```

---

## Part 4: Nginx Reverse Proxy Setup

### 4.1 Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/intraflow
```

**Add this configuration:**

```nginx
upstream intraflow_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # API endpoints
    location /api {
        proxy_pass http://intraflow_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Webhook endpoint
    location /webhook {
        proxy_pass http://intraflow_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://intraflow_backend;
        access_log off;
    }

    # API documentation
    location /docs {
        proxy_pass http://intraflow_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend (if serving from this server)
    location / {
        root /opt/intraflow/frontend/out;
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/intraflow /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 4.2 Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically update your Nginx config for HTTPS

# Test auto-renewal
sudo certbot renew --dry-run

# Auto-renewal is configured via systemd timer
```

---

## Part 5: GitHub Actions CI/CD Setup

### 5.1 Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

```
DEPLOY_HOST          = your-ec2-public-ip or domain
DEPLOY_USER          = ubuntu (or azureuser for Azure)
DEPLOY_SSH_KEY       = <paste your private SSH key>
DEPLOY_PORT          = 22
```

### 5.2 Generate Deployment SSH Key (Optional)

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/intraflow_deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/intraflow_deploy.pub ubuntu@your-server-ip

# Copy private key content
cat ~/.ssh/intraflow_deploy

# Add private key to GitHub Secrets as DEPLOY_SSH_KEY
```

### 5.3 Test Workflow

```bash
# Push to main branch
git add .
git commit -m "feat: add CI/CD workflows"
git push origin main

# GitHub Actions will:
# 1. Run tests
# 2. Build Docker images
# 3. Deploy to your server
# 4. Restart services
```

---

## Part 6: Monitoring Setup

### 6.1 Access Monitoring Dashboards

```bash
# Prometheus: http://your-server-ip:9090
# Grafana: http://your-server-ip:3001 (admin/admin)

# Configure Grafana data source:
# 1. Login to Grafana
# 2. Add Prometheus data source: http://prometheus:9090
# 3. Import IntraFlow dashboard
```

### 6.2 Setup Alerting (Optional)

```bash
# Configure Prometheus alerts
nano /opt/intraflow/monitoring/prometheus/alerts.yml

# Configure Alertmanager
nano /opt/intraflow/monitoring/alertmanager/config.yml
```

---

## Part 7: Frontend Deployment

### 7.1 Build Frontend

```bash
cd /opt/intraflow/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Frontend will be built to /opt/intraflow/frontend/out
# Nginx will serve it from the location / block
```

### 7.2 Update Frontend Environment

```bash
# Create frontend .env.production
nano /opt/intraflow/frontend/.env.production
```

```bash
NEXT_PUBLIC_API_URL=https://yourdomain.com
```

---

## Part 8: Production Checklist

### Before Going Live:

- [ ] PostgreSQL database accessible from EC2/VM
- [ ] Database migrations completed
- [ ] .env file configured with production values
- [ ] All secrets are secure random strings (not defaults)
- [ ] LLM API keys configured
- [ ] CORS origins set to your domain
- [ ] DEBUG=false in .env
- [ ] SSL certificate installed
- [ ] Nginx reverse proxy configured
- [ ] Health check returns 200 OK
- [ ] Metrics endpoint accessible
- [ ] GitHub Actions CI/CD working
- [ ] Frontend deployed and accessible
- [ ] Monitoring dashboards configured
- [ ] Backups configured for database
- [ ] Firewall rules properly configured

### Test Production Deployment:

```bash
# Test API
curl https://yourdomain.com/health

# Test signup
curl -X POST https://yourdomain.com/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "tenant_name": "Test Company"
  }'

# Test metrics
curl https://yourdomain.com/metrics

# Run E2E tests
./scripts/e2e-test.sh
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Test from server
psql -h your-db-host -U your-username -d intraflow_production -c "SELECT 1;"

# Check security group (AWS) allows EC2 IP
# Check NSG (Azure) allows VM IP
# Verify DATABASE_URL in .env is correct
```

### Docker Services Not Starting

```bash
# Check logs
docker-compose logs -f

# Check disk space
df -h

# Check memory
free -h

# Restart services
docker-compose restart
```

### Health Check Fails

```bash
# Check agent-orchestrator logs
docker-compose logs -f agent-orchestrator

# Check if database is accessible
docker-compose exec agent-orchestrator python -c "
import asyncio
from src.database.connection import engine
async def test():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('DB OK')
asyncio.run(test())
"
```

---

## Maintenance

### Update Application

```bash
cd /opt/intraflow

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or use deployment script
./deploy/deploy.sh production
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f agent-orchestrator

# Last 100 lines
docker-compose logs --tail=100 agent-orchestrator
```

### Database Backup

```bash
# Backup database
pg_dump -h your-db-host -U your-username -d intraflow_production > backup_$(date +%Y%m%d).sql

# Restore backup
psql -h your-db-host -U your-username -d intraflow_production < backup_20241116.sql
```

---

## Security Best Practices

1. **Firewall**: Only allow necessary ports
2. **SSH**: Disable password auth, use key-only
3. **Database**: Use separate read-only user for analytics
4. **Secrets**: Rotate JWT_SECRET and WEBHOOK_SECRET regularly
5. **SSL**: Keep certificates up to date
6. **Monitoring**: Set up alerts for failures
7. **Backups**: Automated daily database backups
8. **Updates**: Keep Docker and system packages updated

---

## Support

For issues:
- Check logs: `docker-compose logs -f`
- Review health: `curl http://localhost:8000/health`
- GitHub Issues: https://github.com/PankajLal99/intraflow/issues

---

**Deployment complete! 🎉**

Your IntraFlow instance is now running in production with external PostgreSQL database.
