# NetMirage: API Specifications & Data Contracts

## Overview

NetMirage provides a synchronous RESTful control plane coupled with a low-latency, bidirectional WebSocket event bus. All communications use strict JSON serialization conforming to Pydantic v2 validation models and OpenAPI 3.1.0 specifications.

Base URL: `http://localhost:8000`  
WebSocket Endpoint: `ws://localhost:8000/api/runs/{run_id}/events`

---

## 1. RESTful API Endpoints

### 1.1. Health & Egress Status (`GET /api/health`)
Verifies API operational status, database connectivity, and zero-egress sandbox policy enforcement.

#### Request
```bash
curl -X GET http://localhost:8000/api/health \
  -H "Accept: application/json"
```

#### Response (`200 OK`)
```json
{
  "status": "operational",
  "database": "connected",
  "active_runs": 1,
  "egress_guard": "enforced",
  "timestamp": "2026-10-18T07:15:30.123456Z"
}
```

---

### 1.2. Lab Topology Query (`GET /api/topology`)
Returns the complete 5-segment virtualized network architecture, subnet CIDRs, gateway IPs, hosted nodes, and deception lures.

#### Request
```bash
curl -X GET http://localhost:8000/api/topology \
  -H "Accept: application/json"
```

#### Response (`200 OK`)
```json
{
  "subnets": [
    {
      "name": "edge",
      "cidr": "10.0.10.0/24",
      "gateway": "10.0.10.1",
      "isolation": "zero-egress",
      "nodes": [
        { "name": "edge-gateway", "ip": "10.0.10.42", "role": "gateway", "type": "node" },
        { "name": "simulated-adversary", "ip": "10.0.10.15", "role": "attacker", "type": "adversary" }
      ]
    },
    {
      "name": "ssh",
      "cidr": "10.0.20.0/24",
      "gateway": "10.0.20.1",
      "isolation": "zero-egress",
      "nodes": [
        { "name": "cowrie-ssh", "ip": "10.0.20.10", "role": "lure", "type": "lure" }
      ]
    },
    {
      "name": "web",
      "cidr": "10.0.30.0/24",
      "gateway": "10.0.30.1",
      "isolation": "zero-egress",
      "nodes": [
        { "name": "web-lure", "ip": "10.0.30.10", "role": "lure", "type": "lure" }
      ]
    },
    {
      "name": "services",
      "cidr": "10.0.40.0/24",
      "gateway": "10.0.40.1",
      "isolation": "zero-egress",
      "nodes": [
        { "name": "internal-dns", "ip": "10.0.40.10", "role": "lure", "type": "lure" },
        { "name": "internal-smtp", "ip": "10.0.40.20", "role": "lure", "type": "lure" }
      ]
    },
    {
      "name": "monitor",
      "cidr": "10.0.50.0/24",
      "gateway": "10.0.50.1",
      "isolation": "zero-egress",
      "nodes": [
        { "name": "telemetry-collector", "ip": "10.0.50.10", "role": "monitor", "type": "collector" },
        { "name": "quarantine-sinkhole", "ip": "10.0.50.99", "role": "sinkhole", "type": "node" }
      ]
    }
  ],
  "routing_rules": [
    {
      "source_cidr": "10.0.10.0/24",
      "target_cidr": "10.0.20.0/24",
      "state": "engaged",
      "active_lure": "10.0.20.10"
    }
  ]
}
```

---

### 1.3. Run Lifecycle Initialization (`POST /api/runs`)
Spawns a new autonomous cyber-range run, initializing state tracking and spinning up the adversary planner worker.

#### Request
```bash
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{
    "active_profile": "reconnaissance"
  }'
```

#### Response (`201 Created`)
```json
{
  "id": "run_20261018_071530_a1b2",
  "created_at": "2026-10-18T07:15:30.456123Z",
  "status": "pending",
  "threat_score": 0,
  "active_profile": "reconnaissance",
  "next_deception_zone": "edge",
  "metadata_json": {}
}
```

---

### 1.4. Interactive Run Controls (`/pause`, `/resume`, `/terminate`)

#### Pause Active Run (`POST /api/runs/{id}/pause`)
Freezes the adversary execution loop without tearing down the virtualized container environment.

```bash
curl -X POST http://localhost:8000/api/runs/run_20261018_071530_a1b2/pause
```

Response (`200 OK`):
```json
{
  "id": "run_20261018_071530_a1b2",
  "status": "paused",
  "threat_score": 10,
  "active_profile": "reconnaissance",
  "next_deception_zone": "ssh"
}
```

#### Resume Paused Run (`POST /api/runs/{id}/resume`)
Unfreezes adversary planning and continues protocol execution.

```bash
curl -X POST http://localhost:8000/api/runs/run_20261018_071530_a1b2/resume
```

Response (`200 OK`):
```json
{
  "id": "run_20261018_071530_a1b2",
  "status": "running",
  "threat_score": 10,
  "active_profile": "reconnaissance",
  "next_deception_zone": "ssh"
}
```

#### Terminate Run / Global Kill Switch (`POST /api/runs/{id}/terminate`)
Immediately terminates adversary execution, revokes container network routes, and permanently locks run state.

