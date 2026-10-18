import pytest
from datetime import datetime, timezone
from app_build.backend import models
from app_build.backend.core.safety_policy import safety_policy, SafetyPolicyEngine
from app_build.backend.core.action_broker import action_broker

def test_out_of_cidr_ips_denied():
    bad_ips = ["8.8.8.8", "192.168.1.1", "172.16.0.5", "127.0.0.1", "0.0.0.0", "10.0.99.1"]
    for ip in bad_ips:
        res = safety_policy.evaluate_action(
            run_id="run_safety_test",
            action_type="connect_tcp",
            target_ip=ip,
            target_port=80
        )
        assert res.allowed is False
        assert res.status == "denied"
        assert "outside allowed lab CIDRs" in res.reason

def test_unregistered_ports_denied():
    bad_ports = [443, 8443, 3306, 5432, 21, 23, 9000, 65535]
    for port in bad_ports:
        res = safety_policy.evaluate_action(
            run_id="run_safety_test",
            action_type="connect_tcp",
            target_ip="10.0.10.42",
            target_port=port
        )
        assert res.allowed is False
        assert res.status == "denied"
        assert "not in registered lab ports" in res.reason

def test_unauthorized_action_types_denied():
    bad_actions = ["execute_bash", "shell_exec", "spawn_process", "wget_download", "rm_rf"]
    for act in bad_actions:
        res = safety_policy.evaluate_action(
            run_id="run_safety_test",
            action_type=act,
            target_ip="10.0.10.42",
            target_port=80
        )
        assert res.allowed is False
        assert res.status == "denied"
        assert "not in the allowlist of 7 permitted actions" in res.reason

def test_valid_lab_actions_allowed():
    valid_cases = [
        ("discover_lab_services", "10.0.10.42", 80),
        ("resolve_dns", "10.0.40.10", 53),
        ("connect_tcp", "10.0.30.10", 80),
        ("request_http", "10.0.30.10", 8080),
        ("attempt_ssh_to_lure", "10.0.20.10", 22),
        ("send_icmp_probe", "10.0.40.20", 25),
        ("inspect_session_output", "10.0.20.10", 2222),
    ]
    for act_type, ip, port in valid_cases:
        res = safety_policy.evaluate_action(
            run_id=f"run_allowed_{act_type}",
            action_type=act_type,
            target_ip=ip,
            target_port=port
        )
        assert res.allowed is True
        assert res.status == "allowed"

def test_concurrency_cap_enforced():
    run_id = "run_concurrency_test"
    # Action 1 - Allowed
    res1 = safety_policy.evaluate_action(run_id, "connect_tcp", "10.0.10.42", 80)
    assert res1.allowed is True

    # Action 2 - Allowed
    res2 = safety_policy.evaluate_action(run_id, "connect_tcp", "10.0.10.42", 80)
    assert res2.allowed is True

    # Action 3 - Denied due to concurrency cap (max 2)
    res3 = safety_policy.evaluate_action(run_id, "connect_tcp", "10.0.10.42", 80)
    assert res3.allowed is False
    assert res3.status == "denied"
    assert "Concurrency cap reached" in res3.reason

    # Clean up concurrency
    safety_policy.release_concurrency(run_id)
    safety_policy.release_concurrency(run_id)

def test_kill_switch_blocks_actions(test_db):
    run = models.Run(
        id="run_terminated_test",
        status="terminated",
        threat_score=50,
        created_at=datetime.now(timezone.utc)
    )
    test_db.add(run)
    test_db.commit()

    res = safety_policy.evaluate_action(
        run_id=run.id,
        action_type="discover_lab_services",
        target_ip="10.0.10.42",
        target_port=80,
        db=test_db
    )
    assert res.allowed is False
    assert res.status == "denied"
    assert "Global Kill Switch active" in res.reason

def test_paused_run_blocks_actions(test_db):
    run = models.Run(
        id="run_paused_test",
        status="paused",
        threat_score=30,
        created_at=datetime.now(timezone.utc)
    )
    test_db.add(run)
    test_db.commit()

    res = safety_policy.evaluate_action(
        run_id=run.id,
        action_type="discover_lab_services",
        target_ip="10.0.10.42",
        target_port=80,
        db=test_db
    )
    assert res.allowed is False
    assert res.status == "denied"
    assert "Global Kill Switch active" in res.reason

def test_container_security_assertions():
    # Privileged container must be rejected
    valid, reason = safety_policy.validate_container_security({"privileged": True})
    assert valid is False
    assert "privileged: true is strictly forbidden" in reason

    # Host network container must be rejected
    valid, reason = safety_policy.validate_container_security({"network_mode": "host"})
    assert valid is False
    assert "network_mode: host is strictly forbidden" in reason

    # Secure container should pass
    valid, reason = safety_policy.validate_container_security({"privileged": False, "read_only": True})
    assert valid is True
    assert reason is None

@pytest.mark.asyncio
async def test_action_broker_execution():
    broker_out = await action_broker.execute_action(
        run_id="run_broker_test",
        action_type="connect_tcp",
        target_ip="10.0.30.10",
        target_port=80,
        parameters={}
    )
    assert broker_out["action"] == "connect_tcp"
    assert broker_out["target"] == "10.0.30.10"
    assert broker_out["port"] == 80
    assert broker_out["status"] == "completed"
    assert broker_out["latency_ms"] >= 0
    assert "TCP SYN handshake succeeded" in broker_out["output"]
