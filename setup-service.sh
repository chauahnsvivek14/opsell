#!/bin/bash

# OpSell Market Direction Classifier - Quick Service Setup
# Run this on EC2 after files are in place: bash setup-service.sh
# This assumes deploy.sh has already run OR you're manually setting up

set -e

APP_DIR="/opt/opsell"
VENV_PATH="$APP_DIR/venv"
LOG_DIR="/var/log/opsell"
SERVICE_NAME="opsell-direction"

echo "🔧 Starting service setup..."

# Check if already running
if sudo systemctl is-active --quiet "$SERVICE_NAME.service" 2>/dev/null; then
    echo "ℹ Service is already running. Skipping setup."
    exit 0
fi

echo "📦 Creating Python virtual environment..."
cd "$APP_DIR"

if [ ! -d "$VENV_PATH" ]; then
    python3.11 -m venv "$VENV_PATH"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo "📥 Installing dependencies..."
source "$VENV_PATH/bin/activate"
pip install --upgrade pip setuptools wheel --quiet
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

echo "📂 Setting up directories..."
sudo mkdir -p "$LOG_DIR"
sudo chown ubuntu:ubuntu "$LOG_DIR"
echo "✓ Log directory configured"

echo "⚙️  Setting up systemd service..."
sudo cp "$APP_DIR/opsell-direction.service" "/etc/systemd/system/$SERVICE_NAME.service"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME.service"
echo "✓ Service enabled"

echo "🚀 Starting service..."
sudo systemctl start "$SERVICE_NAME.service"
sleep 2

if sudo systemctl is-active --quiet "$SERVICE_NAME.service"; then
    echo "✓ Service is running"
else
    echo "✗ Service failed to start"
    sudo systemctl status "$SERVICE_NAME.service"
    echo ""
    echo "Checking logs..."
    sudo journalctl -u "$SERVICE_NAME.service" -n 20
    exit 1
fi

echo ""
echo "✓ Service setup complete!"
echo ""
echo "Check status: sudo systemctl status $SERVICE_NAME.service"
echo "View logs: sudo journalctl -u $SERVICE_NAME.service -f"
