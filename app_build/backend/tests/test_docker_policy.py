from pathlib import Path
import yaml
import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
COMPOSE_FILE = WORKSPACE_ROOT / "app_build" / "docker" / "docker-compose.lab.yml"

def test_docker_compose_exists():
    assert COMPOSE_FILE.exists(), f"Compose file not found at {COMPOSE_FILE}"

def test_zero_egress_and_cidr_policy():
    with open(COMPOSE_FILE, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    assert "networks" in compose_data
    networks = compose_data["networks"]

    expected_subnets = {
        "edge_net": "10.0.10.0/24",
        "ssh_net": "10.0.20.0/24",
        "web_net": "10.0.30.0/24",
        "services_net": "10.0.40.0/24",
        "monitor_net": "10.0.50.0/24"
    }

    # Verify all 5 segregated networks exist
    for net_name, expected_cidr in expected_subnets.items():
        assert net_name in networks, f"Missing network {net_name}"
        net_cfg = networks[net_name]

        # Enforce zero-egress internal: true
        assert net_cfg.get("internal") is True, f"Network {net_name} MUST have internal: true (zero internet egress)"

        # Check CIDR
        configs = net_cfg.get("ipam", {}).get("config", [])
        assert len(configs) > 0, f"No IPAM config for {net_name}"
        assert configs[0].get("subnet") == expected_cidr, f"Subnet mismatch for {net_name}: expected {expected_cidr}, got {configs[0].get('subnet')}"

def test_container_security_boundaries():
    with open(COMPOSE_FILE, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    assert "services" in compose_data
    services = compose_data["services"]

    expected_services = ["edge-gateway", "cowrie-ssh-lure", "web-lure", "dns-smtp-lure", "telemetry-collector"]
    for svc_name in expected_services:
        assert svc_name in services, f"Service {svc_name} missing from docker-compose.lab.yml"
        svc = services[svc_name]

        # Zero host breakout / privilege escalation assertions
        assert svc.get("privileged") is not True, f"Service {svc_name} MUST NOT have privileged: true"
        assert svc.get("network_mode") != "host", f"Service {svc_name} MUST NOT use network_mode: host"

        # Cap drops and security options
        security_opt = svc.get("security_opt", [])
        assert "no-new-privileges:true" in security_opt, f"Service {svc_name} missing no-new-privileges:true"

        cap_drop = svc.get("cap_drop", [])
        assert "ALL" in cap_drop, f"Service {svc_name} missing cap_drop: ALL"
