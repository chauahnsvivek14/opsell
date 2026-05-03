# EC2 Deployment Guide - Market Direction Classifier Microservice

## Prerequisites
- EC2 instance running Ubuntu 20.04 LTS or later
- SSH access to the instance
- Basic familiarity with Linux and systemd

## Step 1: Initial Setup on EC2 Instance

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx

# Create application directory
sudo mkdir -p /opt/opsell
sudo chown -R ubuntu:ubuntu /opt/opsell

# Create log directory
sudo mkdir -p /var/log/opsell
sudo chown -R ubuntu:ubuntu /var/log/opsell
```

## Step 2: Deploy Application

### Option A: Automated Deployment (Recommended)
```bash
# Copy deployment script to EC2, then run:
bash /opt/opsell/deploy.sh
```

This handles everything: environment setup, dependencies, service configuration, and Nginx setup.

### Option B: Manual Deployment
```bash
# Navigate to app directory
cd /opt/opsell

# Clone or copy your application
git clone <your-repo-url> . 
# OR copy files from your local machine

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Step 3: Configure Systemd Service

### Quick Service Setup
If you've already deployed the app files but need to set up the service:
```bash
bash /opt/opsell/setup-service.sh
```

### Manual Configuration
```bash
# Copy systemd service file
sudo cp opsell-direction.service /etc/systemd/system/

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable opsell-direction.service
sudo systemctl start opsell-direction.service

# Check status
sudo systemctl status opsell-direction.service

# View logs
sudo journalctl -u opsell-direction.service -f
```

## Step 4: Configure Nginx Reverse Proxy (Optional but Recommended)

Create `/etc/nginx/sites-available/opsell`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS (optional)
    # return 301 https://$server_name$request_uri;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Enable Nginx configuration:
```bash
sudo ln -s /etc/nginx/sites-available/opsell /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 5: Enable SSL/TLS with Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com

# Update Nginx configuration to use SSL
sudo certbot --nginx -d your-domain.com

# Auto-renewal is automatic with certbot
```

## Step 6: Configure Security

### UFW Firewall
```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### AWS Security Groups
- Allow inbound on port 22 (SSH) from your IP
- Allow inbound on port 80 (HTTP) from 0.0.0.0/0
- Allow inbound on port 443 (HTTPS) from 0.0.0.0/0

## Step 7: Monitor and Maintain

### Check service status
```bash
sudo systemctl status opsell-direction.service
```

### View real-time logs
```bash
sudo journalctl -u opsell-direction.service -f
sudo tail -f /var/log/opsell/access.log
sudo tail -f /var/log/opsell/error.log
```

### Restart service
```bash
sudo systemctl restart opsell-direction.service
```

### Stop service
```bash
sudo systemctl stop opsell-direction.service
```

## Testing the Service

### Health check
```bash
curl http://your-ec2-ip:8000/health
```

### API Documentation
```
http://your-ec2-ip:8000/docs          # Swagger UI
http://your-ec2-ip:8000/redoc         # ReDoc
```

### Test classification endpoint
```bash
curl -X POST http://your-ec2-ip:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "open_price": 23945.45,
    "current_price": 24040.25,
    "vix_open": 19.3,
    "vix_now": 18.97,
    "straddle_open": 241.35,
    "straddle_now": 235.85
  }'
```

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed solutions to common issues including:
- `gunicorn: command not found` error
- Service fails to start
- Port already in use
- Permission denied errors
- Health check failures
- Module import errors
- And more...

## Performance Tuning

### Adjust workers based on CPU cores
```bash
# In opsell-direction.service
# For 2 CPUs: workers=4
# For 4 CPUs: workers=8
# For 8 CPUs: workers=16
# Generally: (2 × CPU_cores) + 1
```

### Adjust timeouts if needed
```bash
# In opsell-direction.service
# Increase timeout for slower operations
# --timeout 180
```

## Backup and Recovery

```bash
# Backup configuration
sudo tar -czf opsell-backup-$(date +%Y%m%d).tar.gz /opt/opsell /var/log/opsell

# Restore from backup
sudo tar -xzf opsell-backup-20240428.tar.gz -C /
```

## Next Steps

1. Set up CloudWatch monitoring for logs
2. Configure SNS alerts for service failures
3. Set up Auto Scaling Group for high availability
4. Implement rate limiting with AWS WAF
5. Set up Route53 for DNS and load balancing
