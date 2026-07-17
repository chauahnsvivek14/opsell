import os
import socket
import threading
import time
import webbrowser
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


def find_free_port(start_port=8000):
    for port in range(start_port, start_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port available")


def start_callback_server(preferred_redirect_uri):
    parsed = urlparse(preferred_redirect_uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8000

    try:
        server = ThreadingHTTPServer((host, port), OAuthCallbackHandler)
    except OSError:
        port = find_free_port(port + 1)
        server = ThreadingHTTPServer((host, port), OAuthCallbackHandler)

    server.redirect_uri = f"http://{host}:{server.server_address[1]}"
    return server


def wait_for_auth_code(server, auth_url):
    server.auth_code = ""
    server.received_code = False

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print(f"Using redirect URI: {server.redirect_uri}")
    print(auth_url)
    webbrowser.open(auth_url, new=1)

    deadline = time.time() + 120
    while time.time() < deadline:
        if server.received_code:
            return server.auth_code, server.redirect_uri
        time.sleep(0.5)

    raise TimeoutError("Timed out waiting for the Fyers redirect.")


preferred_redirect_uri = os.getenv("FYERS_REDIRECT_URI", "http://127.0.0.1:8000")
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
auth_code, actual_redirect_uri = wait_for_auth_code(server, generateTokenUrl)

print(f"Captured auth code from redirect URI: {actual_redirect_uri}")
appSession.set_token(auth_code)
response = appSession.generate_token()

if response.get("s") != "ok":
    raise RuntimeError(f"Fyers token request failed: {response}")

print("Access token received successfully.")
print(response)