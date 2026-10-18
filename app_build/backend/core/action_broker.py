import asyncio
import time
from typing import Dict, Any, Optional
from app_build.backend.core.safety_policy import safety_policy

class ActionBroker:
    """
    Executes permitted, strictly parameterized operations against the isolated cyber-range.
    Enforces the zero-arbitrary-shell architectural invariant.
    """

    def __init__(self, emulation_mode: bool = True):
        self.emulation_mode = emulation_mode

    async def execute_action(
        self,
        run_id: str,
        action_type: str,
        target_ip: str,
        target_port: int,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = parameters or {}
        start_time = time.perf_counter()

        try:
            if action_type == "discover_lab_services":
                result = await self._exec_discover_lab_services(target_ip, target_port, params)
            elif action_type == "resolve_dns":
                result = await self._exec_resolve_dns(target_ip, target_port, params)
            elif action_type == "connect_tcp":
                result = await self._exec_connect_tcp(target_ip, target_port, params)
            elif action_type == "request_http":
                result = await self._exec_request_http(target_ip, target_port, params)
            elif action_type == "attempt_ssh_to_lure":
                result = await self._exec_attempt_ssh_to_lure(target_ip, target_port, params)
            elif action_type == "send_icmp_probe":
                result = await self._exec_send_icmp_probe(target_ip, target_port, params)
            elif action_type == "inspect_session_output":
                result = await self._exec_inspect_session_output(target_ip, target_port, params)
            else:
                result = {
                    "status": "failed",
                    "output": f"Unsupported action type: {action_type}"
                }
        finally:
            # Release concurrency lock held by safety policy
            safety_policy.release_concurrency(run_id)

        latency_ms = int((time.perf_counter() - start_time) * 1000)

        return {
            "action": action_type,
            "target": target_ip,
            "port": target_port,
            "status": result.get("status", "completed"),
            "latency_ms": latency_ms,
            "output": result.get("output", "")
        }

    async def _exec_discover_lab_services(self, target_ip: str, target_port: int, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        # Service inventory based on target subnet
        discovered = []
        if target_ip.startswith("10.0.10."):
            discovered = [{"port": 80, "service": "HTTP/Reverse-Proxy", "banner": "Edge-Gateway-v2.1"}]
        elif target_ip.startswith("10.0.20."):
            discovered = [{"port": 22, "service": "SSH-2.0-OpenSSH_8.9p1", "banner": "Ubuntu-3ubuntu0.6"}]
        elif target_ip.startswith("10.0.30."):
            discovered = [
                {"port": 80, "service": "HTTP", "banner": "Apache/2.4.52 (Ubuntu)"},
                {"port": 8080, "service": "HTTP-Admin", "banner": "NetMirage-Internal-Portal/1.0"}
            ]
        elif target_ip.startswith("10.0.40."):
            discovered = [
                {"port": 53, "service": "DNS", "banner": "BIND 9.18.1"},
                {"port": 25, "service": "SMTP", "banner": "220 mail.corp.netmirage.internal ESMTP"}
            ]
        elif target_ip.startswith("10.0.50."):
            discovered = [{"port": 8080, "service": "Telemetry-Tap", "banner": "NetMirage-Collector"}]
        else:
            discovered = []

        return {
            "status": "completed",
            "output": {
                "scanned_target": target_ip,
                "open_services": discovered,
                "message": f"Service discovery completed on {target_ip}"
            }
        }

    async def _exec_resolve_dns(self, target_ip: str, target_port: int, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        query = params.get("query", "gateway.edge.internal")
        record_type = params.get("record_type", "A")

        dns_table = {
            "gateway.edge.internal": "10.0.10.42",
            "ssh.corp.internal": "10.0.20.10",
            "portal.web.internal": "10.0.30.10",
            "dns.services.internal": "10.0.40.10",
            "mail.services.internal": "10.0.40.20",
            "monitor.internal": "10.0.50.10",
            "corp-exfil.net": "10.0.40.10",
        }

        resolved_ip = dns_table.get(query, "10.0.40.10")
        return {
            "status": "completed",
            "output": {
                "server": target_ip,
                "query": query,
                "type": record_type,
                "resolved_ip": resolved_ip
            }
        }

    async def _exec_connect_tcp(self, target_ip: str, target_port: int, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        return {
            "status": "completed",
            "output": f"TCP SYN handshake succeeded with {target_ip}:{target_port}"
        }

    async def _exec_request_http(self, target_ip: str, target_port: int, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.02)
        method = params.get("method", "GET")
        path = params.get("path", "/")

        if path in ("/admin", "/admin/login"):
            resp = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>NetMirage Decoy Admin Console</body></html>"
        elif path.startswith("/api/"):
            resp = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"status": "ok", "service": "web-lure"}'
        else:
            resp = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>NetMirage Public Gateway</body></html>"

        return {
            "status": "completed",
            "output": {
                "method": method,
                "path": path,
                "status_code": 200,
                "response_preview": resp[:120]
            }
        }

    async def _exec_attempt_ssh_to_lure(self, target_ip: str, target_port: int, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.02)
        username = params.get("username", "root")
        command = params.get("command", "id")

        return {
            "status": "completed",
            "output": {
                "banner": "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6",
                "auth_status": "accepted_by_lure",
                "authenticated_user": username,
                "executed_command": command,
                "session_output": f"uid=0({username}) gid=0(root) groups=0(root)"
            }
        }

    async def _exec_send_icmp_probe(self, target_ip: str, target_port: int, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        ttl = params.get("ttl", 64)
        return {
            "status": "completed",
            "output": {
                "probe_type": "echo_request",
                "target": target_ip,
                "reply_received": True,
                "ttl": ttl,
                "rtt_ms": 1.2
            }
        }

    async def _exec_inspect_session_output(self, target_ip: str, target_port: int, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        return {
            "status": "completed",
            "output": {
                "target": target_ip,
                "session_count": 1,
                "last_active": "cowrie_ssh",
                "summary": "Captured terminal interaction logged to honeypot store"
            }
        }

action_broker = ActionBroker()
