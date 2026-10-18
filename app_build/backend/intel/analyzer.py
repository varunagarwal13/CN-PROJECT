import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class ProtocolAnalyzer:
    """
    Passive protocol intelligence adapter and telemetry analyzer.
    Extracts behavioral indicators from network transactions without host reconfiguration.
    """

    def analyze_action_event(
        self,
        run_id: str,
        action: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Derives passive network observations from executed lab actions.
        """
        observations = []
        action_type = action.get("action_type") or action.get("action")
        target_ip = action.get("target_ip") or action.get("target")
        target_port = action.get("target_port") or action.get("port")
        source_ip = action.get("source_ip", "10.0.10.15")

        now_iso = datetime.now(timezone.utc).isoformat()

        if action_type == "discover_lab_services":
            observations.append({
                "observation_id": f"obs_{uuid.uuid4().hex[:8]}",
                "source": "protocol-analyzer",
                "source_ip": source_ip,
                "destination_ip": target_ip,
                "protocol": "TCP",
                "behavior_type": "port_discovery",
                "raw_payload": {"scanned_ports": [22, 53, 80, 8080], "flags": "SYN"},
                "details": {
                    "pattern": "Sequential SYN sweep across registered lab segments",
                    "incomplete_handshakes": 3,
                    "target_subnet": target_ip.rsplit(".", 1)[0] + ".0/24"
                }
            })

        elif action_type == "connect_tcp":
            observations.append({
                "observation_id": f"obs_{uuid.uuid4().hex[:8]}",
                "source": "protocol-analyzer",
                "source_ip": source_ip,
                "destination_ip": target_ip,
                "protocol": "TCP",
                "behavior_type": "tcp_syn_pattern",
                "raw_payload": {"flags": "SYN_ACK_ESTABLISHED", "port": target_port},
                "details": {
                    "rtt_ms": 1.4,
                    "retransmission_count": 0,
                    "state": "established"
                }
            })

        elif action_type == "request_http":
            path = action.get("parameters", {}).get("path", "/")
            behavior = "web_path_probing" if "/admin" in path else "http_traffic"
            observations.append({
                "observation_id": f"obs_{uuid.uuid4().hex[:8]}",
                "source": "protocol-analyzer",
                "source_ip": source_ip,
                "destination_ip": target_ip,
                "protocol": "HTTP",
                "behavior_type": behavior,
                "raw_payload": {"path": path, "method": "GET"},
                "details": {
                    "uri": path,
                    "user_agent": "Mozilla/5.0 (Adversary Scanner 1.0)",
                    "status_code": 200
                }
            })

        elif action_type == "attempt_ssh_to_lure":
            observations.append({
                "observation_id": f"obs_{uuid.uuid4().hex[:8]}",
                "source": "protocol-analyzer",
                "source_ip": source_ip,
                "destination_ip": target_ip,
                "protocol": "SSH",
                "behavior_type": "ssh_credential_probing",
                "raw_payload": {"kex": "curve25519-sha256", "cipher": "chacha20-poly1305@openssh.com"},
                "details": {
                    "target_lure": "cowrie-ssh-lure",
                    "auth_attempts": 1,
                    "timing_interval_ms": 120
                }
            })

        elif action_type == "resolve_dns":
            query = action.get("parameters", {}).get("query", "")
            is_anomaly = "exfil" in query or len(query) > 20
            behavior = "dns_anomaly" if is_anomaly else "dns_query"
            observations.append({
                "observation_id": f"obs_{uuid.uuid4().hex[:8]}",
                "source": "protocol-analyzer",
                "source_ip": source_ip,
                "destination_ip": target_ip,
                "protocol": "DNS",
                "behavior_type": behavior,
                "raw_payload": {"query": query, "type": "A"},
                "details": {
                    "record_type": "A",
                    "query_string": query,
                    "potential_covert_channel": is_anomaly
                }
            })

        elif action_type == "send_icmp_probe":
            observations.append({
                "observation_id": f"obs_{uuid.uuid4().hex[:8]}",
                "source": "protocol-analyzer",
                "source_ip": source_ip,
                "destination_ip": target_ip,
                "protocol": "ICMP",
                "behavior_type": "icmp_payload_anomaly",
                "raw_payload": {"type": 8, "code": 0, "size": 32},
                "details": {
                    "echo_sequence": 1,
                    "ttl": 64,
                    "entropy": 4.12
                }
            })

        return observations

    def analyze_scapy_packet(self, packet_bytes: bytes, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Parses raw packet bytes using Scapy if available.
        """
        try:
            from scapy.layers.inet import IP, TCP, UDP, ICMP
            from scapy.all import Ether
            pkt = Ether(packet_bytes)
            if pkt.haslayer(IP):
                ip_layer = pkt[IP]
                return {
                    "observation_id": f"obs_{uuid.uuid4().hex[:8]}",
                    "source": "protocol-analyzer",
                    "source_ip": ip_layer.src,
                    "destination_ip": ip_layer.dst,
                    "protocol": "TCP" if pkt.haslayer(TCP) else ("UDP" if pkt.haslayer(UDP) else "IP"),
                    "behavior_type": "packet_capture",
                    "raw_payload": {"length": len(packet_bytes)},
                    "details": {"summary": pkt.summary()}
                }
        except Exception:
            pass
        return None

protocol_analyzer = ProtocolAnalyzer()
