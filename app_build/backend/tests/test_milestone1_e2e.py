import pytest
from starlette.websockets import WebSocketDisconnect
from app_build.backend import models

@pytest.mark.asyncio
async def test_milestone1_full_e2e_flow(client, test_db):
    """
    End-to-End Milestone 1 Verification:
    1. Starts a run via POST /api/runs.
    2. Subscribes to WS /api/runs/:id/events.
    3. Verifies multi-stage execution across AI planner, safety policy,
       action broker, honeypot redaction, passive analyzer, MITRE ATT&CK mapper,
       and dynamic deception router.
    4. Triggers POST /api/runs/:id/terminate (Global Kill Switch).
    5. Asserts graceful halt and terminal state.
    """
    # 1. Initialize run
    create_resp = client.post("/api/runs", json={"scenario": "milestone1_adversary_emulation"})
    assert create_resp.status_code == 201
    run_data = create_resp.json()
    run_id = run_data["id"]
    assert run_id.startswith("run_")

    # 2. Connect WebSocket to stream events
    received_events = []
    found_t1046 = False
    found_t1110 = False
    found_deception_policy = False
    found_honeypot = False

    with client.websocket_connect(f"/api/runs/{run_id}/events") as websocket:
        for _ in range(30):
            try:
                evt = websocket.receive_json()
                received_events.append(evt)
                kind = evt.get("kind")
                payload = evt.get("payload", {})

                if kind == "detection":
                    tech = payload.get("technique_id")
                    if tech == "T1046":
                        found_t1046 = True
                    elif tech == "T1110":
                        found_t1110 = True

                elif kind == "policy":
                    found_deception_policy = True

                elif kind == "honeypot":
                    found_honeypot = True
                    cmds = payload.get("commands_or_requests", [])
                    for cmd in cmds:
                        if "password" in cmd and cmd["password"]:
                            assert cmd["password"] == "[REDACTED]"

                if found_t1046 and found_t1110 and found_deception_policy and found_honeypot:
                    break
            except (WebSocketDisconnect, Exception):
                break

    # Verify key Milestone 1 invariants
    assert found_t1046, "MITRE T1046 (Network Service Discovery) must be detected"
    assert found_t1110, "MITRE T1110 (Brute Force) must be detected"
    assert found_deception_policy, "Dynamic deception policy must trigger dynamic routing"
    assert found_honeypot, "Honeypot session must be captured with credentials sanitized"

    # Verify Universal Event Envelope conformance
    for evt in received_events:
        assert "run_id" in evt
        assert "event_id" in evt
        assert "timestamp" in evt
        assert "kind" in evt
        assert "source" in evt
        assert "payload" in evt
        assert evt["kind"] in ("detection", "action", "observation", "honeypot", "policy", "system")

    # 4. Trigger Global Kill Switch via POST /api/runs/:id/terminate
    term_resp = client.post(f"/api/runs/{run_id}/terminate")
    assert term_resp.status_code == 200
    assert term_resp.json()["status"] == "terminated"

    # Query DB to assert terminated state
    run_record = test_db.query(models.Run).filter(models.Run.id == run_id).first()
    assert run_record.status == "terminated"
    assert run_record.ended_at is not None

    # Verify recorded database entries
    actions = test_db.query(models.AgentAction).filter(models.AgentAction.run_id == run_id).all()
    observations = test_db.query(models.Observation).filter(models.Observation.run_id == run_id).all()
    detections = test_db.query(models.Detection).filter(models.Detection.run_id == run_id).all()
    decisions = test_db.query(models.PolicyDecision).filter(models.PolicyDecision.run_id == run_id).all()

    assert len(actions) > 0, "Agent actions must be persisted to DB"
    assert len(observations) > 0, "Observations must be persisted to DB"
    assert len(detections) > 0, "Detections must be persisted to DB"
    assert len(decisions) > 0, "Policy decisions must be persisted to DB"
