# IntraFlow Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose installed
- Git installed
- OpenAI API key (or Anthropic/Google)

### 1. Clone & Configure

```bash
# Clone repository
git clone https://github.com/PankajLal99/intraflow.git
cd intraflow

# Generate secrets and configure .env
./quick-start.sh

# Edit .env and add your LLM API key
nano .env
# Add: OPENAI_API_KEY=sk-your-key-here
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agent-orchestrator
```

### 3. Initialize Database

```bash
# Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready -U whatsapp

# Run base schema
docker-compose exec -T postgres psql -U whatsapp -d whatsapp < database/init.sql

# Run multi-tenant migration
docker-compose exec -T postgres psql -U whatsapp -d whatsapp < database/migrations/002_multi_tenant_workflows.sql

# Load seed data (optional, for testing)
docker-compose exec -T postgres psql -U whatsapp -d whatsapp < database/seeds/001_test_data.sql

# Verify tables created
docker-compose exec postgres psql -U whatsapp -d whatsapp -c "\dt"
```

### 4. Connect WhatsApp

```bash
# Open OpenWA dashboard
open http://localhost:2785

# Scan QR code with WhatsApp
# Your phone number is now connected!
```

### 5. Test the System

```bash
# Create a test tenant
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "Test Company",
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'

# Save the access_token from response

# Send a WhatsApp message to your connected number
# It should be processed by the agent!
```

---

## Production Deployment (AWS EC2)

### Infrastructure Requirements

**Minimum Specs:**
- EC2 Instance: t3.medium (2 vCPU, 4GB RAM)
- EBS Volume: 30GB GP3
- PostgreSQL RDS: db.t3.micro (or hosted on EC2)
- Redis ElastiCache: cache.t3.micro (or hosted on EC2)

**Recommended Specs (for scale):**
- EC2 Instance: t3.large (2 vCPU, 8GB RAM)
- EBS Volume: 50GB GP3
- PostgreSQL RDS: db.t3.small
- Redis ElastiCache: cache.t3.small
- Application Load Balancer (for multiple instances)

### 1. Launch EC2 Instance

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/PankajLal99/intraflow.git
cd intraflow

# Create production .env
cp .env.example .env

# Edit configuration
nano .env
```

**Production .env:**
```bash
# Application
ENVIRONMENT=production
PORT=8000
DEBUG=false

# Security (use strong random secrets!)
WEBHOOK_SECRET=<generate-with-openssl-rand-hex-32>
JWT_SECRET=<generate-with-openssl-rand-hex-32>

# OpenWA
OPENWA_API_KEY=<your-openwa-api-key>

# Database (use RDS endpoint)
DATABASE_URL=postgresql://whatsapp:password@your-rds-endpoint:5432/whatsapp

# Redis (use ElastiCache endpoint)
REDIS_URL=redis://your-elasticache-endpoint:6379

# LLM
OPENAI_API_KEY=sk-your-production-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# External APIs
PRODUCT_API_URL=https://api.yourcompany.com/products
PRODUCT_API_KEY=your-api-key
```

### 3. Configure Security Groups

**EC2 Instance Security Group:**
- Port 22 (SSH): Your IP only
- Port 8000 (FastAPI): ALB security group
- Port 2785 (OpenWA): Your IP for QR setup

**RDS Security Group:**
- Port 5432 (PostgreSQL): EC2 security group

**ElastiCache Security Group:**
- Port 6379 (Redis): EC2 security group

### 4. Start Application

```bash
# Start services
docker-compose up -d

# Initialize database (first time only)
docker-compose exec -T postgres psql -U whatsapp -d whatsapp < database/init.sql
docker-compose exec -T postgres psql -U whatsapp -d whatsapp < database/migrations/002_multi_tenant_workflows.sql

# Check logs
docker-compose logs -f agent-orchestrator

# Test health endpoint
curl http://localhost:8000/health
```

### 5. Configure Domain & SSL

```bash
# Install Nginx
sudo apt install nginx -y

# Configure Nginx as reverse proxy
sudo nano /etc/nginx/sites-available/intraflow
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/intraflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

### 6. Configure Auto-Start

```bash
# Create systemd service
sudo nano /etc/systemd/system/intraflow.service
```

