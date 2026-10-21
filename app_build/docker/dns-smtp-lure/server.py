"""
NetMirage Real DNS & SMTP Decoy Lure Server
1. DNS Server: Listens on UDP/TCP 53, resolves RFC 1035 A records for internal domains.
2. SMTP Server: Listens on TCP 25 and TCP 2525, emulates Postfix ESMTP exchange.
Logs transactions to /tmp/dns_queries.jsonl and /tmp/smtp_requests.jsonl
"""

import socket
import threading
import json
import struct
import time
from datetime import datetime, timezone

DNS_LOG = "/tmp/dns_queries.jsonl"
SMTP_LOG = "/tmp/smtp_requests.jsonl"

DNS_RECORDS = {
    "gateway.edge.internal": "10.0.10.42",
    "ssh.corp.internal": "10.0.20.10",
    "portal.web.internal": "10.0.30.10",
    "dns.services.internal": "10.0.40.10",
    "mail.services.internal": "10.0.40.20",
    "monitor.internal": "10.0.50.10",
    "corp-exfil.net": "10.0.40.10"
}

def log_event(log_path: str, data: dict):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **data
    }
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[DNS-SMTP] Log error: {e}")

# -------------------------------------------------------------
# DNS SERVER (UDP & TCP 53)
# -------------------------------------------------------------
def parse_dns_query_name(data: bytes, offset: int = 12):
    labels = []
    curr = offset
    while curr < len(data):
        length = data[curr]
        if length == 0:
            curr += 1
            break
        curr += 1
        labels.append(data[curr:curr+length].decode("utf-8", errors="replace"))
        curr += length
    qname = ".".join(labels)
    # 2 bytes QTYPE, 2 bytes QCLASS
    qtype = struct.unpack("!H", data[curr:curr+2])[0] if curr + 2 <= len(data) else 1
    return qname, qtype, curr + 4

def build_dns_response(data: bytes):
    if len(data) < 12:
        return None
    trans_id = data[:2]
    # Standard query response, recursion desired, recursion available, no error
    flags = b"\x81\x80"
    qdcount = data[4:6]
    ancount = b"\x00\x01" # 1 answer
    nscount = b"\x00\x00"
    arcount = b"\x00\x00"

    header = trans_id + flags + qdcount + ancount + nscount + arcount

    qname, qtype, q_end = parse_dns_query_name(data, 12)
    question = data[12:q_end]

    # Resolve IP
    resolved_ip = DNS_RECORDS.get(qname.lower(), "10.0.40.10")

    # Answer RR: Name pointer 0xc00c (points to offset 12 in packet)
    ans_ptr = b"\xc0\x0c"
    ans_type = b"\x00\x01" # Type A
    ans_class = b"\x00\x01" # Class IN
    ans_ttl = struct.pack("!I", 300) # 300s TTL
    ans_len = struct.pack("!H", 4)
    ans_ip = socket.inet_aton(resolved_ip)

    answer = ans_ptr + ans_type + ans_class + ans_ttl + ans_len + ans_ip
    return header + question + answer, qname, resolved_ip

def start_dns_udp_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", 53))
    print("[DNS-LURE] Listening on UDP 0.0.0.0:53 (BIND Decoy)")

    while True:
        try:
            data, addr = server.recvfrom(2048)
            resp, qname, resolved_ip = build_dns_response(data)
            if resp:
                server.sendto(resp, addr)
                print(f"[DNS-LURE] Query from {addr[0]}: '{qname}' -> {resolved_ip}")
                log_event(DNS_LOG, {
                    "source_ip": addr[0],
                    "query": qname,
                    "resolved_ip": resolved_ip,
                    "protocol": "UDP"
                })
        except Exception as e:
            print(f"[DNS-LURE] UDP error: {e}")

# -------------------------------------------------------------
# SMTP SERVER (TCP 25 & 2525)
# -------------------------------------------------------------
def handle_smtp_client(client_sock: socket.socket, addr: tuple):
    client_ip, client_port = addr
    print(f"[SMTP-LURE] Inbound SMTP connection from {client_ip}:{client_port}")
    try:
        client_sock.settimeout(10.0)
        client_sock.sendall(b"220 mail.corp.netmirage.internal ESMTP Postfix (Ubuntu)\r\n")

        commands = []
        while True:
            line = client_sock.recv(1024)
            if not line:
                break
            cmd = line.decode("utf-8", errors="replace").strip()
            print(f"[SMTP-LURE] Received: {cmd}")
            commands.append(cmd)

            upper = cmd.upper()
            if upper.startswith("HELO") or upper.startswith("EHLO"):
                client_sock.sendall(b"250-mail.corp.netmirage.internal\r\n250-PIPELINING\r\n250-SIZE 10240000\r\n250 8BITMIME\r\n")
            elif upper.startswith("MAIL FROM"):
                client_sock.sendall(b"250 2.1.0 Ok\r\n")
            elif upper.startswith("RCPT TO"):
                client_sock.sendall(b"250 2.1.5 Ok\r\n")
            elif upper.startswith("DATA"):
                client_sock.sendall(b"354 End data with <CR><LF>.<CR><LF>\r\n")
                # Consume until .
                client_sock.recv(4096)
                client_sock.sendall(b"250 2.0.0 Ok: queued as 7F3A901B\r\n")
            elif upper.startswith("QUIT"):
                client_sock.sendall(b"221 2.0.0 Bye\r\n")
                break
            else:
                client_sock.sendall(b"250 2.0.0 Ok\r\n")

        log_event(SMTP_LOG, {
            "source_ip": client_ip,
            "commands": commands
        })
    except Exception as e:
        print(f"[SMTP-LURE] Error with {addr}: {e}")
    finally:
        try:
            client_sock.close()
        except Exception:
            pass

def start_smtp_listener(port: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(10)
    print(f"[SMTP-LURE] Listening on TCP 0.0.0.0:{port} (Postfix ESMTP)")
    while True:
        try:
            client, addr = server.accept()
            t = threading.Thread(target=handle_smtp_client, args=(client, addr), daemon=True)
            t.start()
        except Exception as e:
            print(f"[SMTP-LURE] Accept error on {port}: {e}")
            time.sleep(1)

def main():
    print("[SERVICES-LURE] Initializing NetMirage DNS & SMTP Decoy Services...")
    t_dns = threading.Thread(target=start_dns_udp_listener, daemon=True)
    t_smtp25 = threading.Thread(target=start_smtp_listener, args=(25,), daemon=True)
    t_smtp2525 = threading.Thread(target=start_smtp_listener, args=(2525,), daemon=True)
    t_dns.start()
    t_smtp25.start()
    t_smtp2525.start()
    t_dns.join()
    t_smtp25.join()
    t_smtp2525.join()

if __name__ == "__main__":
    main()
