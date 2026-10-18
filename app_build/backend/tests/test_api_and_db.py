from datetime import datetime, timezone
import pytest
from app_build.backend import models

def test_six_database_tables_crud(test_db):
    # 1. Run
    run = models.Run(
        id="run_test_001",
        status="running",
        threat_score=15,
        active_profile="reconnaissance",
        next_deception_zone="edge",
        created_at=datetime.now(timezone.utc),
        metadata_json={"test": True}
    )
    test_db.add(run)
    test_db.commit()

    # 2. AgentAction
    action = models.AgentAction(
        id="act_test_001",
        run_id=run.id,
        action_type="discover_lab_services",
        target_ip="10.0.10.42",
        target_port=80,
        parameters={"depth": "fast"},
        status="completed",
        latency_ms=12,
        output={"status": "ok"}
    )
    test_db.add(action)

    # 3. Observation
    obs = models.Observation(
        id="obs_test_001",
        run_id=run.id,
        source="protocol-analyzer",
        source_ip="10.0.10.15",
        destination_ip="10.0.10.42",
        protocol="TCP",
        behavior_type="port_discovery",
        raw_payload={"flags": "SYN"},
        details={"scanned_ports": [80]}
    )
    test_db.add(obs)

    # 4. Detection
    det = models.Detection(
        id="det_test_001",
        run_id=run.id,
        source_ip="10.0.10.15",
        technique_id="T1046",
        technique_name="Network Service Discovery",
        confidence=0.90,
        evidence={"ports": [80]}
    )
    test_db.add(det)

    # 5. HoneypotSession
    ses = models.HoneypotSession(
        id="ses_test_001",
        run_id=run.id,
        lure_type="cowrie_ssh",
        session_id="ses_cowrie_1",
        source_ip="10.0.10.15",
        source_port=51234,
        commands_or_requests=[{"command": "whoami", "password": "[REDACTED]"}],
        metadata_json={"banner": "SSH-2.0-OpenSSH"}
    )
    test_db.add(ses)

    # 6. PolicyDecision
    pol = models.PolicyDecision(
        id="pol_test_001",
        run_id=run.id,
        threat_profile="reconnaissance",
        confidence=0.85,
        decision="Route to SSH lure",
        target_zone="ssh-lure",
        evidence={"trigger": "T1046"}
    )
    test_db.add(pol)
    test_db.commit()

    # Assert persistence across all 6 tables
    assert test_db.query(models.Run).count() == 1
    assert test_db.query(models.AgentAction).count() == 1
    assert test_db.query(models.Observation).count() == 1
    assert test_db.query(models.Detection).count() == 1
    assert test_db.query(models.HoneypotSession).count() == 1
    assert test_db.query(models.PolicyDecision).count() == 1

    # Verify relationships
    queried_run = test_db.query(models.Run).filter(models.Run.id == run.id).first()
    assert len(queried_run.actions) == 1
    assert len(queried_run.observations) == 1
    assert len(queried_run.detections) == 1
    assert len(queried_run.honeypot_sessions) == 1
    assert len(queried_run.policy_decisions) == 1

def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["lab_mode"] == "zero-egress-emulated"
    assert data["egress_guard"] == "enforced"

def test_api_topology(client):
    response = client.get("/api/topology")
    assert response.status_code == 200
    data = response.json()
    segments = data["segments"]
    assert len(segments) == 5
    segment_names = [s["name"] for s in segments]
    assert "edge" in segment_names
    assert "ssh" in segment_names
    assert "web" in segment_names
    assert "services" in segment_names
    assert "monitor" in segment_names

    # Check CIDRs
    cidrs = {s["name"]: s["cidr"] for s in segments}
    assert cidrs["edge"] == "10.0.10.0/24"
    assert cidrs["ssh"] == "10.0.20.0/24"
    assert cidrs["web"] == "10.0.30.0/24"
    assert cidrs["services"] == "10.0.40.0/24"
    assert cidrs["monitor"] == "10.0.50.0/24"

    # Check active lures
    assert len(data["active_lures"]) == 4

def test_run_lifecycle_api(client, test_db):
    # 1. Create run
    create_resp = client.post("/api/runs", json={"scenario": "test_adversary"})
    assert create_resp.status_code == 201
    run_data = create_resp.json()
    run_id = run_data["id"]
    assert run_id.startswith("run_")

    # 2. Pause run
    pause_resp = client.post(f"/api/runs/{run_id}/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    # 3. Resume run
    resume_resp = client.post(f"/api/runs/{run_id}/resume")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "running"

    # 4. Terminate run
    term_resp = client.post(f"/api/runs/{run_id}/terminate")
    assert term_resp.status_code == 200
    assert term_resp.json()["status"] == "terminated"

def test_honeypot_session_api_redaction(client, test_db):
    run = models.Run(
        id="run_redact_test",
        status="running",
        threat_score=10,
        created_at=datetime.now(timezone.utc)
    )
    test_db.add(run)
    test_db.commit()

    ses = models.HoneypotSession(
        id="ses_redact_001",
        run_id=run.id,
        lure_type="cowrie_ssh",
        session_id="ses_redact_001",
        source_ip="10.0.10.15",
        source_port=50000,
        commands_or_requests=[
            {"username": "admin", "password": "[REDACTED]", "command": "cat /etc/shadow"}
        ],
        metadata_json={"secret_key": "[REDACTED]"}
    )
    test_db.add(ses)
    test_db.commit()

    # Query by session id
    resp = client.get(f"/api/sessions/{ses.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["commands_or_requests"][0]["password"] == "[REDACTED]"
    assert data["metadata_json"]["secret_key"] == "[REDACTED]"

    # Query by run id
    run_resp = client.get(f"/api/sessions/{run.id}")
    assert run_resp.status_code == 200
    assert isinstance(run_resp.json(), list)
    assert len(run_resp.json()) == 1

    # Query via explicit /api/runs/{run_id}/sessions endpoint
    run_sessions_resp = client.get(f"/api/runs/{run.id}/sessions")
    assert run_sessions_resp.status_code == 200
    assert len(run_sessions_resp.json()) == 1
    assert run_sessions_resp.json()[0]["id"] == ses.id

def test_websocket_streaming(client, test_db):
    run = models.Run(
        id="run_ws_test",
        status="running",
        threat_score=20,
        next_deception_zone="edge",
        created_at=datetime.now(timezone.utc)
    )
    test_db.add(run)
    test_db.commit()

    with client.websocket_connect(f"/api/runs/{run.id}/events") as websocket:
        initial_msg = websocket.receive_json()
        assert initial_msg["run_id"] == run.id
        assert initial_msg["kind"] == "system"
        assert initial_msg["payload"]["status"] == "running"
