# Market Direction Classifier - Quick Start Guide

## Overview
This is a production-ready FastAPI microservice for classifying market conditions. It can be deployed on EC2 with multiple options.

## 📋 Prerequisites
- Python 3.11+ (for direct deployment)
- Docker & Docker Compose (for containerized deployment)
- Ubuntu 20.04 LTS or later (for EC2)
- Git

## 🚀 Quick Start Options

### Option 1: Direct EC2 Deployment (Recommended for simplicity)

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Download and run the automated deployment script
curl -O https://raw.githubusercontent.com/your-repo/deploy.sh
chmod +x deploy.sh
./deploy.sh

# The service will be running on http://your-ec2-ip:8000
```

Or manual setup:
```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Run commands from EC2_DEPLOYMENT.md Steps 1-7
```

### Option 2: Docker Deployment (Most portable)

**Locally or on EC2:**

```bash
# Clone/download the repository
cd /opt/opsell

# Build the Docker image
docker build -t market-direction-classifier:latest .

# Run the container
docker run -d \
  --name market-direction \
  -p 8000:8000 \
  -v $(pwd)/logs:/var/log/opsell \
  -e SERVICE_WORKERS=4 \
  market-direction-classifier:latest

# Or use Docker Compose
docker-compose up -d

# View logs
docker logs -f market-direction
```

### Option 3: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python services/direction.py

# Or with auto-reload
uvicorn services.direction:app --reload --host 0.0.0.0 --port 8000
```

## 📊 API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Get API Documentation
```
http://localhost:8000/docs           # Swagger UI (interactive)
http://localhost:8000/redoc          # ReDoc (alternative view)
```

### Classify Market Conditions
```bash
curl -X POST http://localhost:8000/classify \
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

Response:
```json
{
  "classification": "🟢 OPTION SELLER DAY (Range + Decay)",
  "price_move_pct": 0.4,
  "vix_change": -0.33,
  "premium_change_pct": -2.26,
  "timestamp": "2024-04-28T10:30:45.123456"
}
```

## 🛠️ File Structure

```
OpSell/
├── services/
│   └── direction.py              # FastAPI microservice
├── requirements.txt              # Python dependencies
├── gunicorn.conf.py             # Gunicorn configuration
├── opsell-direction.service     # Systemd service file
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose orchestration
├── nginx.conf                   # Nginx reverse proxy config
├── .env.example                 # Environment variables template
├── deploy.sh                    # Automated deployment script
├── EC2_DEPLOYMENT.md            # Detailed EC2 setup guide
└── QUICK_START.md              # This file
```

## 🔧 Configuration

### Environment Variables
```bash
# Copy and edit
cp .env.example .env

# Key variables:
SERVICE_HOST=0.0.0.0           # Bind address
SERVICE_PORT=8000              # Service port
SERVICE_WORKERS=4              # Number of Gunicorn workers
```

### Adjust Worker Processes
```bash
# Based on CPU cores: (2 × CPU_cores) + 1
# 2 CPUs: 5 workers
# 4 CPUs: 9 workers
# 8 CPUs: 17 workers

# Edit in: opsell-direction.service or docker-compose.yml
--workers 9  # Change this value
```

## 📝 Common Commands

### Service Management (Direct Deployment)
```bash
# Check status
sudo systemctl status opsell-direction.service

# View logs
sudo journalctl -u opsell-direction.service -f

# Restart
sudo systemctl restart opsell-direction.service

# Stop
sudo systemctl stop opsell-direction.service

# Start
sudo systemctl start opsell-direction.service
```

### Docker Commands
```bash
# Build image
docker build -t market-direction:latest .

# Run container
docker run -d -p 8000:8000 market-direction:latest

# View logs
docker logs -f market-direction

# Stop container
docker stop market-direction

# Remove container
docker rm market-direction

# Using Docker Compose
docker-compose up -d          # Start all services
docker-compose logs -f        # View logs
docker-compose down           # Stop all services
```

## 🌐 Deploy to AWS

### Using EC2 Instance
1. Launch EC2 instance (Ubuntu 20.04 LTS)
2. SSH into instance
3. Run `./deploy.sh` script
4. Configure security groups (allow 80, 443, 22)
5. Point domain to EC2 elastic IP

### Using ECS (Container)
1. Push Docker image to ECR
2. Create ECS task definition
3. Deploy as ECS service
4. Configure ALB (Application Load Balancer)

### Using Elastic Beanstalk
1. Install EB CLI
2. Create Beanstalk app: `eb create`
3. Deploy: `eb deploy`
4. Configure domain/SSL

## 🔒 Security Considerations

- [ ] Enable HTTPS with SSL certificate
- [ ] Configure AWS Security Groups (restrict source IPs if needed)
- [ ] Set up firewall rules (UFW on Ubuntu)
- [ ] Use IAM roles for EC2 instances
- [ ] Enable CloudWatch logging
- [ ] Implement rate limiting
- [ ] Use VPC security best practices
- [ ] Regularly update dependencies

## 📈 Monitoring

### CloudWatch Logs
```bash
# On EC2, logs are at:
/var/log/opsell/direction_service.log
/var/log/opsell/access.log
/var/log/opsell/error.log

# View with Docker:
docker logs market-direction
```

### Health Checks
```bash
# Automated health endpoint
GET /health

# Manual test
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u opsell-direction.service -n 50 -p err
```

**Port 8000 already in use:**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

**Permission denied:**
```bash
sudo chown -R ubuntu:ubuntu /opt/opsell
sudo chmod 755 /opt/opsell
```

**Nginx connection refused:**
```bash
sudo systemctl status nginx
sudo nginx -t
```

## 📚 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Gunicorn Docs](https://gunicorn.org/)
- [Uvicorn Docs](https://www.uvicorn.org/)
- [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [Docker Documentation](https://docs.docker.com/)

## 🆘 Support

For issues or questions:
1. Check logs: `sudo journalctl -u opsell-direction.service -f`
2. Review EC2_DEPLOYMENT.md for detailed guidance
3. Check API docs at `/docs` endpoint

---

**Happy Deploying! 🚀**