```bash
curl -X POST http://localhost:8000/api/runs/run_20261018_071530_a1b2/terminate
```

Response (`200 OK`):
```json
{
  "id": "run_20261018_071530_a1b2",
  "status": "terminated",
  "threat_score": 86,
  "active_profile": "covert_channel",
  "next_deception_zone": "quarantine"
}
```

---

### 1.5. Honeypot Session Detail Inspector (`GET /api/sessions/{id}`)
Fetches granular captured telemetry for an individual honeypot interaction session with sensitive credentials sanitized to `[REDACTED]`.

#### Request
```bash
curl -X GET http://localhost:8000/api/sessions/cowrie-session-001 \
  -H "Accept: application/json"
```

#### Response (`200 OK`)
```json
{
  "id": "cowrie-session-001",
  "run_id": "run_20261018_071530_a1b2",
  "honeypot_type": "cowrie_ssh",
  "source_ip": "10.0.10.15",
  "source_port": 52341,
  "started_at": "2026-10-18T07:15:45.000000Z",
  "ended_at": "2026-10-18T07:15:52.000000Z",
  "commands_or_requests": [
    {
      "user": "root",
      "password": "[REDACTED]",
      "command": "cat /etc/passwd"
    },
    {
      "user": "admin",
      "password": "[REDACTED]",
      "command": "uname -a; whoami"
    }
  ],
  "metadata_json": {
    "ssh_banner": "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.4",
    "kex_algorithms": ["curve25519-sha256", "diffie-hellman-group14-sha256"],
    "lure_ip": "10.0.20.10",
    "lure_port": 2222
  }
}
```

---

## 2. Universal Event Envelope Specification

All real-time streaming over `WS /api/runs/{run_id}/events` and immutable database events conform to the Universal Event Envelope schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UniversalEventEnvelope",
  "type": "object",
  "required": ["run_id", "event_id", "timestamp", "kind", "source", "payload"],
  "properties": {
    "run_id": { "type": "string" },
    "event_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "kind": { 
      "type": "string", 
      "enum": ["system", "action", "observation", "detection", "honeypot", "policy"] 
    },
    "source": { "type": "string" },
    "payload": { "type": "object" }
  }
}
```

### Event Kind Payloads

#### Kind: `action`
Emitted by the Action Broker whenever an adversary action is evaluated and executed:
```json
{
  "run_id": "run_20261018_071530_a1b2",
  "event_id": "evt_act_001",
  "timestamp": "2026-10-18T07:15:32.100000Z",
  "kind": "action",
  "source": "action-broker",
  "payload": {
    "action_id": "act_discover_01",
    "action_type": "discover_lab_services",
    "target_ip": "10.0.10.42",
    "target_port": 80,
    "parameters": { "scan_type": "syn_stealth", "ports": [22, 53, 80] },
    "status": "completed",
    "latency_ms": 14,
    "output": { "open_ports": [80], "state": "active" }
  }
}
```

#### Kind: `detection`
Emitted by the MITRE ATT&CK Behavioral Classifier:
```json
{
  "run_id": "run_20261018_071530_a1b2",
  "event_id": "evt_det_002",
  "timestamp": "2026-10-18T07:15:35.200000Z",
  "kind": "detection",
  "source": "mitre-classifier",
  "payload": {
    "detection_id": "det_t1046_01",
    "source_ip": "10.0.10.15",
    "technique_id": "T1046",
    "technique_name": "Network Service Discovery",
    "confidence": 0.90,
    "threat_score": 35,
    "active_profile": "reconnaissance",
    "evidence": { "syn_packets": 12, "scanned_subnets": ["10.0.10.0/24"] }
  }
}
```

#### Kind: `policy`
Emitted by the Dynamic Deception Engine during route updates:
```json
{
  "run_id": "run_20261018_071530_a1b2",
  "event_id": "evt_pol_003",
  "timestamp": "2026-10-18T07:15:40.500000Z",
  "kind": "policy",
  "source": "deception-engine",
  "payload": {
    "policy_id": "pol_reroute_01",
    "decision": "divert",
    "threat_profile": "credential_probing",
    "confidence": 0.85,
    "target_zone": "ssh",
    "evidence": { "target_lure": "10.0.20.10", "rule": "redirect_port_2222" }
  }
}
```

---

## 3. Action Broker JSON Execution Contract

The Action Broker strictly accepts parameters according to the following schema:

```json
{
  "type": "object",
  "required": ["action_type", "target_ip", "target_port", "parameters"],
  "properties": {
    "action_type": {
      "type": "string",
      "enum": [
        "discover_lab_services",
        "resolve_dns",
        "connect_tcp",
        "request_http",
        "attempt_ssh_to_lure",
        "send_icmp_probe",
        "inspect_session_output"
      ]
    },
    "target_ip": {
      "type": "string",
      "pattern": "^10\\.0\\.(10|20|30|40|50)\\.[0-9]{1,3}$"
    },
    "target_port": {
      "type": "integer",
      "enum": [22, 2222, 53, 80, 8080, 25, 587]
    },
    "parameters": {
      "type": "object",
      "additionalProperties": true
    }
  }
}
```
