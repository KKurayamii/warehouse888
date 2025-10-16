# Smart Sales Analytics - Deployment Guide

This guide provides step-by-step instructions for deploying the Smart Sales Analytics system to production.

## Prerequisites

- Python 3.10+
- ClickHouse Server
- Node.js 16+ (for Tailwind CSS)
- OpenAI API Key
- Production web server (Gunicorn, Nginx)

## Step 1: Server Setup

### 1.1 Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.10 python3-pip python3-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Nginx
sudo apt install nginx

# Install ClickHouse
sudo apt-get install -y apt-transport-https ca-certificates dirmngr
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754
echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt-get update
sudo apt-get install -y clickhouse-server clickhouse-client

# Start ClickHouse
sudo service clickhouse-server start
```

## Step 2: Application Setup

### 2.1 Clone and Setup Project

```bash
# Create application directory
sudo mkdir -p /var/www/smart-sales-analytics
cd /var/www/smart-sales-analytics

# Upload your code (via git, scp, etc.)
# git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn
```

### 2.2 Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Set the following in `.env`:

```bash
SECRET_KEY=<generate-secure-random-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

OPENAI_API_KEY=sk-...

CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=<your-password>
CLICKHOUSE_DATABASE=sales_analytics

MAX_UPLOAD_SIZE=10485760
```

### 2.3 Build Static Files

```bash
# Install Node dependencies
npm install

# Build Tailwind CSS
npm run build:css

# Collect Django static files
python manage.py collectstatic --no-input
```

## Step 3: Database Setup

### 3.1 Configure ClickHouse

```bash
# Set password for default user
clickhouse-client
```

In ClickHouse client:

```sql
ALTER USER default IDENTIFIED BY 'your-secure-password';
EXIT;
```

### 3.2 Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Setup ClickHouse tables
python manage.py setup_clickhouse
```

## Step 4: Configure Gunicorn

Create `/etc/systemd/system/smart-sales-analytics.service`:

```ini
[Unit]
Description=Smart Sales Analytics Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/smart-sales-analytics
Environment="PATH=/var/www/smart-sales-analytics/venv/bin"
ExecStart=/var/www/smart-sales-analytics/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/smart-sales-analytics/gunicorn.sock \
    --timeout 300 \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start Gunicorn:

```bash
sudo systemctl daemon-reload
sudo systemctl start smart-sales-analytics
sudo systemctl enable smart-sales-analytics
sudo systemctl status smart-sales-analytics
```

## Step 5: Configure Nginx

Create `/etc/nginx/sites-available/smart-sales-analytics`:

```nginx
upstream smart_sales_analytics {
    server unix:/var/www/smart-sales-analytics/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/smart-sales-analytics/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/smart-sales-analytics/media/;
    }

    location / {
        proxy_pass http://smart_sales_analytics;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_read_timeout 300s;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/smart-sales-analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 6: SSL Certificate (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Step 7: Monitoring & Maintenance

### 7.1 Log Files

- Application logs: `/var/log/smart-sales-analytics/`
- Nginx logs: `/var/log/nginx/`
- ClickHouse logs: `/var/log/clickhouse-server/`

### 7.2 Backup Strategy

```bash
# Backup ClickHouse data
clickhouse-client --query="BACKUP DATABASE sales_analytics TO '/backups/sales_analytics_$(date +%Y%m%d).zip'"

# Backup uploaded files
tar -czf /backups/media_$(date +%Y%m%d).tar.gz /var/www/smart-sales-analytics/media/
```

### 7.3 Monitoring Commands

```bash
# Check application status
sudo systemctl status smart-sales-analytics

# Check logs
sudo journalctl -u smart-sales-analytics -f

# Check ClickHouse status
sudo service clickhouse-server status

# Monitor resource usage
htop
```

## Step 8: Performance Optimization

### 8.1 ClickHouse Optimization

Edit `/etc/clickhouse-server/config.xml`:

```xml
<max_memory_usage>10000000000</max_memory_usage>
<max_concurrent_queries>100</max_concurrent_queries>
```

### 8.2 Django Optimization

In `settings.py`:

```python
# Enable caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Database connection pooling
# Already handled by ClickHouse driver
```

## Troubleshooting

### Issue: Gunicorn won't start

```bash
# Check logs
sudo journalctl -u smart-sales-analytics -n 50

# Verify socket permissions
sudo chown www-data:www-data /var/www/smart-sales-analytics/gunicorn.sock
```

### Issue: Static files not loading

```bash
# Rebuild static files
python manage.py collectstatic --clear --no-input

# Check Nginx configuration
sudo nginx -t
```

### Issue: ClickHouse connection failed

```bash
# Test connection
clickhouse-client

# Check if service is running
sudo service clickhouse-server status

# Restart if needed
sudo service clickhouse-server restart
```

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY generated
- [ ] ClickHouse password set
- [ ] Firewall configured (UFW)
- [ ] SSL certificate installed
- [ ] Regular backups scheduled
- [ ] Log rotation configured
- [ ] OpenAI API key secured

## Maintenance Tasks

### Weekly
- Check disk space
- Review error logs
- Verify backups

### Monthly
- Update dependencies
- Review security patches
- Optimize database
- Clean old logs

## Support

For issues, check:
1. Application logs
2. Nginx logs
3. ClickHouse logs
4. System resource usage

Contact: [your-support-email]
