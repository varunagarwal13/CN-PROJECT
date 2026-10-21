import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from app_build.backend.core.planner import planner
from app_build.backend.core.safety_policy import safety_policy
from app_build.backend.core.action_broker import action_broker
from app_build.backend.intel.honeypots import honeypot_normalizer
from app_build.backend.intel.analyzer import protocol_analyzer
from app_build.backend.intel.mitre_mapper import mitre_mapper
from app_build.backend.intel.deception_policy import deception_policy
from app_build.backend.event_bus import event_bus
from app_build.backend.db import SessionLocal
from app_build.backend import models
from app_build.backend.intel.pcap_exporter import generate_pcap_from_actions

class LabRunner:
    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._step_counters: Dict[str, int] = {}
        self._prior_actions: Dict[str, list] = {}
        self._prior_observations: Dict[str, list] = {}

    def is_running(self, run_id: str) -> bool:
        task = self._active_tasks.get(run_id)
        return task is not None and not task.done()

    def start_run(self, run_id: str):
        if self.is_running(run_id):
            return
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._run_loop(run_id))
            self._active_tasks[run_id] = task
        except RuntimeError:
            pass

    def pause_run(self, run_id: str):
        db = SessionLocal()
        try:
            run = db.query(models.Run).filter(models.Run.id == run_id).first()
            if run and run.status == "running":
                run.status = "paused"
                db.commit()
        finally:
            db.close()

    def resume_run(self, run_id: str):
        db = SessionLocal()
        try:
            run = db.query(models.Run).filter(models.Run.id == run_id).first()
            if run and run.status == "paused":
                run.status = "running"
                db.commit()
        finally:
            db.close()

    def terminate_run(self, run_id: str):
        db = SessionLocal()
        try:
            run = db.query(models.Run).filter(models.Run.id == run_id).first()
            if run:
                run.status = "terminated"
                run.ended_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

        task = self._active_tasks.get(run_id)
        if task and not task.done():
            task.cancel()

    async def _run_loop(self, run_id: str):
        stage_index = 0
        self._prior_actions[run_id] = []
        self._prior_observations[run_id] = []
        cumulative_threat_score = 0

        # Mark run as running
        db = SessionLocal()
        try:
            run = db.query(models.Run).filter(models.Run.id == run_id).first()
            if run:
                run.status = "running"
                run.started_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

        await event_bus.emit(
            run_id=run_id,
            kind="system",
            source="system",
            payload={"status": "running", "message": f"Cyber-range emulation started for {run_id}"}
        )

        max_stages = len(planner.DETERMINISTIC_PROGRESSION)

        try:
            while stage_index < max_stages:
                # 1. Check database for status updates (e.g. Pause, Terminate Kill Switch)
                db = SessionLocal()
                run_status = "running"
                try:
                    run = db.query(models.Run).filter(models.Run.id == run_id).first()
                    if run:
                        run_status = run.status
                finally:
                    db.close()

                if run_status == "terminated":
                    break
                elif run_status == "paused":
                    await asyncio.sleep(0.1)
                    continue

                # 2. Layer 1: Observation Summary
                summary = planner.build_observation_summary(
                    stage_index=stage_index,
                    prior_actions=self._prior_actions[run_id],
                    prior_observations=self._prior_observations[run_id]
                )

                # 3. Layer 2: Planner (Safe Action Request)
                action_plan = planner.plan_next_action(summary, stage_index)
                action_id = f"act_{uuid.uuid4().hex[:8]}"

                # 4. Layer 3: Safety Policy Evaluation
                db = SessionLocal()
                policy_eval = safety_policy.evaluate_action(
                    run_id=run_id,
                    action_type=action_plan.action_type,
                    target_ip=action_plan.target_ip,
                    target_port=action_plan.target_port,
                    db=db,
                    parameters=action_plan.parameters
                )
                db.close()

                if not policy_eval.allowed:
                    await event_bus.emit(
                        run_id=run_id,
                        kind="action",
                        source="safety-policy",
                        payload={
                            "action_id": action_id,
                            "action_type": action_plan.action_type,
                            "target_ip": action_plan.target_ip,
                            "target_port": action_plan.target_port,
                            "parameters": action_plan.parameters,
                            "status": "denied",
                            "reason": policy_eval.reason
                        }
                    )
                    break

                # 5. Action Broker Execution
                broker_res = await action_broker.execute_action(
                    run_id=run_id,
                    action_type=action_plan.action_type,
                    target_ip=action_plan.target_ip,
                    target_port=action_plan.target_port,
                    parameters=action_plan.parameters
                )

                action_record = {
                    "action_id": action_id,
                    "action_type": action_plan.action_type,
                    "target_ip": action_plan.target_ip,
                    "target_port": action_plan.target_port,
                    "status": broker_res["status"],
                    "latency_ms": broker_res["latency_ms"],
                    "output": broker_res["output"]
                }
                self._prior_actions[run_id].append(action_record)

                # Live standard Wireshark PCAP capture update
                try:
                    generate_pcap_from_actions(self._prior_actions[run_id], run_id=run_id)
                except Exception as pcap_err:
                    print(f"[LAB-RUNNER] PCAP write error: {pcap_err}")

                await event_bus.emit(
                    run_id=run_id,
                    kind="action",
                    source="action-broker",
                    payload={
                        "action_id": action_id,
                        "action_type": action_plan.action_type,
                        "target_ip": action_plan.target_ip,
                        "target_port": action_plan.target_port,
                        "parameters": action_plan.parameters,
                        "status": broker_res["status"],
                        "latency_ms": broker_res["latency_ms"],
                        "output": broker_res["output"]
                    }
                )

                # 6. Honeypot Ingestion (with Credential Redaction)
                if action_plan.action_type == "attempt_ssh_to_lure":
                    hp_data = honeypot_normalizer.normalize_cowrie_event(
                        run_id=run_id,
                        session_id=f"ses_ssh_{uuid.uuid4().hex[:6]}",
                        source_ip="10.0.10.15",
                        source_port=52341,
                        username=action_plan.parameters.get("username", "root"),
                        password=action_plan.parameters.get("password"),
                        command=action_plan.parameters.get("command", "uname -a")
                    )
                    await event_bus.emit(
                        run_id=run_id,
                        kind="honeypot",
                        source="cowrie-ssh",
                        payload=hp_data
                    )
                elif action_plan.action_type == "request_http":
                    hp_data = honeypot_normalizer.normalize_web_event(
                        run_id=run_id,
                        session_id=f"ses_web_{uuid.uuid4().hex[:6]}",
                        source_ip="10.0.10.15",
                        method=action_plan.parameters.get("method", "GET"),
                        path=action_plan.parameters.get("path", "/"),
                        user_agent="Mozilla/5.0 (NetMirage Adversary Probe)"
                    )
                    await event_bus.emit(
                        run_id=run_id,
                        kind="honeypot",
                        source="web-lure",
                        payload=hp_data
                    )
                elif action_plan.action_type == "resolve_dns":
                    hp_data = honeypot_normalizer.normalize_dns_event(
                        run_id=run_id,
                        session_id=f"ses_dns_{uuid.uuid4().hex[:6]}",
                        source_ip="10.0.10.15",
                        query_domain=action_plan.parameters.get("query", "ssh.corp.internal"),
                        record_type=action_plan.parameters.get("record_type", "A")
                    )
                    await event_bus.emit(
                        run_id=run_id,
                        kind="honeypot",
                        source="dns-lure",
                        payload=hp_data
                    )

                # 7. Protocol Telemetry & Observation
                observations = protocol_analyzer.analyze_action_event(
                    run_id=run_id,
                    action={
                        "action_type": action_plan.action_type,
                        "target_ip": action_plan.target_ip,
                        "target_port": action_plan.target_port,
                        "parameters": action_plan.parameters
                    }
                )

                for obs in observations:
                    self._prior_observations[run_id].append(obs)
                    await event_bus.emit(
                        run_id=run_id,
                        kind="observation",
                        source="protocol-analyzer",
                        payload=obs
                    )

                    # 8. MITRE ATT&CK Mapping (with Dynamic Confidence Calculation)
                    detection = mitre_mapper.classify_observation(obs, run_id=run_id)
                    if detection:
                        # Dynamic weighted threat scoring
                        SEVERITY_WEIGHTS = {
                            "T1110": 30.0,
                            "T1021.004": 25.0,
                            "T1557": 25.0,
                            "T1071.004": 20.0,
                            "T1190": 20.0,
                            "T1046": 15.0,
                            "T1595": 15.0,
                            "T1095": 15.0
                        }
                        weight = SEVERITY_WEIGHTS.get(detection.technique_id, 15.0)
                        cumulative_threat_score = min(100, cumulative_threat_score + int(detection.confidence * weight * 0.8))
                        det_id = f"det_{uuid.uuid4().hex[:8]}"

                        await event_bus.emit(
                            run_id=run_id,
                            kind="detection",
                            source="protocol-analyzer",
                            payload={
                                "detection_id": det_id,
                                "source_ip": obs.get("source_ip", "10.0.10.15"),
                                "technique_id": detection.technique_id,
                                "technique_name": detection.technique_name,
                                "confidence": detection.confidence,
                                "threat_profile": detection.threat_profile,
                                "threat_score": cumulative_threat_score,
                                "active_profile": detection.threat_profile,
                                "evidence": detection.evidence
                            }
                        )

                        # 9. Dynamic Deception Policy Routing
                        deception_decision = deception_policy.evaluate_policy(
                            threat_profile=detection.threat_profile,
                            confidence=detection.confidence,
                            detection_evidence=detection.evidence
                        )

                        await event_bus.emit(
                            run_id=run_id,
                            kind="policy",
                            source="deception-router",
                            payload={
                                "policy_id": f"pol_{uuid.uuid4().hex[:8]}",
                                "threat_profile": deception_decision.threat_profile,
                                "confidence": deception_decision.confidence,
                                "decision": deception_decision.decision,
                                "target_zone": deception_decision.target_zone,
                                "evidence": deception_decision.evidence
                            }
                        )

                stage_index += 1
                await asyncio.sleep(0.05)  # Pace between steps

            # Mark complete if still running
            db = SessionLocal()
            try:
                run = db.query(models.Run).filter(models.Run.id == run_id).first()
                if run and run.status == "running":
                    run.status = "completed"
                    run.ended_at = datetime.now(timezone.utc)
                    db.commit()
                    await event_bus.emit(
                        run_id=run_id,
                        kind="system",
                        source="system",
                        payload={"status": "completed", "message": "Emulation scenario completed successfully"}
                    )
            finally:
                db.close()

        except asyncio.CancelledError:
            db = SessionLocal()
            try:
                run = db.query(models.Run).filter(models.Run.id == run_id).first()
                if run and run.status != "terminated":
                    run.status = "terminated"
                    run.ended_at = datetime.now(timezone.utc)
                    db.commit()
            finally:
                db.close()
            await event_bus.emit(
                run_id=run_id,
                kind="system",
                source="system",
                payload={"status": "terminated", "message": "Run terminated by global kill switch"}
            )
        except Exception as e:
            await event_bus.emit(
                run_id=run_id,
                kind="system",
                source="system",
                payload={"status": "failed", "error": str(e)}
            )

lab_runner = LabRunner()
