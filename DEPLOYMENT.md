# Production Deployment Guide

## 🚀 Quick Start

This guide covers deploying the Multi-Tenant ERP Platform to production.

---

## 📋 Prerequisites

- **Server:** Linux (Ubuntu 20.04+ or Debian 11+ recommended)
- **Docker:** Version 20.10+
- **Docker Compose:** Version 2.0+
- **Domain:** Registered domain with DNS configured
- **SSL Certificate:** Let's Encrypt or commercial SSL

---

## ⚙️ Pre-Deployment Checklist

### 1. Generate Secure Credentials

```bash
cd backend
python3 scripts/generate_secrets.py
```

**Save the output securely!** You'll need:
- `SECRET_KEY` for JWT tokens
- `ADMIN_PASSWORD` for admin account
- `DB_PASSWORD` for PostgreSQL

### 2. Configure Environment Variables

```bash
cp .env.production.example .env.production
```

Edit `.env.production` with your secure values:
- ✅ Update `SECRET_KEY`
- ✅ Update `ADMIN_EMAIL` and `ADMIN_PASSWORD`
- ✅ Update `DB_PASSWORD`
- ✅ Update `CORS_ORIGINS` with your domain
- ✅ Update `API_URL` with your API domain

### 3. Review Configuration

**Backend** (`backend/.env`):
```bash
# Ensure these are set correctly
ENVIRONMENT=production
DATABASE_URL=postgresql://...
SECRET_KEY=<your-secure-key>
CORS_ORIGINS=["https://yourdomain.com"]
```

**Frontend** (`.env.production`):
```bash
VITE_API_URL=https://api.yourdomain.com
```

---

## 🐳 Docker Deployment

### Option 1: Using Production Docker Compose

```bash
# Load environment variables
export $(cat .env.production | xargs)

# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check health
curl http://localhost:8000/api/v1/healthz
```

### Option 2: Manual Docker Commands

```bash
# Build backend
docker build -t erp-backend:latest ./backend

# Build frontend
docker build -f frontend/Dockerfile.prod -t erp-frontend:latest ./frontend

# Run PostgreSQL
docker run -d \
  --name erp-db \
  -e POSTGRES_USER=erp_user \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=erp_db \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Run backend
docker run -d \
  --name erp-backend \
  -p 8000:8000 \
  --link erp-db:db \
  -e DATABASE_URL=postgresql://erp_user:secure_password@db:5432/erp_db \
  -e SECRET_KEY=your-secret-key \
  -e ENVIRONMENT=production \
  erp-backend:latest

# Run frontend
docker run -d \
  --name erp-frontend \
  -p 80:80 \
  --link erp-backend:backend \
  erp-frontend:latest
```

---

## 🌐 Nginx Reverse Proxy (Recommended)

### Install Nginx

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

### Configure Nginx

Create `/etc/nginx/sites-available/erp`:

```nginx
# API Backend
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/erp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Setup SSL with Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

---

## 🗄️ Database Setup

### Initialize Database

```bash
# Run migrations (first time)
docker-compose -f docker-compose.prod.yml exec backend python scripts/seed_db.py
```

### Backup Database

```bash
# Manual backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U erp_user erp_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U erp_user erp_db < backup.sql
```

### Automated Backups (Cron)

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * docker-compose -f /path/to/docker-compose.prod.yml exec -T db pg_dump -U erp_user erp_db | gzip > /backups/erp_$(date +\%Y\%m\%d).sql.gz
```

---

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban (Brute Force Protection)

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Rate Limiting

Rate limiting is built-in via slowapi (already configured).

### 4. Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 Monitoring

### Health Checks

```bash
# API health
curl https://api.yourdomain.com/api/v1/healthz

# Database health
curl https://api.yourdomain.com/api/v1/healthz/db
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Backend only
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Application Logs

```bash
# Backend logs
docker-compose -f docker-compose.prod.yml exec backend ls -lh logs/

# View app log
docker-compose -f docker-compose.prod.yml exec backend tail -f logs/app.log

# View error log
docker-compose -f docker-compose.prod.yml exec backend tail -f logs/error.log
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose -f docker-compose.prod.yml build

# Restart services (zero-downtime)
docker-compose -f docker-compose.prod.yml up -d

# Clean old images
docker image prune -f
```

### Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Rollback migration
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Check configuration
docker-compose -f docker-compose.prod.yml config

# Restart service
docker-compose -f docker-compose.prod.yml restart backend
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps db

# Test database connection
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.core.database import check_db_connection; print(check_db_connection())"
```

### High CPU/Memory Usage

```bash
# Check resource usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

---

## 📈 Performance Optimization

### Database Connection Pooling

Already configured in `backend/app/core/database.py`:
- Pool size: 20 connections
- Max overflow: 10 connections
- Connection recycling: 1 hour

### Caching (Optional)

Add Redis for caching:

```yaml
# In docker-compose.prod.yml
redis:
  image: redis:7-alpine
  restart: unless-stopped
  volumes:
    - redis_data:/data
```

---

## 📝 Post-Deployment Checklist

- [ ] All services running (`docker-compose ps`)
- [ ] Health checks passing
- [ ] SSL certificate installed
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] Firewall configured
- [ ] Admin account created
- [ ] DNS configured correctly
- [ ] CORS origins updated
- [ ] Logs directory created and writable
- [ ] Email notifications tested (if configured)
- [ ] Rate limiting tested
- [ ] Security headers verified

---

## 🔗 Useful Commands

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (CAUTION: Deletes data!)
docker-compose -f docker-compose.prod.yml down -v

# View resource usage
docker-compose -f docker-compose.prod.yml top

# Execute command in container
docker-compose -f docker-compose.prod.yml exec backend bash

# View container details
docker-compose -f docker-compose.prod.yml exec backend env
```

---

## 📞 Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify configuration
3. Review this guide
4. Check application health endpoints
5. Open an issue on GitHub

---

**🎉 Congratulations!** Your Multi-Tenant ERP Platform is now deployed in production.
