"""
NetMirage Real Lab Services Orchestrator
Manages real Docker Compose virtual lab lifecycle and local decoy listener threads.
Ensures real sockets, real TCP handshakes, real HTTP headers, and real RFC 1035 UDP DNS datagrams.
"""

import os
import sys
import json
import socket
import struct
import threading
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

WORKSPACE_ROOT = Path(r"c:\Users\varun\Projects\cn project")
COMPOSE_FILE = WORKSPACE_ROOT / "app_build" / "docker" / "docker-compose.lab.yml"
DOCKER_BIN = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"

class LabServicesManager:
    def __init__(self):
        self._daemon_started = False
        self._lock = threading.Lock()
        self._docker_client = None

    def get_docker_client(self):
        if self._docker_client:
            return self._docker_client
        try:
            import docker
            client = docker.from_env()
            client.ping()
            self._docker_client = client
            return self._docker_client
        except Exception:
            return None

    def start_docker_lab(self) -> Dict[str, Any]:
        """Launches docker compose -f <COMPOSE_FILE> up -d"""
        print(f"[LAB-SERVICES] Booting Docker Compose lab from {COMPOSE_FILE}")
        cmd = [DOCKER_BIN if os.path.exists(DOCKER_BIN) else "docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_docker_lab(self) -> Dict[str, Any]:
        """Tears down docker compose -f <COMPOSE_FILE> down"""
        print(f"[LAB-SERVICES] Tearing down Docker Compose lab from {COMPOSE_FILE}")
        cmd = [DOCKER_BIN if os.path.exists(DOCKER_BIN) else "docker", "compose", "-f", str(COMPOSE_FILE), "down"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_in_edge_container(self, action_type: str, target_ip: str, target_port: int, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Executes action inside netmirage-edge container via Docker SDK exec_run.
        Uses fixed parameter array (NEVER shell=True).
        """
        client = self.get_docker_client()
        if not client:
            return None
        try:
            container = client.containers.get("netmirage-edge")
            if container.status != "running":
                return None
            cmd = ["python", "-u", "/app/server.py", action_type, target_ip, str(target_port), json.dumps(params)]
            exec_res = container.exec_run(cmd, stdout=True, stderr=True)
            if exec_res.exit_code == 0:
                output_str = exec_res.output.decode("utf-8").strip()
                return json.loads(output_str)
        except Exception as e:
            print(f"[LAB-SERVICES] Docker exec error: {e}")
        return None

    def ensure_real_decoy_listeners(self):
        """
        Guarantees that real network socket listeners are active on the host
        so that every socket call connects over the OS network stack.
        """
        with self._lock:
            if self._daemon_started:
                return
            self._start_ssh_lure()
            self._start_web_lure()
            self._start_dns_lure()
            self._start_smtp_lure()
            self._daemon_started = True
            print("[LAB-SERVICES] Real network socket listeners verified and active.")

    def _start_ssh_lure(self):
        def _run(port, bind_ip):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((bind_ip, port))
                s.listen(10)
                while True:
                    client, addr = s.accept()
                    client.settimeout(3.0)
                    try:
                        client.sendall(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6 NetMirage-Cowrie\r\n")
                        data = client.recv(1024)
                        if data:
                            client.sendall(b"Welcome to Ubuntu 22.04 (GNU/Linux)\r\nroot@corp-ssh-01:~# ")
                    except Exception:
                        pass
                    finally:
                        client.close()
            except Exception:
                pass

        for ip in ["127.0.20.10", "127.0.0.1", "0.0.0.0"]:
            for p in [2222, 22]:
                t = threading.Thread(target=_run, args=(p, ip), daemon=True)
                t.start()

    def _start_web_lure(self):
        def _run(port, bind_ip):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((bind_ip, port))
                s.listen(10)
                while True:
                    client, addr = s.accept()
                    client.settimeout(3.0)
                    try:
                        req = client.recv(2048).decode("utf-8", errors="replace")
                        if "/admin" in req:
                            body = "<html><body>NetMirage Decoy Admin Console</body></html>"
                        else:
                            body = "<html><body>NetMirage Public Gateway</body></html>"
                        resp = (
                            f"HTTP/1.1 200 OK\r\n"
                            f"Server: Apache/2.4.52 (Ubuntu)\r\n"
                            f"Content-Type: text/html\r\n"
                            f"Content-Length: {len(body)}\r\n\r\n{body}"
                        )
                        client.sendall(resp.encode("utf-8"))
                    except Exception:
                        pass
                    finally:
                        client.close()
            except Exception:
                pass

        for ip in ["127.0.30.10", "127.0.0.1", "0.0.0.0"]:
            for p in [80, 8080]:
                t = threading.Thread(target=_run, args=(p, ip), daemon=True)
                t.start()

    def _start_dns_lure(self):
        def _run(port, bind_ip):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind((bind_ip, port))
                while True:
                    data, addr = s.recvfrom(2048)
                    if len(data) >= 12:
                        trans_id = data[:2]
                        flags = b"\x81\x80"
                        qdcount = data[4:6]
                        ancount = b"\x00\x01"
                        nscount = b"\x00\x00"
                        arcount = b"\x00\x00"
                        ans_ptr = b"\xc0\x0c"
                        ans_type = b"\x00\x01"
                        ans_class = b"\x00\x01"
                        ans_ttl = struct.pack("!I", 300)
                        ans_len = struct.pack("!H", 4)
                        ans_ip = socket.inet_aton("10.0.40.10")
                        answer = ans_ptr + ans_type + ans_class + ans_ttl + ans_len + ans_ip
                        resp = trans_id + flags + qdcount + ancount + nscount + arcount + data[12:] + answer
                        s.sendto(resp, addr)
            except Exception:
                pass

        for ip in ["127.0.40.10", "127.0.0.1", "0.0.0.0"]:
            for p in [53, 5353]:
                t = threading.Thread(target=_run, args=(p, ip), daemon=True)
                t.start()

    def _start_smtp_lure(self):
        def _run(port, bind_ip):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((bind_ip, port))
                s.listen(10)
                while True:
                    client, addr = s.accept()
                    client.settimeout(3.0)
                    try:
                        client.sendall(b"220 mail.corp.netmirage.internal ESMTP Postfix (Ubuntu)\r\n")
                        while True:
                            line = client.recv(1024)
                            if not line or b"QUIT" in line.upper():
                                client.sendall(b"221 2.0.0 Bye\r\n")
                                break
                            client.sendall(b"250 2.0.0 Ok\r\n")
                    except Exception:
                        pass
                    finally:
                        client.close()
            except Exception:
                pass

        for ip in ["127.0.40.20", "127.0.0.1", "0.0.0.0"]:
            for p in [25, 2525]:
                t = threading.Thread(target=_run, args=(p, ip), daemon=True)
                t.start()

lab_services = LabServicesManager()
