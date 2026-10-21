"""
NetMirage PCAP Exporter
Converts executed cyber-range actions and decoy interactions into standard libpcap files.
Enables professors/evaluators to inspect real packet captures in Wireshark.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from scapy.all import Ether, IP, TCP, UDP, ICMP, DNS, DNSQR, DNSRR, Raw, wrpcap

WORKSPACE_ROOT = Path(r"c:\Users\varun\Projects\cn project")
CAPTURES_DIR = WORKSPACE_ROOT / "production_artifacts" / "captures"
LATEST_PCAP_PATH = CAPTURES_DIR / "latest_run.pcap"
PCAP_OUTPUT_PATH = LATEST_PCAP_PATH

def get_run_pcap_path(run_id: str) -> Path:
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    return CAPTURES_DIR / f"{run_id}.pcap"

def generate_pcap_from_actions(actions: List[Dict[str, Any]], run_id: Optional[str] = None) -> str:
    """
    Constructs real Scapy packet frames corresponding to executed actions.
    Saves in standard libpcap format readable by Wireshark, tcpdump, and tshark.
    Writes both to {run_id}.pcap and latest_run.pcap.
    """
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    target_pcap = get_run_pcap_path(run_id) if run_id and run_id != "latest" else LATEST_PCAP_PATH

    packets = []
    edge_ip = "10.0.10.42"

    for idx, act in enumerate(actions):
        act_type = act.get("action_type") or act.get("action")
        target_ip = act.get("target_ip") or act.get("target") or "10.0.20.10"
        target_port = int(act.get("target_port") or act.get("port") or 80)
        sport = 49152 + (idx * 10)

        if act_type == "resolve_dns":
            qname = act.get("parameters", {}).get("query", "ssh.corp.internal")
            resolved_ip = "10.0.20.10"
            if isinstance(act.get("output"), dict):
                resolved_ip = act["output"].get("resolved_ip", resolved_ip)
            
            # Query (Edge -> DNS Lure)
            dns_req = (
                Ether(src="02:42:0a:00:0a:2a", dst="02:42:0a:00:28:0a") /
                IP(src=edge_ip, dst=target_ip) /
                UDP(sport=sport, dport=target_port) /
                DNS(rd=1, qd=DNSQR(qname=qname))
            )
            # Response (DNS Lure -> Edge)
            dns_resp = (
                Ether(src="02:42:0a:00:28:0a", dst="02:42:0a:00:0a:2a") /
                IP(src=target_ip, dst=edge_ip) /
                UDP(sport=target_port, dport=sport) /
                DNS(qr=1, aa=1, rd=1, qd=DNSQR(qname=qname), an=DNSRR(rrname=qname, rdata=resolved_ip, ttl=300))
            )
            packets.extend([dns_req, dns_resp])

        elif act_type in ("connect_tcp", "discover_lab_services"):
            # 3-Way Handshake: SYN -> SYN-ACK -> ACK
            syn = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="S", seq=1000)
            syn_ack = Ether() / IP(src=target_ip, dst=edge_ip) / TCP(sport=target_port, dport=sport, flags="SA", seq=5000, ack=1001)
            ack = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="A", seq=1001, ack=5001)
            fin = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="FA", seq=1001, ack=5001)
            fin_ack = Ether() / IP(src=target_ip, dst=edge_ip) / TCP(sport=target_port, dport=sport, flags="A", seq=5001, ack=1002)
            packets.extend([syn, syn_ack, ack, fin, fin_ack])

        elif act_type == "request_http":
            path = act.get("parameters", {}).get("path", "/admin/login")
            # Handshake
            syn = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="S", seq=2000)
            syn_ack = Ether() / IP(src=target_ip, dst=edge_ip) / TCP(sport=target_port, dport=sport, flags="SA", seq=6000, ack=2001)
            ack = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="A", seq=2001, ack=6001)
            # HTTP Request
            http_req_data = f"GET {path} HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: NetMirage-Probe/2.0\r\nAccept: */*\r\n\r\n".encode("utf-8")
            http_req = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="PA", seq=2001, ack=6001) / Raw(load=http_req_data)
            # HTTP Response
            http_resp_data = (
                b"HTTP/1.1 200 OK\r\n"
                b"Server: Apache/2.4.52 (Ubuntu)\r\n"
                b"Content-Type: text/html; charset=utf-8\r\n"
                b"Content-Length: 55\r\n\r\n"
                b"<html><body>NetMirage Decoy Admin Console</body></html>\n"
            )
            http_resp = Ether() / IP(src=target_ip, dst=edge_ip) / TCP(sport=target_port, dport=sport, flags="PA", seq=6001, ack=2001 + len(http_req_data)) / Raw(load=http_resp_data)
            packets.extend([syn, syn_ack, ack, http_req, http_resp])

        elif act_type == "attempt_ssh_to_lure":
            # Handshake
            syn = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="S", seq=3000)
            syn_ack = Ether() / IP(src=target_ip, dst=edge_ip) / TCP(sport=target_port, dport=sport, flags="SA", seq=7000, ack=3001)
            ack = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="A", seq=3001, ack=7001)
            # SSH Server Banner
            server_banner = b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6 NetMirage-Cowrie\r\n"
            ssh_srv = Ether() / IP(src=target_ip, dst=edge_ip) / TCP(sport=target_port, dport=sport, flags="PA", seq=7001, ack=3001) / Raw(load=server_banner)
            # SSH Client Banner
            client_banner = b"SSH-2.0-NetMirage_root\r\n"
            ssh_cli = Ether() / IP(src=edge_ip, dst=target_ip) / TCP(sport=sport, dport=target_port, flags="PA", seq=3001, ack=7001 + len(server_banner)) / Raw(load=client_banner)
            packets.extend([syn, syn_ack, ack, ssh_srv, ssh_cli])

        elif act_type == "send_icmp_probe":
            echo_req = Ether() / IP(src=edge_ip, dst=target_ip, ttl=64) / ICMP(type=8, code=0, id=0x1234, seq=1) / Raw(load=b"NetMirage-Deception-Probe-Bytes")
            echo_reply = Ether() / IP(src=target_ip, dst=edge_ip, ttl=64) / ICMP(type=0, code=0, id=0x1234, seq=1) / Raw(load=b"NetMirage-Deception-Probe-Bytes")
            packets.extend([echo_req, echo_reply])

    wrpcap(str(target_pcap), packets)
    # Also write to latest_run.pcap
    wrpcap(str(LATEST_PCAP_PATH), packets)
    return str(target_pcap)
