from datetime import datetime
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

EventKind = Literal["detection", "action", "observation", "honeypot", "policy", "system"]
EventSource = Literal[
    "protocol-analyzer",
    "action-broker",
    "safety-policy",
    "ai-planner",
    "cowrie-ssh",
    "web-lure",
    "dns-lure",
    "smtp-lure",
    "deception-router",
    "system"
]

class EventEnvelope(BaseModel):
    run_id: str
    event_id: str
    timestamp: str
    kind: EventKind
    source: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class RunCreate(BaseModel):
    scenario: Optional[str] = "full_adversary_emulation"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    threat_score: int
    active_profile: Optional[str]
    next_deception_zone: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    metadata_json: Dict[str, Any]

class AgentActionCreate(BaseModel):
    action_type: str
    target_ip: str
    target_port: int
    parameters: Dict[str, Any] = Field(default_factory=dict)

class AgentActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    timestamp: datetime
    action_type: str
    target_ip: str
    target_port: int
    parameters: Dict[str, Any]
    status: str
    latency_ms: Optional[int]
    output: Optional[Any]

class ObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    timestamp: datetime
    source: str
    source_ip: Optional[str]
    destination_ip: Optional[str]
    protocol: str
    behavior_type: str
    raw_payload: Any
    details: Dict[str, Any]

class DetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    timestamp: datetime
    source_ip: str
    technique_id: str
    technique_name: str
    confidence: float
    evidence: Dict[str, Any]

class HoneypotSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    lure_type: str
    session_id: str
    source_ip: str
    source_port: Optional[int]
    started_at: datetime
    ended_at: Optional[datetime]
    commands_or_requests: List[Any]
    metadata_json: Dict[str, Any]

class PolicyDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    timestamp: datetime
    threat_profile: str
    confidence: float
    decision: str
    target_zone: str
    evidence: Dict[str, Any]

class SystemHealthResponse(BaseModel):
    status: str
    active_runs: int
    lab_mode: str
    version: str
    egress_guard: str

class TopologySegment(BaseModel):
    name: str
    cidr: str
    description: str
    nodes: List[Dict[str, Any]]

class TopologyResponse(BaseModel):
    segments: List[TopologySegment]
    active_lures: List[Dict[str, Any]]
    highlighted_paths: List[Dict[str, Any]]
