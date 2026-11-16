# 🚀 IntraFlow Deployment Setup - Complete!

**Status**: Ready for AWS/Azure deployment with external PostgreSQL

---

## ✅ What's Been Added

### 1. GitHub Actions CI/CD Workflows

**Location**: `.github/workflows/`

#### `test.yml` - Automated Testing
- Runs on every push and pull request
- Backend tests with PostgreSQL and Redis
- Frontend build verification
- Code quality checks (Ruff, Black, MyPy, Bandit)
- Integration tests
- Coverage reporting to Codecov

#### `deploy.yml` - Automated Deployment
- Runs on push to main branch
- Builds Docker images
- Pushes to GitHub Container Registry
- Deploys to your server via SSH
- Health check verification
- Automatic rollback on failure

### 2. Deployment Scripts

**Location**: `deploy/`

#### `deploy.sh` - Automated Deployment Script
```bash
./deploy/deploy.sh production
```

Features:
- ✅ Prerequisites checking
- ✅ Automatic backup creation
- ✅ Git pull latest code
- ✅ Docker image building
- ✅ Service restart
- ✅ Database migration verification
- ✅ Health check validation
- ✅ Cleanup old images

### 3. Deployment Documentation

#### `deploy/QUICK_DEPLOY.md` - 15-Minute Setup Guide
Quick start guide for immediate deployment:
- Step-by-step commands
- Database configuration
- Service startup
- Verification steps

#### `deploy/AWS_DEPLOYMENT.md` - Complete Production Guide
Comprehensive guide covering:
- AWS EC2 setup
- Azure VM setup
- External PostgreSQL configuration (RDS, Azure DB)
- Nginx reverse proxy
- SSL/TLS with Let's Encrypt
- Security best practices
- Monitoring setup
- Troubleshooting

#### `deploy/README.md` - Deployment Directory Guide
Overview of all deployment resources and quick reference.

### 4. Environment Configuration

**Updated**: `.env.example`

New external PostgreSQL configuration:
```bash
# External PostgreSQL (AWS RDS / Azure Database)
DB_HOST=your-postgres-host.amazonaws.com
DB_PORT=5432
DB_NAME=intraflow_production
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Constructed DATABASE_URL
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

---

## 🎯 How to Deploy

### Quick Deployment (15 minutes)

1. **Launch Server**
   ```bash
   # AWS EC2: t3.medium, Ubuntu 22.04
   # or Azure VM: Standard_B2s, Ubuntu 22.04
   ```

2. **Install Docker**
   ```bash
   ssh ubuntu@your-server-ip
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   ```

3. **Clone & Configure**
   ```bash
   cd /opt
   git clone https://github.com/PankajLal99/intraflow.git
   cd intraflow
   cp .env.example .env
   nano .env  # Add your database credentials
   ```

4. **Setup Database**
   ```bash
   # Run migrations on your external PostgreSQL
   psql -h your-db-host -U postgres -d intraflow_production -f database/init.sql
   psql -h your-db-host -U postgres -d intraflow_production -f database/migrations/002_multi_tenant_workflows.sql
   ```

5. **Deploy**
   ```bash
   docker-compose up -d
   curl http://localhost:8000/health
   ```

**Done!** 🎉

See `deploy/QUICK_DEPLOY.md` for detailed steps.

---

## 🔧 GitHub Actions Setup

### Configure Secrets

Go to: `https://github.com/YOUR_USERNAME/intraflow/settings/secrets/actions`

Add these secrets:

```
DEPLOY_HOST = your-server-ip-or-domain
DEPLOY_USER = ubuntu (or azureuser)
DEPLOY_SSH_KEY = <your-private-ssh-key-content>
DEPLOY_PORT = 22
```

### How It Works

```
Push to main → GitHub Actions triggers:
  ├─ Run tests (pytest, linting)
  ├─ Build Docker images
  ├─ Push to registry
  ├─ SSH to server
  ├─ Pull latest code
  ├─ Deploy services
  └─ Verify health check
```

Every push to main automatically deploys to production!

---

## 📋 Environment Variables Guide

### Required Configuration

```bash
# DATABASE (Your External PostgreSQL)
DB_HOST=your-db.rds.amazonaws.com       # ← Your PostgreSQL host
DB_PORT=5432
DB_NAME=intraflow_production             # ← Your database name
DB_USER=postgres                         # ← Your DB username
DB_PASSWORD=your_secure_password         # ← Your DB password

# Construct DATABASE_URL
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# SECRETS (Generate with: openssl rand -hex 32)
JWT_SECRET=<run_openssl_rand_hex_32>
WEBHOOK_SECRET=<run_openssl_rand_hex_32>

# LLM PROVIDER
OPENAI_API_KEY=sk-your-actual-key

# PRODUCTION SETTINGS
ENVIRONMENT=production
DEBUG=false
```

### Generate Secure Secrets

```bash
# Generate JWT_SECRET
openssl rand -hex 32

# Generate WEBHOOK_SECRET
openssl rand -hex 32

# Copy output to .env file
```

---

## 🗄️ Database Setup

### Your External PostgreSQL

You mentioned:
> "We already have PostgreSQL installed in AWS instance"

Perfect! Just configure these in `.env`:

```bash
DB_HOST=your-postgres-host-or-ip
DB_PORT=5432
DB_NAME=intraflow_production
DB_USER=postgres
DB_PASSWORD=your_password
```

### Run Migrations

From your server or any machine with PostgreSQL client:

