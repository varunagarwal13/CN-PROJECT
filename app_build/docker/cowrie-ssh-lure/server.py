"""
NetMirage Real Cowrie SSH Decoy Lure Server
Listens on TCP 22 and TCP 2222.
Exchanges real SSH-2.0 protocol identification banners.
Logs client credentials and command attempts to /tmp/cowrie_sessions.jsonl
"""

import socket
import threading
import json
import time
from datetime import datetime, timezone

SESSIONS_LOG = "/tmp/cowrie_sessions.jsonl"

def log_session(event_type: str, data: dict):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **data
    }
    try:
        with open(SESSIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[SSH-LURE] Log error: {e}")

def handle_ssh_client(client_sock: socket.socket, addr: tuple):
    client_ip, client_port = addr
    print(f"[SSH-LURE] Inbound TCP connection from {client_ip}:{client_port}")
    try:
        client_sock.settimeout(5.0)
        # 1. Send SSH protocol identification string (RFC 4253 Section 4.2)
        banner = b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6 NetMirage-Cowrie\r\n"
        client_sock.sendall(banner)

        # 2. Receive client identification or probe
        client_banner = b""
        try:
            client_banner = client_sock.recv(1024)
        except socket.timeout:
            pass

        client_banner_str = client_banner.decode("utf-8", errors="replace").strip()
        print(f"[SSH-LURE] Client identification received: '{client_banner_str}'")

        log_session("ssh_connect", {
            "source_ip": client_ip,
            "source_port": client_port,
            "client_banner": client_banner_str,
            "server_banner": "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6"
        })

        # 3. If client sends further payload (e.g. simulated auth or command probe)
        try:
            payload = client_sock.recv(4096)
            if payload:
                text = payload.decode("utf-8", errors="replace")
                print(f"[SSH-LURE] Client auth/command payload: {text[:100]}")
                log_session("ssh_payload", {
                    "source_ip": client_ip,
                    "payload_preview": text[:200]
                })
                # Send fake authentication accepted or shell prompt
                client_sock.sendall(b"Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-94-generic x86_64)\r\nroot@corp-ssh-01:~# ")
        except Exception:
            pass

    except Exception as err:
        print(f"[SSH-LURE] Error handling {addr}: {err}")
    finally:
        try:
            client_sock.close()
        except Exception:
            pass

def start_listener(port: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(10)
    print(f"[SSH-LURE] Listening on TCP 0.0.0.0:{port} (Cowrie SSH)")
    while True:
        try:
            client, addr = server.accept()
            t = threading.Thread(target=handle_ssh_client, args=(client, addr), daemon=True)
            t.start()
        except Exception as e:
            print(f"[SSH-LURE] Accept error on port {port}: {e}")
            time.sleep(1)

def main():
    print("[SSH-LURE] Initializing NetMirage SSH Cowrie Lure...")
    t22 = threading.Thread(target=start_listener, args=(22,), daemon=True)
    t2222 = threading.Thread(target=start_listener, args=(2222,), daemon=True)
    t22.start()
    t2222.start()
    t22.join()
    t2222.join()

if __name__ == "__main__":
    main()
