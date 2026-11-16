# IntraFlow Quick Deployment Guide

**For AWS EC2 / Azure VM with External PostgreSQL**

## 🚀 Quick Deploy (15 Minutes)

### Step 1: Server Setup (5 min)

```bash
# SSH into your EC2/Azure VM
ssh -i your-key.pem ubuntu@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again
exit
ssh -i your-key.pem ubuntu@your-server-ip
```

### Step 2: Clone and Configure (3 min)

```bash
# Clone repository
sudo mkdir -p /opt/intraflow
sudo chown $USER:$USER /opt/intraflow
cd /opt
git clone https://github.com/PankajLal99/intraflow.git
cd intraflow

# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

**Required Configuration in .env:**

```bash
# YOUR EXTERNAL POSTGRESQL DATABASE
DB_HOST=your-postgres-host.rds.amazonaws.com
DB_PORT=5432
DB_NAME=intraflow_production
DB_USER=postgres
DB_PASSWORD=your_actual_password

# Construct DATABASE_URL
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# GENERATE SECURE SECRETS
JWT_SECRET=$(openssl rand -hex 32)
WEBHOOK_SECRET=$(openssl rand -hex 32)

# YOUR LLM API KEY
OPENAI_API_KEY=sk-your-actual-openai-key

# PRODUCTION SETTINGS
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
```

**Quick Secret Generation:**

```bash
# Generate JWT_SECRET
openssl rand -hex 32

# Generate WEBHOOK_SECRET  
openssl rand -hex 32

# Copy these values into .env file
```

### Step 3: Database Setup (3 min)

```bash
# Install PostgreSQL client
sudo apt install -y postgresql-client

# Test connection
psql -h your-db-host -U postgres -d postgres -c "SELECT version();"

# Create database (if not exists)
psql -h your-db-host -U postgres -d postgres -c "CREATE DATABASE intraflow_production;"

# Run migrations
psql -h your-db-host -U postgres -d intraflow_production -f database/init.sql
psql -h your-db-host -U postgres -d intraflow_production -f database/migrations/002_multi_tenant_workflows.sql

# Verify tables created
psql -h your-db-host -U postgres -d intraflow_production -c "\dt"
```

### Step 4: Deploy Application (2 min)

```bash
# Update docker-compose.yml to use external PostgreSQL
# Comment out the postgres service in docker-compose.yml
nano docker-compose.yml

# Find and comment out (add # before each line):
# postgres:
#   image: postgres:15
#   ...

# Start services
cd /opt/intraflow
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agent-orchestrator
```

### Step 5: Verify Deployment (2 min)

```bash
# Check health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Check API docs
curl http://localhost:8000/docs

# Run validation
./scripts/validate-deployment.sh

# Check services
docker-compose ps
```

---

## 📋 .env Configuration Reference

### Minimal Required Configuration:

```bash
# Database (YOUR EXTERNAL POSTGRESQL)
DB_HOST=your-db.rds.amazonaws.com
DB_PORT=5432
DB_NAME=intraflow_production
DB_USER=postgres
DB_PASSWORD=your_password
DATABASE_URL=postgresql+asyncpg://postgres:your_password@your-db.rds.amazonaws.com:5432/intraflow_production

# Secrets (GENERATE NEW VALUES)
JWT_SECRET=<run: openssl rand -hex 32>
WEBHOOK_SECRET=<run: openssl rand -hex 32>

# LLM Provider
OPENAI_API_KEY=sk-your-key

# Application
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Full Configuration Options:

```bash
# DATABASE CONFIGURATION
DB_HOST=your-db.rds.amazonaws.com          # Your PostgreSQL host
DB_PORT=5432                                # Default PostgreSQL port
DB_NAME=intraflow_production                # Database name
DB_USER=postgres                            # Database username
DB_PASSWORD=your_secure_password            # Database password
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# REDIS CONFIGURATION
REDIS_URL=redis://localhost:6379/0          # Local Redis (included in Docker)

# APPLICATION SECRETS
JWT_SECRET=<generate with: openssl rand -hex 32>
JWT_EXPIRATION_MINUTES=1440
WEBHOOK_SECRET=<generate with: openssl rand -hex 32>

# LLM PROVIDER
OPENAI_API_KEY=sk-your-actual-key
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4o-mini

# APPLICATION SETTINGS
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# RATE LIMITING
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_IP_PER_MINUTE=300

# LOGGING
LOG_LEVEL=INFO

# SECURITY
BCRYPT_ROUNDS=12
SESSION_TIMEOUT=3600
MAX_REQUEST_SIZE_MB=10
```

