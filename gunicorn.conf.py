# Gunicorn Configuration for Market Direction Classifier

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 2

# Server mechanics
daemon = False
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = "/var/log/opsell/access.log"
errorlog = "/var/log/opsell/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "market-direction-classifier"

# SSL (enable if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
# ca_certs = "/path/to/ca_certs"

# Hook for graceful shutdown
def when_ready(server):
    print("Gunicorn server is ready. Spawning workers")

def on_exit(server):
    print("Gunicorn server shutting down")
