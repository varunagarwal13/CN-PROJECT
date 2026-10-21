"""
NetMirage Real Telemetry Collector & Passive Network Tap
Listens on TCP 8080.
Exposes telemetry status and packet capture observations.
Logs observed packets to /tmp/telemetry_packets.jsonl
"""

import http.server
import socketserver
import threading
import json
import socket
import time
from datetime import datetime, timezone

TELEMETRY_LOG = "/tmp/telemetry_packets.jsonl"

def log_packet(src: str, dst: str, proto: str, details: dict):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": src,
        "destination": dst,
        "protocol": proto,
        "details": details
    }
    try:
        with open(TELEMETRY_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[COLLECTOR] Log error: {e}")

class TelemetryHandler(http.server.BaseHTTPRequestHandler):
    server_version = "NetMirage-Telemetry-Tap/1.0"
    sys_version = ""

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ("/health", "/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {
                "status": "active",
                "service": "netmirage-telemetry",
                "ip": "10.0.50.10",
                "listening_subnet": "10.0.50.0/24",
                "mode": "passive_collector"
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        elif self.path == "/packets":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            packets = []
            try:
                with open(TELEMETRY_LOG, "r", encoding="utf-8") as f:
                    for line in f.readlines()[-50:]:
                        if line.strip():
                            packets.append(json.loads(line))
            except Exception:
                pass
            self.wfile.write(json.dumps(packets).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def main():
    print("[COLLECTOR] Initializing NetMirage Passive Telemetry Tap on 10.0.50.10:8080...")
    try:
        server = ThreadedHTTPServer(("0.0.0.0", 8080), TelemetryHandler)
        print("[COLLECTOR] Listening on TCP 0.0.0.0:8080 (Telemetry Sensor)")
        server.serve_forever()
    except Exception as e:
        print(f"[COLLECTOR] Error starting collector: {e}")

if __name__ == "__main__":
    main()
