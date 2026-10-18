# Skill 01: Database Models & Universal Event Contracts

## Purpose
Defines the SQLAlchemy 2.0 schema for NetMirage's 6 immutable data stores, the Universal Event Envelope schema, and data serializability standards.

## 1. Universal Event Envelope Schema
All WebSocket messages and cross-subsystem event bus transmissions conform strictly to:
```json
{
  "run_id": "run_2026_09_07_001",
  "event_id": "evt_00042",
  "timestamp": "2026-09-07T16:30:00Z",
  "kind": "detection | action | observation | honeypot | policy | system",
  "source": "protocol-analyzer | action-broker | safety-policy | ai-planner | cowrie-ssh | deception-router",
  "payload": {}
}
```

## 2. Six Immutable Database Tables
1. **`runs`**: Tracks cyber-range execution lifecycle, threat score, active profile, and next deception target zone.
   - `id` (VARCHAR PK): e.g. `run_YYYYMMDD_HHMMSS_xxxx`
   - `status` (VARCHAR): `pending | running | paused | terminated | completed`
   - `threat_score` (INTEGER): `0` to `100`
   - `active_profile` (VARCHAR, nullable): e.g. `reconnaissance`, `credential_probing`
   - `next_deception_zone` (VARCHAR, nullable): e.g. `ssh-lure`, `web-lure`, `services-lure`, `quarantine`
   - `created_at` (DATETIME)
   - `started_at` (DATETIME, nullable)
   - `ended_at` (DATETIME, nullable)
   - `metadata_json` (JSON): Configuration, scenario flags, seed parameters.

2. **`agent_actions`**: Records all proposed and brokered AI agent operations.
   - `id` (VARCHAR PK): e.g. `act_xxxx`
   - `run_id` (VARCHAR FK -> runs.id)
   - `timestamp` (DATETIME)
   - `action_type` (VARCHAR): One of 7 allowlisted actions.
   - `target_ip` (VARCHAR)
   - `target_port` (INTEGER)
   - `parameters` (JSON)
   - `status` (VARCHAR): `allowed | denied | timed_out | completed`
   - `latency_ms` (INTEGER, nullable)
   - `output` (JSON, nullable)

3. **`observations`**: Passive protocol analyzer captures and network event records.
   - `id` (VARCHAR PK): e.g. `obs_xxxx`
   - `run_id` (VARCHAR FK -> runs.id)
   - `timestamp` (DATETIME)
   - `source` (VARCHAR): e.g. `protocol-analyzer`
   - `source_ip` (VARCHAR, nullable)
   - `destination_ip` (VARCHAR, nullable)
   - `protocol` (VARCHAR): `TCP | UDP | ICMP | ARP | DNS | HTTP | SSH | SMTP`
   - `behavior_type` (VARCHAR): e.g. `port_discovery`, `incomplete_handshake`, `arp_spoof_candidate`
   - `raw_payload` (JSON)
   - `details` (JSON)

4. **`detections`**: Correlated threat alerts mapped to MITRE ATT&CK techniques.
   - `id` (VARCHAR PK): e.g. `det_xxxx`
   - `run_id` (VARCHAR FK -> runs.id)
   - `timestamp` (DATETIME)
   - `source_ip` (VARCHAR)
   - `technique_id` (VARCHAR): e.g. `T1046`, `T1110`, `T1021.004`, `T1190`, `T1595`, `T1071.004`, `T1557`, `T1095`
   - `technique_name` (VARCHAR)
   - `confidence` (FLOAT): `0.0` to `1.0`
   - `evidence` (JSON)

5. **`honeypot_sessions`**: Honeypot interactions across Cowrie SSH, Web, DNS, and SMTP lures with credentials sanitized.
   - `id` (VARCHAR PK): e.g. `ses_xxxx`
   - `run_id` (VARCHAR FK -> runs.id)
   - `lure_type` (VARCHAR): `cowrie_ssh | web_lure | dns_lure | smtp_lure`
   - `session_id` (VARCHAR)
   - `source_ip` (VARCHAR)
   - `source_port` (INTEGER, nullable)
   - `started_at` (DATETIME)
   - `ended_at` (DATETIME, nullable)
   - `commands_or_requests` (JSON): Sanitized command/request transcript; passwords replaced with `[REDACTED]`.
   - `metadata_json` (JSON)

6. **`policy_decisions`**: Dynamic deception routing decisions triggered by threat scoring and MITRE mapping.
   - `id` (VARCHAR PK): e.g. `pol_xxxx`
   - `run_id` (VARCHAR FK -> runs.id)
   - `timestamp` (DATETIME)
   - `threat_profile` (VARCHAR)
   - `confidence` (FLOAT)
   - `decision` (VARCHAR)
   - `target_zone` (VARCHAR)
   - `evidence` (JSON)
