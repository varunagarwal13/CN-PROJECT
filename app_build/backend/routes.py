import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app_build.backend.db import get_db, SessionLocal
from app_build.backend import models, schemas
from app_build.backend.event_bus import event_bus
from app_build.backend.orchestration.lab_runner import lab_runner
from app_build.backend.intel.honeypots import redact_credentials
from app_build.backend.core.lab_services import lab_services
from app_build.backend.intel.pcap_exporter import generate_pcap_from_actions, PCAP_OUTPUT_PATH

router = APIRouter(prefix="/api")

@router.get("/health", response_model=schemas.SystemHealthResponse)
def get_health(db: Session = Depends(get_db)):
    active_runs_count = db.query(models.Run).filter(models.Run.status == "running").count()
    return schemas.SystemHealthResponse(
        status="operational",
        active_runs=active_runs_count,
        lab_mode="zero-egress-emulated",
        version="1.0.0",
        egress_guard="enforced"
    )

@router.get("/topology", response_model=schemas.TopologyResponse)
def get_topology(run_id: Optional[str] = None, db: Session = Depends(get_db)):
    segments = [
        schemas.TopologySegment(
            name="edge",
            cidr="10.0.10.0/24",
            description="Ingress boundary & perimeter gateway",
            nodes=[
                {"id": "node_edge_gw", "name": "Edge Gateway", "ip": "10.0.10.42", "role": "perimeter_router", "status": "active"},
                {"id": "node_adversary", "name": "Simulated Adversary", "ip": "10.0.10.15", "role": "attacker_ingress", "status": "active"}
            ]
        ),
        schemas.TopologySegment(
            name="ssh",
            cidr="10.0.20.0/24",
            description="Cowrie SSH medium-interaction decoy subnet",
            nodes=[
                {"id": "node_cowrie_ssh", "name": "Cowrie SSH Lure", "ip": "10.0.20.10", "role": "honeypot", "status": "armed"}
            ]
        ),
        schemas.TopologySegment(
            name="web",
            cidr="10.0.30.0/24",
            description="Web portal lure & administrative decoys",
            nodes=[
                {"id": "node_web_lure", "name": "Web Decoy Portal", "ip": "10.0.30.10", "role": "honeypot", "status": "armed"}
            ]
        ),
        schemas.TopologySegment(
            name="services",
            cidr="10.0.40.0/24",
            description="Core DNS & SMTP infrastructure honeypots",
            nodes=[
                {"id": "node_dns_lure", "name": "Internal DNS Lure", "ip": "10.0.40.10", "role": "honeypot", "status": "armed"},
                {"id": "node_smtp_lure", "name": "Internal SMTP Lure", "ip": "10.0.40.20", "role": "honeypot", "status": "armed"}
            ]
        ),
        schemas.TopologySegment(
            name="monitor",
            cidr="10.0.50.0/24",
            description="Passive telemetry collector & quarantine sandbox",
            nodes=[
                {"id": "node_collector", "name": "Telemetry Collector", "ip": "10.0.50.10", "role": "sensor", "status": "active"},
                {"id": "node_quarantine", "name": "Quarantine Sinkhole", "ip": "10.0.50.99", "role": "sinkhole", "status": "standby"}
            ]
        )
    ]

    active_lures = [
        {"name": "Cowrie SSH Lure", "ip": "10.0.20.10", "ports": [22, 2222], "vlan": "ssh", "type": "medium_interaction"},
        {"name": "Web Decoy Portal", "ip": "10.0.30.10", "ports": [80, 8080], "vlan": "web", "type": "http_decoy"},
        {"name": "DNS Honeynet Tap", "ip": "10.0.40.10", "ports": [53], "vlan": "services", "type": "dns_tap"},
        {"name": "SMTP Decoy Server", "ip": "10.0.40.20", "ports": [25, 587], "vlan": "services", "type": "smtp_decoy"}
    ]

    highlighted_paths = []
    if run_id:
        run = db.query(models.Run).filter(models.Run.id == run_id).first()
        if run:
            target_zone = run.next_deception_zone or "edge"
            zone_ip_map = {
                "edge": "10.0.10.42",
                "ssh-lure": "10.0.20.10",
                "web-lure": "10.0.30.10",
                "services-lure": "10.0.40.20",
                "dns-lure": "10.0.40.10",
                "quarantine": "10.0.50.99"
            }
            dst_ip = zone_ip_map.get(target_zone, "10.0.20.10")
            highlighted_paths.append({
                "source": "10.0.10.15",
                "destination": dst_ip,
                "target_zone": target_zone,
                "threat_score": run.threat_score,
                "status": "diverted" if target_zone != "edge" else "direct"
            })
    else:
        highlighted_paths.append({
            "source": "10.0.10.15",
            "destination": "10.0.10.42",
            "target_zone": "edge",
            "threat_score": 0,
            "status": "direct"
        })

    return schemas.TopologyResponse(
        segments=segments,
        active_lures=active_lures,
        highlighted_paths=highlighted_paths
    )

