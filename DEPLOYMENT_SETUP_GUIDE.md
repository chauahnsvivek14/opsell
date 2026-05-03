# OpSell EC2 Deployment Summary

## Issue Resolved
✓ **Root Cause:** Gunicorn not found at `/opt/opsell/venv/bin/gunicorn` because the Python virtual environment and dependencies were not set up on the EC2 instance.

## Solution Provided

### 1. **setup-service.sh** (NEW)
Quick service setup script that:
- Creates Python virtual environment
- Installs all dependencies from requirements.txt
- Sets up log directories with correct permissions
- Configures and starts the systemd service
- Verifies the service is running

**Usage:**
```bash
bash setup-service.sh
```

### 2. **TROUBLESHOOTING.md** (NEW)
Comprehensive troubleshooting guide covering:
- `gunicorn: command not found` and `203/EXEC` errors
- Permission denied issues
- Port conflicts
- Service startup failures
- Module import errors
- High resource usage
- Nginx 502 Bad Gateway errors
- Diagnostic commands and recovery procedures

### 3. **Updated EC2_DEPLOYMENT.md**
- Added reference to `setup-service.sh` for quick setup
- Added reference to `TROUBLESHOOTING.md` for issue resolution
- Clarified automated vs manual deployment options

## Deployment Workflow

### Quick Deploy (Recommended)
```bash
# 1. Connect to EC2
ssh -i opsell-key.pem ubuntu@your-ec2-ip

# 2. Run automated setup (handles everything)
bash /opt/opsell/setup-service.sh

# 3. Verify
sudo systemctl status opsell-direction.service
curl http://localhost:8000/health
```

### Or Full Setup
```bash
bash /opt/opsell/deploy.sh
```

## What the Service Expects

- **App Location:** `/opt/opsell/`
- **Virtual Environment:** `/opt/opsell/venv/`
- **Log Directory:** `/var/log/opsell/`
- **Python Module:** `services.direction:app` (from `services/direction.py`)
- **Port:** 8000
- **User:** ubuntu

## Files Included

1. **deploy.sh** - Full automated deployment script (already present)
2. **setup-service.sh** - Quick service setup script (NEW)
3. **opsell-direction.service** - Systemd service file (already present)
4. **EC2_DEPLOYMENT.md** - Updated deployment guide
5. **TROUBLESHOOTING.md** - New troubleshooting guide (NEW)

## Verification Steps

After running the setup:
```bash
# Check service status
sudo systemctl status opsell-direction.service

# Check if Gunicorn is running
ps aux | grep gunicorn

# Test health endpoint
curl http://localhost:8000/health

# View logs
sudo journalctl -u opsell-direction.service -f
```

## Next Steps

1. Copy these files to your EC2 instance
2. Run `bash setup-service.sh` or `bash deploy.sh`
3. Verify with the commands above
4. Configure Nginx (included in deploy.sh) or manually with EC2_DEPLOYMENT.md
5. Set up SSL with Let's Encrypt (optional but recommended)

## Support

If you encounter any issues:
1. Check `TROUBLESHOOTING.md` for your specific error
2. Run diagnostic commands
3. Check logs with `sudo journalctl -u opsell-direction.service -f`
