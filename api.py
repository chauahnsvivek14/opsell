import os
import threading
import time
import webbrowser
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from fyers_apiv3 import fyersModel

client_id = os.getenv("FYERS_CLIENT_ID", "7ASRZNCBRY-100")
secret_key = os.getenv("FYERS_SECRET_KEY", "80C9W7CV4S")
grant_type = "authorization_code"
response_type = "code"
state = "sample"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        code = parse_qs(parsed.query).get("code", [""])[0]
        self.server.auth_code = code
        self.server.received_code = True
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Authorization complete. You can close this window.")

    def log_message(self, format, *args):
        return


def get_public_ip():
    try:
        return urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode().strip()
    except Exception:
        return "127.0.0.1"


def start_callback_server(preferred_redirect_uri):
    parsed = urlparse(preferred_redirect_uri)
    host = parsed.hostname or "0.0.0.0"
    port = parsed.port or 8001

    server = ThreadingHTTPServer(("0.0.0.0", port), OAuthCallbackHandler)
    server.redirect_uri = preferred_redirect_uri
    return server


def wait_for_auth_code(server, auth_url):
    server.auth_code = ""
    server.received_code = False

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print(f"Using redirect URI: {server.redirect_uri}")
    print(auth_url)

    try:
        webbrowser.open(auth_url, new=1)
    except Exception:
        pass

    deadline = time.time() + 180
    while time.time() < deadline:
        if server.received_code:
            return server.auth_code
        time.sleep(0.5)

    raise TimeoutError("Timed out waiting for the Fyers redirect.")


public_ip = get_public_ip()
preferred_redirect_uri = os.getenv("FYERS_REDIRECT_URI", f"http://{public_ip}:8001")
server = start_callback_server(preferred_redirect_uri)

appSession = fyersModel.SessionModel(
    client_id=client_id,
    redirect_uri=server.redirect_uri,
    response_type=response_type,
    state=state,
    secret_key=secret_key,
    grant_type=grant_type,
)

generateTokenUrl = appSession.generate_authcode()
auth_code = wait_for_auth_code(server, generateTokenUrl)

print(f"Captured auth code: {auth_code}")

response = fyersModel.request_access_token(
    auth_code=auth_code,
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=server.redirect_uri,
)

print(response)