from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    JSON,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from app_build.backend.db import Base

def utcnow():
    return datetime.now(timezone.utc)

class Run(Base):
    __tablename__ = "runs"

    id = Column(String(64), primary_key=True, index=True)
    status = Column(String(32), default="pending", index=True)  # pending | running | paused | terminated | completed
    threat_score = Column(Integer, default=0)
    active_profile = Column(String(64), nullable=True)
    next_deception_zone = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    metadata_json = Column(JSON, default=dict)

    actions = relationship("AgentAction", back_populates="run", cascade="all, delete-orphan")
    observations = relationship("Observation", back_populates="run", cascade="all, delete-orphan")
    detections = relationship("Detection", back_populates="run", cascade="all, delete-orphan")
    honeypot_sessions = relationship("HoneypotSession", back_populates="run", cascade="all, delete-orphan")
    policy_decisions = relationship("PolicyDecision", back_populates="run", cascade="all, delete-orphan")

class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("runs.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=utcnow)
    action_type = Column(String(64), nullable=False)
    target_ip = Column(String(64), nullable=False)
    target_port = Column(Integer, nullable=False)
    parameters = Column(JSON, default=dict)
    status = Column(String(32), nullable=False)  # allowed | denied | timed_out | completed
    latency_ms = Column(Integer, nullable=True)
    output = Column(JSON, nullable=True)

    run = relationship("Run", back_populates="actions")

class Observation(Base):
    __tablename__ = "observations"

    id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("runs.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=utcnow)
    source = Column(String(64), nullable=False)
    source_ip = Column(String(64), nullable=True)
    destination_ip = Column(String(64), nullable=True)
    protocol = Column(String(32), nullable=False)
    behavior_type = Column(String(64), nullable=False)
    raw_payload = Column(JSON, default=dict)
    details = Column(JSON, default=dict)

    run = relationship("Run", back_populates="observations")

class Detection(Base):
    __tablename__ = "detections"

    id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("runs.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=utcnow)
    source_ip = Column(String(64), nullable=False)
    technique_id = Column(String(32), nullable=False)  # e.g., T1046
    technique_name = Column(String(128), nullable=False)
    confidence = Column(Float, nullable=False)
    evidence = Column(JSON, default=dict)

    run = relationship("Run", back_populates="detections")

class HoneypotSession(Base):
    __tablename__ = "honeypot_sessions"

    id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("runs.id"), nullable=False, index=True)
    lure_type = Column(String(64), nullable=False)  # cowrie_ssh | web_lure | dns_lure | smtp_lure
    session_id = Column(String(64), nullable=False, index=True)
    source_ip = Column(String(64), nullable=False)
    source_port = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=utcnow)
    ended_at = Column(DateTime, nullable=True)
    commands_or_requests = Column(JSON, default=list)  # Sensitive values redacted as [REDACTED]
    metadata_json = Column(JSON, default=dict)

    run = relationship("Run", back_populates="honeypot_sessions")

class PolicyDecision(Base):
    __tablename__ = "policy_decisions"

    id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("runs.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=utcnow)
    threat_profile = Column(String(64), nullable=False)
    confidence = Column(Float, nullable=False)
    decision = Column(String(128), nullable=False)
    target_zone = Column(String(64), nullable=False)
    evidence = Column(JSON, default=dict)

    run = relationship("Run", back_populates="policy_decisions")
