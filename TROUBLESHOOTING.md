# Troubleshooting Guide - OpSell Market Direction Classifier

## Common Issues and Solutions

### Issue 1: `gunicorn: command not found` or `203/EXEC` error

**Symptom:**
```
Error: cannot access '/opt/opsell/venv/bin/gunicorn': No such file or directory
```

**Cause:** Python virtual environment not set up or dependencies not installed.

**Solution:**
```bash
cd /opt/opsell
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
sudo systemctl restart opsell-direction.service
```

Or use the setup script:
```bash
bash setup-service.sh
```

---

### Issue 2: Service fails to start with "Permission denied"

**Symptom:**
```
Failed with result 'exit-code'
```

**Cause:** Incorrect file permissions or ownership.

**Solution:**
```bash
sudo chown -R ubuntu:ubuntu /opt/opsell
sudo chown -R ubuntu:ubuntu /var/log/opsell
sudo chmod 755 /opt/opsell
sudo chmod 755 /var/log/opsell
sudo systemctl restart opsell-direction.service
```

---

### Issue 3: Port 8000 already in use

**Symptom:**
```
Address already in use
```

**Cause:** Another process is using port 8000.

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process (replace PID with actual process ID)
sudo kill -9 <PID>

# Or change the port in opsell-direction.service
sudo nano /etc/systemd/system/opsell-direction.service
# Change --bind 0.0.0.0:8000 to --bind 0.0.0.0:8001
sudo systemctl daemon-reload
sudo systemctl restart opsell-direction.service
```

---

### Issue 4: Service runs but health check fails

**Symptom:**
```bash
curl http://localhost:8000/health
# Returns: Connection refused or timeout
```

**Cause:** 
- Service might be crashing
- Nginx proxy not configured
- Firewall blocking connections

**Solution:**

1. Check service logs:
```bash
sudo journalctl -u opsell-direction.service -n 50
```

2. Check if service is actually running:
```bash
sudo systemctl status opsell-direction.service
ps aux | grep gunicorn
```

3. Check if port is listening:
```bash
sudo netstat -tlnp | grep 8000
# or
sudo ss -tlnp | grep 8000
```

4. If service crashed, check error logs:
```bash
cat /var/log/opsell/error.log
tail -f /var/log/opsell/error.log
```

---

### Issue 5: Module not found errors (e.g., `services.direction`)

**Symptom:**
```
ModuleNotFoundError: No module named 'services'
```

**Cause:** 
- Working directory not set correctly
- PYTHONPATH not configured
- Missing `__init__.py` files

**Solution:**

1. Verify folder structure:
```bash
ls -la /opt/opsell/
# Should see: services/ requirements.txt api.py opsell-direction.service etc.

ls -la /opt/opsell/services/
# Should see: __init__.py direction.py
```

2. Check PYTHONPATH in service file:
```bash
sudo cat /etc/systemd/system/opsell-direction.service | grep PYTHONPATH
# Should show: Environment="PYTHONPATH=/opt/opsell"
```

3. Verify `__init__.py` exists:
```bash
touch /opt/opsell/services/__init__.py
sudo systemctl restart opsell-direction.service
```

---

### Issue 6: OutOfMemory or high CPU usage

**Symptom:**
- Service gets killed unexpectedly
- High CPU utilization

**Solution:**

1. Reduce number of workers:
```bash
sudo nano /etc/systemd/system/opsell-direction.service
# Change --workers 4 to --workers 2
sudo systemctl daemon-reload
sudo systemctl restart opsell-direction.service
```

2. Monitor resource usage:
```bash
top
# Press 'q' to quit
```

3. Check logs for errors:
```bash
sudo journalctl -u opsell-direction.service -f --lines=50
```

---

### Issue 7: Nginx returns 502 Bad Gateway

**Symptom:**
```
502 Bad Gateway
```

**Cause:** Nginx cannot connect to Gunicorn on 127.0.0.1:8000

**Solution:**

1. Verify Gunicorn is listening:
```bash
sudo netstat -tlnp | grep 8000
```

2. Check Nginx configuration:
```bash
sudo nginx -t
# Should return: successful
```

3. Test direct connection to Gunicorn:
```bash
curl http://127.0.0.1:8000/health
```

4. Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
```

---

### Issue 8: Logs not appearing or permission issues

**Symptom:**
```
/var/log/opsell/access.log: Permission denied
```

**Cause:** Log directory not owned by ubuntu user.

**Solution:**
```bash
sudo mkdir -p /var/log/opsell
sudo chown ubuntu:ubuntu /var/log/opsell
sudo chmod 755 /var/log/opsell
sudo systemctl restart opsell-direction.service
```

---

## Diagnostic Commands

### Quick Health Check
```bash
#!/bin/bash
echo "=== Service Status ==="
sudo systemctl status opsell-direction.service

echo -e "\n=== Process Check ==="
ps aux | grep gunicorn | grep -v grep

echo -e "\n=== Port Check ==="
sudo netstat -tlnp | grep 8000 || echo "Not listening on 8000"

echo -e "\n=== Health Endpoint ==="
curl -s http://localhost:8000/health || echo "Health check failed"

echo -e "\n=== Recent Logs ==="
sudo journalctl -u opsell-direction.service -n 5
```

### Full System Check
```bash
# Run all diagnostics
cat > /tmp/diagnose.sh << 'EOF'
echo "System Information"
echo "==================="
uname -a
df -h
free -h

echo -e "\n\nPython Setup"
echo "============"
which python3.11
python3.11 --version
ls -la /opt/opsell/venv/bin/python*

echo -e "\n\nService Check"
echo "============="
sudo systemctl status opsell-direction.service
ps aux | grep gunicorn | grep -v grep

echo -e "\n\nNetwork Check"
echo "============="
sudo netstat -tlnp | grep 8000
curl -i http://localhost:8000/health

echo -e "\n\nLog Check"
echo "=========="
sudo tail -20 /var/log/opsell/error.log
sudo tail -20 /var/log/opsell/access.log

echo -e "\n\nRecent Errors"
echo "============="
sudo journalctl -u opsell-direction.service -n 20
EOF

bash /tmp/diagnose.sh
```

---

## Recovery Procedures

### Complete Service Reset
```bash
# Stop service
sudo systemctl stop opsell-direction.service

# Remove old venv
rm -rf /opt/opsell/venv

# Run setup
bash /opt/opsell/setup-service.sh

# Verify
sudo systemctl status opsell-direction.service
curl http://localhost:8000/health
```

### Manual Service Start (for debugging)
```bash
cd /opt/opsell
source venv/bin/activate
gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    services.direction:app
```

---

## Getting Help

1. Check service logs:
   ```bash
   sudo journalctl -u opsell-direction.service -f
   ```

2. Check application logs:
   ```bash
   tail -f /var/log/opsell/error.log
   tail -f /var/log/opsell/access.log
   ```

3. Test endpoint directly:
   ```bash
   curl -v http://localhost:8000/health
   ```

4. Check EC2 Security Groups allow port 8000 or 80/443
