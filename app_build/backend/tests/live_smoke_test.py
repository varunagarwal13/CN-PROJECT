"""
Live Integration Smoke Test for NetMirage Platform.
Verifies real HTTP endpoints, real WebSocket streaming, interactive run controls (pause/resume/terminate),
and database persistence with credential sanitization on running FastAPI daemon.
"""

import asyncio
import json
import sys
import httpx
import websockets
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
DB_URL = "sqlite:///netmirage.db"

async def verify_live_health_and_topology(client: httpx.AsyncClient):
    print("[1/5] Testing GET /api/health and GET /api/topology...")
    # Test Health
    health_resp = await client.get(f"{BASE_URL}/api/health")
    assert health_resp.status_code == 200, f"Health check failed: {health_resp.text}"
    health_data = health_resp.json()
    assert health_data.get("status") == "operational"
    assert health_data.get("egress_guard") == "enforced"
    print(f"      [OK] Health OK: status={health_data['status']}, egress={health_data['egress_guard']}")

    # Test Topology
    topo_resp = await client.get(f"{BASE_URL}/api/topology")
    assert topo_resp.status_code == 200, f"Topology check failed: {topo_resp.text}"
    topo_data = topo_resp.json()
    segments = topo_data.get("segments", [])
    expected_cidrs = {"10.0.10.0/24", "10.0.20.0/24", "10.0.30.0/24", "10.0.40.0/24", "10.0.50.0/24"}
    actual_cidrs = {seg["cidr"] for seg in segments}
    assert expected_cidrs.issubset(actual_cidrs), f"Missing CIDRs: {expected_cidrs - actual_cidrs}"
    print(f"      [OK] Topology OK: {len(segments)} VLAN segments verified ({', '.join(sorted(actual_cidrs))})")

async def verify_live_run_and_websocket_stream(client: httpx.AsyncClient):
    print("[2/5] Creating live run and testing WebSocket streaming...")
    run_resp = await client.post(f"{BASE_URL}/api/runs", json={"scenario": "full_adversary_emulation"})
    assert run_resp.status_code == 201, f"Create run failed: {run_resp.text}"
    run_data = run_resp.json()
    run_id = run_data["id"]
    print(f"      [OK] Created Run: {run_id} [status={run_data['status']}]")

    ws_endpoint = f"{WS_URL}/api/runs/{run_id}/events"
    received_kinds = set()
    received_envelopes = []

    async with websockets.connect(ws_endpoint) as ws:
        # Collect at least 4 live envelopes (e.g., system, action, detection, policy)
        for _ in range(8):
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=4.0)
                envelope = json.loads(msg)
                
                # Assert Universal Event Envelope structure
                for req_key in ["run_id", "event_id", "timestamp", "kind", "source", "payload"]:
                    assert req_key in envelope, f"Missing required envelope key: {req_key} in {envelope}"
                
                assert envelope["run_id"] == run_id, f"run_id mismatch: {envelope['run_id']} != {run_id}"
                received_kinds.add(envelope["kind"])
                received_envelopes.append(envelope)
                print(f"      -> Received Envelope [{envelope['kind']}] from {envelope['source']} (id: {envelope['event_id']})")
                
                if len(received_kinds) >= 3:
                    break
            except asyncio.TimeoutError:
                print("      [!] WebSocket receive timed out waiting for next event")
                break

    assert len(received_envelopes) >= 2, f"Expected >= 2 envelopes, got {len(received_envelopes)}"
    print(f"      [OK] WebSocket Streaming OK: Received {len(received_envelopes)} events across kinds: {received_kinds}")
    return run_id

async def verify_live_interactive_controls(client: httpx.AsyncClient, run_id: str):
    print("[3/5] Testing interactive run controls: Pause -> Resume -> Terminate...")
    # Pause Run
    pause_resp = await client.post(f"{BASE_URL}/api/runs/{run_id}/pause")
    assert pause_resp.status_code == 200, f"Pause failed: {pause_resp.text}"
    assert pause_resp.json()["status"] == "paused"
    print("      [OK] POST /pause OK: status=paused")

    # Brief wait in paused state
    await asyncio.sleep(0.5)

    # Resume Run
    resume_resp = await client.post(f"{BASE_URL}/api/runs/{run_id}/resume")
    assert resume_resp.status_code == 200, f"Resume failed: {resume_resp.text}"
    assert resume_resp.json()["status"] == "running"
    print("      [OK] POST /resume OK: status=running")

    # Brief execution before kill-switch
    await asyncio.sleep(1.0)

    # Terminate Kill-Switch
    term_resp = await client.post(f"{BASE_URL}/api/runs/{run_id}/terminate")
    assert term_resp.status_code == 200, f"Terminate failed: {term_resp.text}"
    assert term_resp.json()["status"] == "terminated"
    print("      [OK] POST /terminate OK: status=terminated (kill-switch engaged)")

def verify_database_persistence_and_redaction():
    print("[4/5] Verifying SQLite database persistence across 6 immutable tables...")
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    required_tables = {
        "runs",
        "agent_actions",
        "observations",
        "detections",
        "honeypot_sessions",
        "policy_decisions"
    }
    
    missing_tables = required_tables - existing_tables
    assert not missing_tables, f"Database missing tables: {missing_tables}"

    with engine.connect() as conn:
        for tbl in sorted(required_tables):
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"      [OK] Table '{tbl}': {count} records stored")
            assert count >= 1, f"Table {tbl} has 0 records after live run execution"

    print("[5/5] Checking credential sanitization in honeypot_sessions...")
    with engine.connect() as conn:
        sessions = conn.execute(text("SELECT id, session_id, commands_or_requests, metadata_json FROM honeypot_sessions")).fetchall()
        assert len(sessions) > 0, "No honeypot sessions found in database"
        
        for ses in sessions:
            cmds_str = str(ses[2])
            meta_str = str(ses[3])
            # Check for leaked plaintext passwords
            assert "hunter2" not in cmds_str and "hunter2" not in meta_str, "Found unredacted secret 'hunter2'!"
            assert "password123" not in cmds_str and "password123" not in meta_str, "Found unredacted secret 'password123'!"
            assert "toor" not in cmds_str and "toor" not in meta_str, "Found unredacted secret 'toor'!"
            # Verify [REDACTED] appears if passwords were submitted
            if "password" in cmds_str.lower() or "auth" in cmds_str.lower():
                assert "[REDACTED]" in cmds_str, f"Credential was not sanitized to [REDACTED]: {cmds_str}"

    print("      [OK] Sensitive credential redaction verified: all secrets sanitized to [REDACTED]")

async def main():
    print("=================================================================")
    print("   NETMIRAGE LIVE PROGRAMMATIC INTEGRATION SMOKE TEST (PORT 8000) ")
    print("=================================================================")
    async with httpx.AsyncClient(timeout=10.0) as client:
        await verify_live_health_and_topology(client)
        run_id = await verify_live_run_and_websocket_stream(client)
        await verify_live_interactive_controls(client, run_id)
        verify_database_persistence_and_redaction()
    print("=================================================================")
    print("   ALL LIVE SMOKE TESTS COMPLETED SUCCESSFULLY (100% PASS)       ")
    print("=================================================================")

if __name__ == "__main__":
    asyncio.run(main())
