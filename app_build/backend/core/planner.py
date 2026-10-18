from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from app_build.backend.config import settings

@dataclass
class ObservationSummary:
    stage_index: int
    vantage_point: str
    discovered_nodes: List[str]
    open_ports: List[int]
    last_action_status: Optional[str]
    notes: str

@dataclass
class SafeActionRequest:
    action_type: str
    target_ip: str
    target_port: int
    parameters: Dict[str, Any]
    rationale: str

class AIPlanner:
    """
    3-layer Adversary Emulation Planner:
    1. observation_summary
    2. planner (deterministic cyber-range state machine or LLM)
    3. safe_action_request
    """

    DETERMINISTIC_PROGRESSION = [
        # Stage 0: Initial perimeter discovery
        {
            "action_type": "discover_lab_services",
            "target_ip": "10.0.10.42",
            "target_port": 80,
            "parameters": {"depth": "fast"},
            "rationale": "Discover active network services on edge gateway (10.0.10.42:80)"
        },
        # Stage 1: Internal DNS resolution for corporate services
        {
            "action_type": "resolve_dns",
            "target_ip": "10.0.40.10",
            "target_port": 53,
            "parameters": {"query": "ssh.corp.internal", "record_type": "A"},
            "rationale": "Resolve corporate SSH infrastructure via internal DNS lure"
        },
        # Stage 2: Public-facing web lure exploration
        {
            "action_type": "request_http",
            "target_ip": "10.0.30.10",
            "target_port": 80,
            "parameters": {"method": "GET", "path": "/admin/login"},
            "rationale": "Probe administrative web portal for vulnerabilities and reconnaissance"
        },
        # Stage 3: Credential brute force against SSH lure
        {
            "action_type": "attempt_ssh_to_lure",
            "target_ip": "10.0.20.10",
            "target_port": 22,
            "parameters": {
                "username": "root",
                "password": "SuperSecretPassword123!",  # Will be redacted by honeypot normalizer
                "command": "cat /etc/passwd"
            },
            "rationale": "Attempt automated credential authentication and post-auth reconnaissance on SSH lure"
        },
        # Stage 4: Inspect session output
        {
            "action_type": "inspect_session_output",
            "target_ip": "10.0.20.10",
            "target_port": 22,
            "parameters": {"filter": "latest"},
            "rationale": "Harvest session terminal output and command history"
        },
        # Stage 5: Covert ICMP probe
        {
            "action_type": "send_icmp_probe",
            "target_ip": "10.0.40.20",
            "target_port": 25,
            "parameters": {"ttl": 64, "payload_size": 32},
            "rationale": "Verify lateral reachability to corporate mail services via ICMP echo"
        },
        # Stage 6: Service reachability verification
        {
            "action_type": "connect_tcp",
            "target_ip": "10.0.40.10",
            "target_port": 53,
            "parameters": {"timeout": 2.0},
            "rationale": "Establish TCP connection to DNS service to confirm state"
        }
    ]

    def build_observation_summary(
        self,
        stage_index: int,
        prior_actions: List[Dict[str, Any]],
        prior_observations: List[Dict[str, Any]]
    ) -> ObservationSummary:
        discovered = set()
        open_ports = set()
        last_status = None

        for act in prior_actions:
            last_status = act.get("status")
            if act.get("target_ip"):
                discovered.add(act["target_ip"])
            if act.get("target_port"):
                open_ports.add(act["target_port"])

        return ObservationSummary(
            stage_index=stage_index,
            vantage_point="10.0.10.15 (Simulated Adversary Ingress)",
            discovered_nodes=list(discovered),
            open_ports=list(open_ports),
            last_action_status=last_status,
            notes=f"Active emulation at stage {stage_index}. Evaluated {len(prior_actions)} prior operations."
        )

    def plan_next_action(
        self,
        summary: ObservationSummary,
        stage_index: int
    ) -> SafeActionRequest:
        # Determine plan via deterministic progression loop
        progression_len = len(self.DETERMINISTIC_PROGRESSION)
        step = self.DETERMINISTIC_PROGRESSION[stage_index % progression_len]

        return SafeActionRequest(
            action_type=step["action_type"],
            target_ip=step["target_ip"],
            target_port=step["target_port"],
            parameters=step["parameters"].copy(),
            rationale=step["rationale"]
        )

planner = AIPlanner()