---

## 🔧 Useful Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f agent-orchestrator

# Check service status
docker-compose ps
```

### Database Operations

```bash
# Connect to database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# Backup database
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$(date +%Y%m%d).sql

# Restore database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backup.sql

# Run migrations
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/init.sql
```

### Monitoring

```bash
# Check health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics

# Access Grafana (configure after deployment)
http://your-server-ip:3001  # Login: admin/admin

# Access Prometheus
http://your-server-ip:9090
```

### Updates

```bash
# Pull latest code
cd /opt/intraflow
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache agent-orchestrator
docker-compose up -d

# Or use deployment script
./deploy/deploy.sh production
```

---

## 🚨 Troubleshooting

### Database Connection Failed

```bash
# Test connection
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;"

# Check .env file
cat .env | grep DATABASE_URL

# Check security group (AWS) or NSG (Azure)
# Ensure your EC2/VM IP is allowed to connect to PostgreSQL

# Verify from container
docker-compose exec agent-orchestrator python -c "
import asyncio
from src.database.connection import engine
async def test():
    async with engine.begin() as conn:
        await conn.execute('SELECT 1')
        print('✅ Database connected')
asyncio.run(test())
"
```

### Service Won't Start

```bash
# Check logs
docker-compose logs -f agent-orchestrator

# Check disk space
df -h

# Check memory
free -h

# Verify .env file
cat .env

# Restart services
docker-compose restart
```

### Health Check Fails

```bash
# Check if service is running
docker-compose ps

# Check logs for errors
docker-compose logs --tail=100 agent-orchestrator

# Test locally
docker-compose exec agent-orchestrator curl http://localhost:8000/health

# Check port binding
sudo netstat -tulpn | grep 8000
```

---

## 📱 GitHub Actions Setup (Optional)

### Add Secrets to GitHub Repository

1. Go to: `https://github.com/YOUR_USERNAME/intraflow/settings/secrets/actions`
2. Add these secrets:

```
DEPLOY_HOST = your-server-ip-or-domain
DEPLOY_USER = ubuntu (or azureuser for Azure)
DEPLOY_SSH_KEY = <your-private-ssh-key>
DEPLOY_PORT = 22
```

### Enable Auto-Deploy

```bash
# Every push to main branch will:
# 1. Run tests
# 2. Build Docker images
# 3. Deploy to your server
# 4. Restart services

# Workflow files are already in .github/workflows/
```

---

## ✅ Production Checklist

Before going live:

- [ ] PostgreSQL accessible from EC2/VM
- [ ] Database migrations completed (`\dt` shows tables)
- [ ] .env file configured with real values
- [ ] JWT_SECRET and WEBHOOK_SECRET are secure random strings
- [ ] OPENAI_API_KEY configured
- [ ] DEBUG=false in .env
- [ ] ENVIRONMENT=production in .env
- [ ] Health check returns 200: `curl http://localhost:8000/health`
- [ ] Services running: `docker-compose ps` shows "Up"
- [ ] Logs show no errors: `docker-compose logs -f`

---

## 🔒 Security Notes

1. **Never commit .env file to Git**
2. **Rotate secrets regularly** (JWT_SECRET, WEBHOOK_SECRET)
3. **Use strong database passwords**
4. **Configure firewall** (AWS Security Groups / Azure NSG)
5. **Enable SSL** with Let's Encrypt (see AWS_DEPLOYMENT.md)
6. **Regular backups** of PostgreSQL database
7. **Monitor logs** for suspicious activity

---

## 📞 Support

- **Full Deployment Guide**: See `deploy/AWS_DEPLOYMENT.md`
- **Documentation**: See repository root for comprehensive guides
- **Issues**: https://github.com/PankajLal99/intraflow/issues

---

**Total Time**: ~15 minutes from server to running application! 🚀

Your IntraFlow instance is now running with your external PostgreSQL database.

Access:
- API: http://your-server-ip:8000
- API Docs: http://your-server-ip:8000/docs
- Health: http://your-server-ip:8000/health
