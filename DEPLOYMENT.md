# Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Ubuntu/Debian server (or compatible)
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Redis (optional)
- Domain name (for HTTPS)

### Step 1: Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3.11 python3.11-venv python3-pip \
  postgresql postgresql-contrib nginx redis-server git

# Create deploy user
sudo useradd -m -s /bin/bash deploy
sudo su - deploy
```

### Step 2: Clone Repository

```bash
cd /home/deploy
git clone <your-repo-url> ecommerce
cd ecommerce
```

### Step 3: Setup Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
# Edit with production settings
sudo nano .env
```

Key production settings:
```env
DEBUG=False
SECRET_KEY=generate-a-strong-random-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Step 5: Setup Database

```bash
# Create PostgreSQL database
sudo -u postgres createdb ecommerce
sudo -u postgres createuser ecommerce_user
sudo -u postgres psql -c "ALTER USER ecommerce_user WITH PASSWORD 'strong_password';"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Create sample data (optional)
python manage.py create_sample_data
```

### Step 6: Configure Gunicorn

Create `/home/deploy/ecommerce/gunicorn.conf.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
daemon = False
```

Create systemd service `/etc/systemd/system/ecommerce.service`:

```ini
[Unit]
Description=E-Commerce Gunicorn Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/ecommerce
Environment="PATH=/home/deploy/ecommerce/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=/home/deploy/ecommerce/venv/bin/gunicorn \
  --config /home/deploy/ecommerce/gunicorn.conf.py \
  config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ecommerce
sudo systemctl start ecommerce
```

### Step 7: Configure Nginx

Create `/etc/nginx/sites-available/ecommerce`:

```nginx
upstream ecommerce_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificates (get from Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    client_max_body_size 20M;
    
    location /static/ {
        alias /home/deploy/ecommerce/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/deploy/ecommerce/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://ecommerce_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: Setup SSL Certificate

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Step 9: Configure Backups

Create backup script `/home/deploy/ecommerce/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_BACKUP="$BACKUP_DIR/db_$DATE.sql"
MEDIA_BACKUP="$BACKUP_DIR/media_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump ecommerce > $DB_BACKUP
gzip $DB_BACKUP

# Backup media files
tar -czf $MEDIA_BACKUP /home/deploy/ecommerce/media/

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $DATE"
```

Setup cron job:
```bash
crontab -e
# Add: 0 2 * * * /home/deploy/ecommerce/backup.sh
```

### Step 10: Monitoring

Install monitoring tools:
```bash
sudo apt-get install -y htop iotop nethogs

# Monitor application
tail -f /var/log/syslog | grep ecommerce
```

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Set DEBUG=False in production
- [ ] Configure SECRET_KEY with a strong random value
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Setup secure database connection
- [ ] Enable firewall (UFW)
- [ ] Regular security updates
- [ ] Setup error logging and monitoring
- [ ] Configure backup strategy
- [ ] Regular security audits

## 📊 Performance Optimization

```bash
# Postgresql optimization
sudo -u postgres psql ecommerce
# Add indexes and optimize queries

# Redis caching
redis-cli
> INFO

# Monitor application
docker stats
systemctl status ecommerce
```

## 🆘 Troubleshooting

### Gunicorn not starting
```bash
journalctl -u ecommerce -n 50
```

### Nginx connection refused
```bash
curl http://127.0.0.1:8000
```

### Database connection error
```bash
psql -U ecommerce_user -d ecommerce -c "SELECT 1"
```

## 📚 Additional Resources

- Gunicorn: https://gunicorn.org/
- Nginx: https://nginx.org/
- PostgreSQL: https://www.postgresql.org/
- Certbot: https://certbot.eff.org/

---

**Deployment complete!** 🎉
