import asyncio
from datetime import datetime, timezone
import uuid
from typing import Dict, Set, List, Optional, Any
from sqlalchemy.orm import Session
from app_build.backend.schemas import EventEnvelope
from app_build.backend.db import SessionLocal
from app_build.backend import models

class EventBus:
    def __init__(self):
        # run_id -> Set[asyncio.Queue]
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
        # run_id -> List[EventEnvelope]
        self._history: Dict[str, List[EventEnvelope]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, run_id: str) -> asyncio.Queue:
        async with self._lock:
            queue: asyncio.Queue = asyncio.Queue()
            if run_id not in self._subscribers:
                self._subscribers[run_id] = set()
            self._subscribers[run_id].add(queue)

            # Replay historical events for this run to the subscriber
            history = self._history.get(run_id, [])
            for env in history:
                queue.put_nowait(env)

            return queue

    async def unsubscribe(self, run_id: str, queue: asyncio.Queue):
        async with self._lock:
            if run_id in self._subscribers:
                self._subscribers[run_id].discard(queue)
                if not self._subscribers[run_id]:
                    del self._subscribers[run_id]

    async def publish(self, run_id: str, envelope: EventEnvelope, db: Optional[Session] = None):
        # 1. Distribute to all active subscribers and append to history
        async with self._lock:
            if run_id not in self._history:
                self._history[run_id] = []
            self._history[run_id].append(envelope)
            queues = list(self._subscribers.get(run_id, set()))

        for q in queues:
            try:
                q.put_nowait(envelope)
            except asyncio.QueueFull:
                pass

        # 2. Persist to database
        self._persist_event(run_id, envelope, db)

    def _persist_event(self, run_id: str, envelope: EventEnvelope, db: Optional[Session] = None):
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            run = db.query(models.Run).filter(models.Run.id == run_id).first()
            if not run:
                return

            payload = envelope.payload
            kind = envelope.kind

            if kind == "system":
                new_status = payload.get("status")
                if new_status:
                    run.status = new_status
                if "threat_score" in payload:
                    run.threat_score = int(payload["threat_score"])
                if "active_profile" in payload:
                    run.active_profile = payload["active_profile"]
                if "next_deception_zone" in payload:
                    run.next_deception_zone = payload["next_deception_zone"]
                db.commit()

            elif kind == "action":
                act_id = payload.get("action_id", f"act_{uuid.uuid4().hex[:8]}")
                action = db.query(models.AgentAction).filter(models.AgentAction.id == act_id).first()
                if not action:
                    action = models.AgentAction(
                        id=act_id,
                        run_id=run_id,
                        action_type=payload.get("action_type", "unknown"),
                        target_ip=payload.get("target_ip", "10.0.10.42"),
                        target_port=payload.get("target_port", 80),
                        parameters=payload.get("parameters", {}),
                        status=payload.get("status", "allowed"),
                        latency_ms=payload.get("latency_ms"),
                        output=payload.get("output")
                    )
                    db.add(action)
                else:
                    action.status = payload.get("status", action.status)
                    if "latency_ms" in payload:
                        action.latency_ms = payload["latency_ms"]
                    if "output" in payload:
                        action.output = payload["output"]
                db.commit()

            elif kind == "observation":
                obs_id = payload.get("observation_id", f"obs_{uuid.uuid4().hex[:8]}")
                obs = models.Observation(
                    id=obs_id,
                    run_id=run_id,
                    source=envelope.source,
                    source_ip=payload.get("source_ip"),
                    destination_ip=payload.get("destination_ip"),
                    protocol=payload.get("protocol", "TCP"),
                    behavior_type=payload.get("behavior_type", "unknown"),
                    raw_payload=payload.get("raw_payload", {}),
                    details=payload.get("details", {})
                )
                db.add(obs)
                db.commit()

            elif kind == "detection":
                det_id = payload.get("detection_id", f"det_{uuid.uuid4().hex[:8]}")
                det = models.Detection(
                    id=det_id,
                    run_id=run_id,
                    source_ip=payload.get("source_ip", "unknown"),
                    technique_id=payload.get("technique_id", "T1046"),
                    technique_name=payload.get("technique_name", "Network Service Discovery"),
                    confidence=float(payload.get("confidence", 0.5)),
                    evidence=payload.get("evidence", {})
                )
                db.add(det)
                if "threat_score" in payload:
                    run.threat_score = min(100, max(0, int(payload["threat_score"])))
                if "active_profile" in payload:
                    run.active_profile = payload["active_profile"]
                db.commit()

            elif kind == "honeypot":
                ses_id = payload.get("session_id", f"ses_{uuid.uuid4().hex[:8]}")
                session = db.query(models.HoneypotSession).filter(models.HoneypotSession.id == ses_id).first()
                if not session:
                    session = models.HoneypotSession(
                        id=ses_id,
                        run_id=run_id,
                        lure_type=payload.get("lure_type", "cowrie_ssh"),
                        session_id=ses_id,
                        source_ip=payload.get("source_ip", "10.0.10.42"),
                        source_port=payload.get("source_port"),
                        commands_or_requests=payload.get("commands_or_requests", []),
                        metadata_json=payload.get("metadata", {})
                    )
                    db.add(session)
                else:
                    if "commands_or_requests" in payload:
                        session.commands_or_requests = payload["commands_or_requests"]
                    if payload.get("ended"):
                        session.ended_at = datetime.now(timezone.utc)
                db.commit()

            elif kind == "policy":
                pol_id = payload.get("policy_id", f"pol_{uuid.uuid4().hex[:8]}")
                pol = models.PolicyDecision(
                    id=pol_id,
                    run_id=run_id,
                    threat_profile=payload.get("threat_profile", "reconnaissance"),
                    confidence=float(payload.get("confidence", 0.8)),
                    decision=payload.get("decision", "route_to_lure"),
                    target_zone=payload.get("target_zone", "ssh-lure"),
                    evidence=payload.get("evidence", {})
                )
                db.add(pol)
                run.next_deception_zone = payload.get("target_zone", run.next_deception_zone)
                db.commit()

        except Exception:
            db.rollback()
        finally:
            if should_close:
                db.close()

    async def emit(self, run_id: str, kind: str, source: str, payload: Dict[str, Any], db: Optional[Session] = None) -> EventEnvelope:
        envelope = EventEnvelope(
            run_id=run_id,
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            kind=kind,
            source=source,
            payload=payload
        )
        await self.publish(run_id, envelope, db)
        return envelope

event_bus = EventBus()
