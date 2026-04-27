#!/bin/bash

# OpSell Market Direction Classifier - EC2 Automated Deployment Script
# Run this on your EC2 instance: bash deploy.sh

set -e

echo "🚀 Starting Market Direction Classifier deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
APP_DIR="/opt/opsell"
LOG_DIR="/var/log/opsell"
SERVICE_NAME="opsell-direction"
VENV_PATH="$APP_DIR/venv"

echo -e "${YELLOW}Step 1: Update system packages...${NC}"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx curl

echo -e "${YELLOW}Step 2: Create application directory...${NC}"
sudo mkdir -p "$APP_DIR"
sudo mkdir -p "$LOG_DIR"
sudo chown -R ubuntu:ubuntu "$APP_DIR"
sudo chown -R ubuntu:ubuntu "$LOG_DIR"
sudo chmod 755 "$APP_DIR"
sudo chmod 755 "$LOG_DIR"

echo -e "${YELLOW}Step 3: Clone/copy application files...${NC}"
# If you need to clone from git:
# cd "$APP_DIR" && git clone <your-repo-url> . && cd -
# Otherwise, files should already be copied via SCP or CodeDeploy

echo -e "${YELLOW}Step 4: Create Python virtual environment...${NC}"
cd "$APP_DIR"
python3.11 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

echo -e "${YELLOW}Step 5: Install Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo -e "${YELLOW}Step 6: Set up environment file...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "Created .env file. Please review and adjust if needed."
fi

echo -e "${YELLOW}Step 7: Copy systemd service file...${NC}"
sudo cp "$APP_DIR/opsell-direction.service" "/etc/systemd/system/${SERVICE_NAME}.service"
sudo systemctl daemon-reload

echo -e "${YELLOW}Step 8: Enable and start service...${NC}"
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl start "${SERVICE_NAME}.service"

echo -e "${YELLOW}Step 9: Configure Nginx...${NC}"
# Create Nginx config
sudo tee /etc/nginx/sites-available/opsell > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/opsell /etc/nginx/sites-enabled/opsell
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo -e "${YELLOW}Step 10: Configure firewall...${NC}"
sudo ufw allow 22/tcp 2>/dev/null || true
sudo ufw allow 80/tcp 2>/dev/null || true
sudo ufw allow 443/tcp 2>/dev/null || true
# Enable UFW if not already enabled
sudo ufw --force enable 2>/dev/null || true

echo -e "${YELLOW}Step 11: Verify deployment...${NC}"
sleep 3

# Check if service is running
if sudo systemctl is-active --quiet "${SERVICE_NAME}.service"; then
    echo -e "${GREEN}✓ Service is running${NC}"
else
    echo -e "${RED}✗ Service is not running${NC}"
    sudo systemctl status "${SERVICE_NAME}.service"
    exit 1
fi

# Test health endpoint
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HEALTH_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Health check returned status $HEALTH_RESPONSE${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Service Details:"
echo "  Service Name: $SERVICE_NAME"
echo "  Service Status: $(sudo systemctl is-active $SERVICE_NAME.service)"
echo "  App Directory: $APP_DIR"
echo "  Log Directory: $LOG_DIR"
echo ""
echo "Useful Commands:"
echo "  Status: sudo systemctl status $SERVICE_NAME.service"
echo "  Logs: sudo journalctl -u $SERVICE_NAME.service -f"
echo "  Restart: sudo systemctl restart $SERVICE_NAME.service"
echo "  Stop: sudo systemctl stop $SERVICE_NAME.service"
echo ""
echo "Access the API:"
echo "  Health: http://$(hostname -I | awk '{print $1}'):8000/health"
echo "  API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "  ReDoc: http://$(hostname -I | awk '{print $1}'):8000/redoc"
echo ""
echo "Next Steps:"
echo "  1. Configure your domain name"
echo "  2. Set up SSL certificate with Let's Encrypt"
echo "  3. Configure AWS Security Groups"
echo "  4. Set up CloudWatch monitoring"
echo ""
