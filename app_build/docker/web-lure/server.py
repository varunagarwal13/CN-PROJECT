"""
NetMirage Real Web Decoy Lure Server
Listens on TCP 80 and TCP 8080.
Emulates Apache/2.4.52 (Ubuntu) administrative portal.
Logs HTTP request paths, methods, and credentials to /tmp/web_requests.jsonl
"""

import http.server
import socketserver
import threading
import json
import time
from datetime import datetime, timezone

REQUESTS_LOG = "/tmp/web_requests.jsonl"

def log_request(method: str, path: str, client_ip: str, headers: dict, body: str = ""):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "client_ip": client_ip,
        "headers": headers,
        "body_preview": body[:200]
    }
    try:
        with open(REQUESTS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[WEB-LURE] Log error: {e}")

class WebLureHandler(http.server.BaseHTTPRequestHandler):
    server_version = "Apache/2.4.52 (Ubuntu)"
    sys_version = ""

    def log_message(self, format, *args):
        print(f"[WEB-LURE] {self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}")

    def do_GET(self):
        client_ip = self.client_address[0]
        header_dict = {k: v for k, v in self.headers.items()}
        log_request("GET", self.path, client_ip, header_dict)

        if self.path in ("/admin", "/admin/login", "/login"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", self.server_version)
            self.end_headers()
            html = (
                "<!DOCTYPE html><html><head><title>NetMirage Administrative Console</title></head>"
                "<body style='font-family: monospace; background: #FAF5E9; color: #111827; padding: 2rem;'>"
                "<h2>NETMIRAGE SECURE ADMIN PORTAL v1.4</h2>"
                "<p>Restricted Corporate Access. All activity is logged.</p>"
                "<form method='POST' action='/admin/login'>"
                "<div><label>Username: </label><input type='text' name='username'/></div>"
                "<div style='margin-top: 10px;'><label>Password: </label><input type='password' name='password'/></div>"
                "<div style='margin-top: 10px;'><button type='submit'>Authenticate</button></div>"
                "</form></body></html>"
            )
            self.wfile.write(html.encode("utf-8"))
        elif self.path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", self.server_version)
            self.end_headers()
            resp = json.dumps({"status": "ok", "service": "web-lure", "host": "portal.web.internal"})
            self.wfile.write(resp.encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", self.server_version)
            self.end_headers()
            html = (
                "<!DOCTYPE html><html><head><title>NetMirage Public Gateway</title></head>"
                "<body style='font-family: sans-serif; background: #FAF5E9; color: #111827; padding: 2rem;'>"
                "<h1>NetMirage Enterprise Infrastructure Gateway</h1>"
                "<p>Edge perimeter node operational. Routing to registered lab services.</p>"
                "</body></html>"
            )
            self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        client_ip = self.client_address[0]
        header_dict = {k: v for k, v in self.headers.items()}
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8", errors="replace") if content_len > 0 else ""

        log_request("POST", self.path, client_ip, header_dict, body)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Server", self.server_version)
        self.end_headers()
        resp = json.dumps({"status": "auth_recorded", "message": "Credential probe received by decoy portal"})
        self.wfile.write(resp.encode("utf-8"))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def start_http_listener(port: int):
    try:
        server = ThreadedHTTPServer(("0.0.0.0", port), WebLureHandler)
        print(f"[WEB-LURE] Listening on TCP 0.0.0.0:{port} (Apache Decoy)")
        server.serve_forever()
    except Exception as e:
        print(f"[WEB-LURE] Server error on {port}: {e}")

def main():
    print("[WEB-LURE] Initializing NetMirage Web Decoy Lure...")
    t80 = threading.Thread(target=start_http_listener, args=(80,), daemon=True)
    t8080 = threading.Thread(target=start_http_listener, args=(8080,), daemon=True)
    t80.start()
    t8080.start()
    t80.join()
    t8080.join()

if __name__ == "__main__":
    main()