@router.get("/sessions/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.HoneypotSession).filter(models.HoneypotSession.id == session_id).first()
    if session:
        return {
            "id": session.id,
            "run_id": session.run_id,
            "lure_type": session.lure_type,
            "session_id": session.session_id,
            "source_ip": session.source_ip,
            "source_port": session.source_port,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "commands_or_requests": redact_credentials(session.commands_or_requests),
            "metadata_json": redact_credentials(session.metadata_json)
        }

    sessions = db.query(models.HoneypotSession).filter(models.HoneypotSession.run_id == session_id).all()
    if sessions:
        return [
            {
                "id": s.id,
                "run_id": s.run_id,
                "lure_type": s.lure_type,
                "session_id": s.session_id,
                "source_ip": s.source_ip,
                "source_port": s.source_port,
                "started_at": s.started_at,
                "ended_at": s.ended_at,
                "commands_or_requests": redact_credentials(s.commands_or_requests),
                "metadata_json": redact_credentials(s.metadata_json)
            }
            for s in sessions
        ]

    raise HTTPException(status_code=404, detail="Honeypot session not found")

@router.get("/runs", response_model=List[schemas.RunResponse])
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(models.Run).order_by(models.Run.created_at.desc()).all()
    return runs

@router.get("/runs/{run_id}", response_model=schemas.RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(models.Run).filter(models.Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.post("/runs", response_model=schemas.RunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(payload: Optional[schemas.RunCreate] = None, db: Session = Depends(get_db)):
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"run_{date_str}_{uuid.uuid4().hex[:4]}"

    metadata = (payload.metadata if payload else None) or {}
    scenario = (payload.scenario if payload else None) or "full_adversary_emulation"
    metadata["scenario"] = scenario

    new_run = models.Run(
        id=run_id,
        status="pending",
        threat_score=0,
        active_profile=None,
        next_deception_zone="edge",
        created_at=datetime.now(timezone.utc),
        metadata_json=metadata
    )
    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    # Boot real Docker Compose lab virtual networks
    asyncio.create_task(asyncio.to_thread(lab_services.start_docker_lab))
    lab_runner.start_run(run_id)

    return new_run

@router.post("/runs/{run_id}/pause", response_model=schemas.RunResponse)
async def pause_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(models.Run).filter(models.Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    run.status = "paused"
    db.commit()
    db.refresh(run)
    lab_runner.pause_run(run_id)
    return run

@router.post("/runs/{run_id}/resume", response_model=schemas.RunResponse)
async def resume_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(models.Run).filter(models.Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    run.status = "running"
    db.commit()
    db.refresh(run)
    lab_runner.resume_run(run_id)
    return run

@router.post("/runs/{run_id}/terminate", response_model=schemas.RunResponse)
async def terminate_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(models.Run).filter(models.Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    run.status = "terminated"
    run.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    lab_runner.terminate_run(run_id)
    # Tear down Docker Compose lab virtual networks
    asyncio.create_task(asyncio.to_thread(lab_services.stop_docker_lab))
    return run

@router.get("/runs/{run_id}/actions", response_model=List[schemas.AgentActionResponse])
def get_run_actions(run_id: str, db: Session = Depends(get_db)):
    actions = db.query(models.AgentAction).filter(models.AgentAction.run_id == run_id).order_by(models.AgentAction.timestamp.asc()).all()
    return actions

@router.get("/runs/{run_id}/detections", response_model=List[schemas.DetectionResponse])
def get_run_detections(run_id: str, db: Session = Depends(get_db)):
    detections = db.query(models.Detection).filter(models.Detection.run_id == run_id).order_by(models.Detection.timestamp.asc()).all()
    return detections

@router.get("/runs/{run_id}/policies", response_model=List[schemas.PolicyDecisionResponse])
def get_run_policies(run_id: str, db: Session = Depends(get_db)):
    policies = db.query(models.PolicyDecision).filter(models.PolicyDecision.run_id == run_id).order_by(models.PolicyDecision.timestamp.asc()).all()
    return policies

@router.get("/runs/{run_id}/sessions", response_model=List[schemas.HoneypotSessionResponse])
def get_run_sessions(run_id: str, db: Session = Depends(get_db)):
    sessions = db.query(models.HoneypotSession).filter(models.HoneypotSession.run_id == run_id).order_by(models.HoneypotSession.started_at.asc()).all()
    return [
        {
            "id": s.id,
            "run_id": s.run_id,
            "lure_type": s.lure_type,
            "session_id": s.session_id,
            "source_ip": s.source_ip,
            "source_port": s.source_port,
            "started_at": s.started_at,
            "ended_at": s.ended_at,
            "commands_or_requests": redact_credentials(s.commands_or_requests),
            "metadata_json": redact_credentials(s.metadata_json)
        }
        for s in sessions
    ]

@router.get("/runs/{run_id}/pcap")
def download_run_pcap(run_id: str, db: Session = Depends(get_db)):
    from app_build.backend.intel.pcap_exporter import LATEST_PCAP_PATH
    if run_id == "latest":
        return download_latest_pcap()
    actions = db.query(models.AgentAction).filter(models.AgentAction.run_id == run_id).order_by(models.AgentAction.timestamp.asc()).all()
    actions_dict = [
        {
            "action_type": a.action_type,
            "target_ip": a.target_ip,
            "target_port": a.target_port,
            "parameters": a.parameters,
            "output": a.output
        }
        for a in actions
    ]
    pcap_path = generate_pcap_from_actions(actions_dict, run_id=run_id)
    return FileResponse(
        path=pcap_path,
        media_type="application/vnd.tcpdump.pcap",
        filename=f"netmirage_{run_id}.pcap"
    )

@router.get("/pcap/latest")
def download_latest_pcap():
    from app_build.backend.intel.pcap_exporter import LATEST_PCAP_PATH
    if not LATEST_PCAP_PATH.exists():
        generate_pcap_from_actions([
            {"action_type": "discover_lab_services", "target_ip": "10.0.10.42", "target_port": 80},
            {"action_type": "resolve_dns", "target_ip": "10.0.40.10", "target_port": 53, "parameters": {"query": "ssh.corp.internal"}},
            {"action_type": "request_http", "target_ip": "10.0.30.10", "target_port": 80, "parameters": {"path": "/admin/login"}},
            {"action_type": "attempt_ssh_to_lure", "target_ip": "10.0.20.10", "target_port": 22}
        ], run_id="latest")
    return FileResponse(
        path=str(LATEST_PCAP_PATH),
        media_type="application/vnd.tcpdump.pcap",
        filename="netmirage_latest_run.pcap"
    )

@router.websocket("/runs/{run_id}/events")
async def websocket_events(websocket: WebSocket, run_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    queue = await event_bus.subscribe(run_id)

    try:
        run = db.query(models.Run).filter(models.Run.id == run_id).first()
        init_envelope = schemas.EventEnvelope(
            run_id=run_id,
            event_id=f"evt_init_{uuid.uuid4().hex[:6]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            kind="system",
            source="system",
            payload={
                "status": run.status if run else "unknown",
                "threat_score": run.threat_score if run else 0,
                "active_profile": run.active_profile if run else None,
                "next_deception_zone": run.next_deception_zone if run else "edge"
            }
        )
        await websocket.send_text(init_envelope.model_dump_json())

        while True:
            try:
                envelope: schemas.EventEnvelope = await asyncio.wait_for(queue.get(), timeout=0.5)
                await websocket.send_text(envelope.model_dump_json())
            except asyncio.TimeoutError:
                run = db.query(models.Run).filter(models.Run.id == run_id).first()
                if run and run.status in ("completed", "terminated") and queue.empty():
                    break
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await event_bus.unsubscribe(run_id, queue)