```bash
# Create database
psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE intraflow_production;"

# Run migrations
psql -h $DB_HOST -U $DB_USER -d intraflow_production -f database/init.sql
psql -h $DB_HOST -U $DB_USER -d intraflow_production -f database/migrations/002_multi_tenant_workflows.sql

# Verify
psql -h $DB_HOST -U $DB_USER -d intraflow_production -c "\dt"
```

You should see these tables:
- tenants
- tenant_users
- whatsapp_sessions
- workflows
- workflow_executions
- users
- conversations
- messages
- agent_interactions
- usage_records

---

## 📦 What Gets Deployed

### Services Stack

```
┌─────────────────────────┐
│   Your EC2/Azure VM     │
│                         │
│  ┌──────────────────┐   │
│  │ agent-orchestrator│   │ ← FastAPI Backend (port 8000)
│  └──────────────────┘   │
│                         │
│  ┌──────────────────┐   │
│  │     Redis        │   │ ← Message Queue (port 6379)
│  └──────────────────┘   │
│                         │
│  ┌──────────────────┐   │
│  │     OpenWA       │   │ ← WhatsApp (port 2785)
│  └──────────────────┘   │
│                         │
│  ┌──────────────────┐   │
│  │   Prometheus     │   │ ← Metrics (port 9090)
│  └──────────────────┘   │
│                         │
│  ┌──────────────────┐   │
│  │    Grafana       │   │ ← Dashboards (port 3001)
│  └──────────────────┘   │
└─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│  External PostgreSQL    │ ← Your existing DB
│  (AWS RDS / Azure DB)   │
└─────────────────────────┘
```

### Excluded Services

Since you have external PostgreSQL:
- ❌ PostgreSQL container (not needed)
- ✅ All other services run in Docker

---

## ✅ Deployment Checklist

Before deploying:

- [ ] AWS EC2 or Azure VM launched
- [ ] External PostgreSQL accessible from VM
- [ ] PostgreSQL credentials available (host, port, user, password, db name)
- [ ] GitHub repository forked/cloned
- [ ] .env file configured with database credentials
- [ ] JWT_SECRET and WEBHOOK_SECRET generated
- [ ] OpenAI API key available
- [ ] Docker installed on server
- [ ] Database migrations completed

After deploying:

- [ ] Health check returns 200: `curl http://localhost:8000/health`
- [ ] Services running: `docker-compose ps`
- [ ] API docs accessible: `curl http://localhost:8000/docs`
- [ ] No errors in logs: `docker-compose logs -f`

---

## 🔒 Security Notes

1. **Database Security**
   - ✅ PostgreSQL should NOT be publicly accessible
   - ✅ Only allow connections from your EC2/VM IP
   - ✅ Use AWS Security Groups or Azure NSG to restrict access
   - ✅ Use strong password for database

2. **Application Secrets**
   - ✅ Never commit .env file to Git
   - ✅ Use `openssl rand -hex 32` for JWT_SECRET and WEBHOOK_SECRET
   - ✅ Rotate secrets regularly

3. **Server Security**
   - ✅ Only open ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
   - ✅ Use SSH keys (not passwords)
   - ✅ Keep system updated: `sudo apt update && sudo apt upgrade`

---

## 📊 Monitoring

### Access Dashboards

- **API Health**: http://your-server-ip:8000/health
- **API Docs**: http://your-server-ip:8000/docs
- **Metrics**: http://your-server-ip:8000/metrics
- **Prometheus**: http://your-server-ip:9090
- **Grafana**: http://your-server-ip:3001 (admin/admin)

### Set Up Grafana

1. Open http://your-server-ip:3001
2. Login: admin/admin
3. Add Prometheus data source: `http://prometheus:9090`
4. Import dashboards from `monitoring/grafana/dashboards/`

---

## 🔄 Updates & Maintenance

### Manual Update

```bash
ssh ubuntu@your-server-ip
cd /opt/intraflow
git pull origin main
docker-compose down
docker-compose build --no-cache agent-orchestrator
docker-compose up -d
```

### Automated Update (with deployment script)

```bash
ssh ubuntu@your-server-ip
cd /opt/intraflow
./deploy/deploy.sh production
```

### Automated Update (with GitHub Actions)

Just push to main:
```bash
git push origin main
```

GitHub Actions will automatically deploy! 🚀

---

## 📞 Support & Documentation

### Quick References

- **Quick Deploy**: `deploy/QUICK_DEPLOY.md` (15-minute guide)
- **Full Guide**: `deploy/AWS_DEPLOYMENT.md` (complete production setup)
- **Deploy Scripts**: `deploy/deploy.sh` (automated deployment)
- **Environment**: `.env.example` (configuration template)

### Troubleshooting

See `deploy/QUICK_DEPLOY.md` for common issues and solutions.

### Need Help?

- GitHub Issues: https://github.com/PankajLal99/intraflow/issues
- Check logs: `docker-compose logs -f`
- Verify health: `curl http://localhost:8000/health`

---

## 🎉 Summary

**Everything is ready for deployment!**

You now have:
- ✅ Complete CI/CD pipeline with GitHub Actions
- ✅ Automated deployment scripts
- ✅ External PostgreSQL configuration
- ✅ Comprehensive deployment documentation
- ✅ Security best practices
- ✅ Monitoring setup

**Next steps:**

1. Configure your `.env` file with database credentials
2. Run database migrations
3. Deploy: `docker-compose up -d`
4. Verify: `curl http://localhost:8000/health`

**Total deployment time: ~15 minutes** ⏱️

See `deploy/QUICK_DEPLOY.md` to get started!

---

**Committed to GitHub**: All deployment files pushed to `main` branch

🚀 **Ready to deploy to production!**