**Service File:**
```ini
[Unit]
Description=IntraFlow Docker Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/intraflow
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Enable auto-start
sudo systemctl enable intraflow
sudo systemctl start intraflow
```

---

## Monitoring Setup

### 1. Access Grafana

```bash
# Grafana is running on port 3001
open http://your-ec2-ip:3001

# Default credentials
Username: admin
Password: (from GRAFANA_PASSWORD in .env)
```

### 2. Add Prometheus Data Source

1. Go to Configuration → Data Sources
2. Add Prometheus
3. URL: `http://prometheus:9090`
4. Save & Test

### 3. Import Dashboards

Use these dashboard IDs:
- FastAPI Metrics: Create custom or use 11133
- Redis Metrics: 11835
- PostgreSQL Metrics: 9628

### 4. Configure Alerts

Create alerts for:
- High error rate (> 5%)
- Slow response time (> 2s)
- Queue depth (> 1000 messages)
- Database connection pool exhaustion

---

## Backup Strategy

### Database Backups

```bash
# Daily backup script
cat > /home/ubuntu/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/home/ubuntu/backups
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U whatsapp whatsapp | gzip > $BACKUP_DIR/intraflow_$DATE.sql.gz
find $BACKUP_DIR -name "intraflow_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /home/ubuntu/backup-db.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup-db.sh
```

### Application Backups

```bash
# Backup .env and docker-compose.yml
tar -czf /home/ubuntu/backups/config_$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

---

## Scaling Strategy

### Horizontal Scaling

1. **Multiple Agent Orchestrators**:
   ```yaml
   agent-orchestrator:
     deploy:
       replicas: 3
   ```

2. **Load Balancer**:
   - Use AWS ALB
   - Health check: `GET /health`
   - Sticky sessions: Enabled

3. **Redis Cluster**:
   - Use Redis Cluster mode in ElastiCache
   - Multiple read replicas

### Vertical Scaling

- Start: t3.medium (2 vCPU, 4GB RAM)
- Medium: t3.large (2 vCPU, 8GB RAM)
- High: t3.xlarge (4 vCPU, 16GB RAM)

---

## Troubleshooting

### Service Won't Start

```bash
# Check Docker logs
docker-compose logs agent-orchestrator

# Check if ports are available
sudo netstat -tulpn | grep :8000

# Rebuild image
docker-compose build --no-cache agent-orchestrator
docker-compose up -d
```

### Database Connection Issues

```bash
# Test connection
docker-compose exec agent-orchestrator python -c "
from src.database.connection import engine
print('Connection test')
"

# Check PostgreSQL status
docker-compose exec postgres pg_isready -U whatsapp
```

### OpenWA Not Connecting

```bash
# Check OpenWA logs
docker-compose logs openwa

# Verify webhook URL
docker-compose exec openwa env | grep WEBHOOK

# Regenerate QR code
# Open http://localhost:2785 and rescan
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Restart services
docker-compose restart agent-orchestrator

# Increase worker pool size in settings
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong random secrets (32+ characters)
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Configure firewall (only necessary ports open)
- [ ] Regular security updates (`apt update && apt upgrade`)
- [ ] Backup encryption
- [ ] API rate limiting enabled
- [ ] Parent Agent guardrails configured
- [ ] Monitoring and alerting active
- [ ] Log retention policy set

---

## Performance Tuning

### Database Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_tenant ON messages(tenant_id);
CREATE INDEX idx_workflows_tenant_status ON workflows(tenant_id, status);
```

### Redis Configuration

```conf
# /etc/redis/redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### FastAPI Optimization

```python
# In src/config/settings.py
WORKERS = 4  # Number of Uvicorn workers
MAX_CONNECTIONS = 100  # Database connection pool
```

---

## Cost Estimation (Monthly)

### AWS Infrastructure
- EC2 t3.medium: $30
- RDS db.t3.micro: $15
- ElastiCache cache.t3.micro: $12
- EBS 30GB: $3
- Data Transfer: $10
- **Total Infrastructure**: ~$70/month

### API Costs
- OpenAI (10K messages @ GPT-4o-mini): $7
- **Total**: ~$77/month

### Scaling (100K messages/month)
- Infrastructure: $150
- OpenAI: $70
- **Total**: ~$220/month

---

**Document Version**: 1.0  
**Last Updated**: November 16, 2026  
**For**: IntraFlow v1.0
