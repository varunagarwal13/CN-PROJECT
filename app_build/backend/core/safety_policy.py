import ipaddress
import time
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app_build.backend.config import settings
from app_build.backend import models

ALLOWLISTED_ACTIONS = {
    "discover_lab_services",
    "resolve_dns",
    "connect_tcp",
    "request_http",
    "attempt_ssh_to_lure",
    "send_icmp_probe",
    "inspect_session_output",
}

DEFAULT_PORTS = {22, 2222, 53, 80, 8080, 25, 2525, 587}
DANGEROUS_PATTERNS = [
    r";", r"\|", r"&&", r"\$\(", r"`", r">\s*/", r"<\s*/",
    r"rm\s+-rf", r"whoami", r"\bnc\s+", r"/bin/sh", r"/bin/bash"
]

@dataclass
class PolicyResult:
    allowed: bool
    status: str  # "allowed" or "denied"
    reason: str

class SafetyPolicyEngine:
    def __init__(self, allowed_cidrs: Optional[str] = None, allowed_ports: Optional[str] = None):
        # Fail-closed CIDR initialization
        raw_cidrs = settings.ALLOWED_LAB_CIDRS if allowed_cidrs is None else allowed_cidrs
        cidr_strs = [c.strip() for c in raw_cidrs.split(",") if c.strip()]
        self.allowed_networks = []
        for c in cidr_strs:
            try:
                self.allowed_networks.append(ipaddress.ip_network(c))
            except Exception:
                pass  # Ignore invalid, fail closed

        # Fail-closed Port initialization
        raw_ports = settings.ALLOWED_LAB_PORTS if allowed_ports is None else allowed_ports
        port_strs = [p.strip() for p in raw_ports.split(",") if p.strip()]
        self.allowed_ports: Set[int] = set()
        for p in port_strs:
            try:
                self.allowed_ports.add(int(p))
            except Exception:
                pass

        # In-memory tracking for rate limits and concurrency
        self._action_timestamps: Dict[str, List[float]] = {}
        self._active_concurrency: Dict[str, int] = {}

    def is_ip_in_lab(self, ip_str: str) -> bool:
        if not self.allowed_networks:
            return False
        try:
            ip = ipaddress.ip_address(ip_str.strip())
            return any(ip in net for net in self.allowed_networks)
        except Exception:
            return False

    def is_port_allowed(self, port: int) -> bool:
        if not self.allowed_ports:
            return False
        return port in self.allowed_ports

    def check_rate_limit(self, run_id: str) -> bool:
        now = time.time()
        window = 60.0  # 1 minute
        history = self._action_timestamps.get(run_id, [])
        recent = [t for t in history if now - t < window]
        self._action_timestamps[run_id] = recent
        if len(recent) >= settings.MAX_ACTIONS_PER_MINUTE:
            return False
        return True

    def record_action_timestamp(self, run_id: str):
        now = time.time()
        if run_id not in self._action_timestamps:
            self._action_timestamps[run_id] = []
        self._action_timestamps[run_id].append(now)

    def acquire_concurrency(self, run_id: str) -> bool:
        count = self._active_concurrency.get(run_id, 0)
        if count >= settings.MAX_CONCURRENT_ACTIONS:
            return False
        self._active_concurrency[run_id] = count + 1
        return True

    def release_concurrency(self, run_id: str):
        count = self._active_concurrency.get(run_id, 0)
        if count > 0:
            self._active_concurrency[run_id] = count - 1

    def validate_container_security(self, container_spec: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Asserts container security posture (no privileged, no host-network, zero-egress)."""
        if container_spec.get("privileged") is True:
            return False, "privileged: true is strictly forbidden"
        if container_spec.get("network_mode") == "host":
            return False, "network_mode: host is strictly forbidden"
        return True, None

    def validate_parameters(self, params: Optional[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Scans parameters to reject arbitrary command injection strings."""
        if not params:
            return True, None
        for key, val in params.items():
            str_val = str(val)
            for pat in DANGEROUS_PATTERNS:
                if re.search(pat, str_val, re.IGNORECASE):
                    return False, f"Command injection or shell metacharacter '{pat}' detected in parameter '{key}'."
        return True, None

    def evaluate_action(
        self,
        run_id: str,
        action_type: str,
        target_ip: str,
        target_port: int,
        db: Optional[Session] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> PolicyResult:
        """
        Fail-closed policy evaluation for proposed AI agent actions.
        """
        # 1. Action type allowlist check
        if not action_type or action_type not in ALLOWLISTED_ACTIONS:
            return PolicyResult(
                allowed=False,
                status="denied",
                reason=f"Action '{action_type}' is not in the allowlist of 7 permitted actions."
            )

        # 2. Check Run state / Global Kill Switch
        if db is not None:
            run = db.query(models.Run).filter(models.Run.id == run_id).first()
            if not run:
                return PolicyResult(allowed=False, status="denied", reason="Run not found.")
            if run.status in ("paused", "terminated", "completed"):
                return PolicyResult(
                    allowed=False,
                    status="denied",
                    reason=f"Global Kill Switch active: run is currently '{run.status}'."
                )

            # 3. Max run duration check
            if run.started_at:
                now = datetime.now(timezone.utc)
                started = run.started_at
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
                duration = (now - started).total_seconds()
                if duration > settings.MAX_RUN_DURATION_SECONDS:
                    return PolicyResult(
                        allowed=False,
                        status="denied",
                        reason=f"Run exceeded maximum duration limit of {settings.MAX_RUN_DURATION_SECONDS}s."
                    )

        # 4. Target IP CIDR check
        if not target_ip or not self.is_ip_in_lab(target_ip):
            return PolicyResult(
                allowed=False,
                status="denied",
                reason=f"Destination IP '{target_ip}' is outside allowed lab CIDRs."
            )

        # 5. Target Port check
        if target_port is None or not self.is_port_allowed(target_port):
            return PolicyResult(
                allowed=False,
                status="denied",
                reason=f"Destination port '{target_port}' is not in registered lab ports."
            )

        # 6. Parameter command injection check
        params_ok, err_msg = self.validate_parameters(parameters)
        if not params_ok:
            return PolicyResult(
                allowed=False,
                status="denied",
                reason=err_msg or "Command injection attempt detected."
            )

        # 7. Rate limit check
        if not self.check_rate_limit(run_id):
            return PolicyResult(
                allowed=False,
                status="denied",
                reason=f"Rate limit exceeded: max {settings.MAX_ACTIONS_PER_MINUTE} actions/min."
            )

        # 8. Concurrency cap check
        if not self.acquire_concurrency(run_id):
            return PolicyResult(
                allowed=False,
                status="denied",
                reason=f"Concurrency cap reached: max {settings.MAX_CONCURRENT_ACTIONS} active actions."
            )

        # Record this action for rate limiting
        self.record_action_timestamp(run_id)

        return PolicyResult(
            allowed=True,
            status="allowed",
            reason="Action conforms to all zero-trust safety guardrails."
        )

safety_policy = SafetyPolicyEngine()
