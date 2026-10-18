# NetMirage: Core Subsystem Architectural Specifications

## Overview

NetMirage is structured as a decoupled, multi-subsystem defensive cyber-range platform designed for deterministic safety, high-fidelity protocol inspection, and adaptive deception routing. The platform comprises 10 primary subsystems operating in continuous coordination.

---

## 1. Operator Web Console

- **Implementation Path**: [app_build/frontend/src/](file:///c:/Users/varun/Projects/cn%20project/app_build/frontend/src/)
- **Technology Stack**: React 18, Vite, TypeScript, Tailwind CSS, native WebSockets API.
- **Visual Design Paradigm**: Bespoke Swiss-industrial hardware telemetry console inspired by Teenage Engineering, Linear, and Palantir Foundry.
- **Architectural Constraints**:
  - **Color Palette Tokens**:
    - Primary Canvas / Background: Ivory (`#FAF5E9`)
    - Verified / Safe / Start / Active: Green (`#009B4D`)
    - Warning / Deception Divert / Highlight: Tangerine Yellow (`#FFCC00`)
    - Borders, Grid Hairlines & Ink: High-Contrast Charcoal (`#111827`)
  - **Layout & Geometry**: Fixed `100vh` full-viewport split-pane grid with zero body scroll. Panels share exposed `1px solid #111827` structural borders with sharp `0px` or `2px` corners (`rounded-none`).
  - **Typography**: Strict monospace (`JetBrains Mono` / `IBM Plex Mono`) with `tabular-nums` (`font-feature-settings: "tnum" 1`) across all metric readouts, latencies, IPs, and timestamps to eliminate layout jitter during high-throughput live streaming.
  - **Zero-AI-Slop Rule**: Zero gradients, zero drop shadows, zero emojis, zero generic circular spinners, and zero conversational prose or empty-state marketing filler. All states display exact technical status codes (e.g., `STATE: STANDBY // AWAITING_RUN_INIT`, `0 ROWS`).

### Panes & Controls
1. **Tactile Hardware Command Strip ([TopControlBar.tsx](file:///c:/Users/varun/Projects/cn%20project/app_build/frontend/src/components/TopControlBar.tsx))**: Physical industrial switches (`START RUN`, `PAUSE`, `RESUME`, `TERMINATE`) with tactile offset press states (`shadow-[2px_2px_0px_#111827] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none`). Displays live readouts for `NM//SYS.01 [LIVE █]`, `THREAT_INDEX: [00-99]`, `PROFILE`, and `NEXT_LURE`.
2. **Panel `[01]` — Technical Schematic Topology ([NetworkTopology.tsx](file:///c:/Users/varun/Projects/cn%20project/app_build/frontend/src/components/NetworkTopology.tsx))**: Orthogonal 90-degree SVG schematic connecting 5 VLAN segments on a dot-matrix canvas (`radial-gradient(#111827 1px, transparent 1px)`). Subnet clicks trigger cross-console filtering (`[FILTER: 10.0.20.0/24 ✕]`).
3. **Panel `[02]` — AI Planner & Action Broker Tape ([AttackerTerminal.tsx](file:///c:/Users/varun/Projects/cn%20project/app_build/frontend/src/components/AttackerTerminal.tsx))**: Dense, single-line Wireshark/htop-style event tape showing timestamp, stage (`OBS->PLAN->REQ`), action, target, inverted status tags (`ALLOWED`, `COMPLETED`, `DENIED`), and latency.
4. **Panel `[03]` — MITRE ATT&CK & Deception Matrix ([DetectionsMatrix.tsx](file:///c:/Users/varun/Projects/cn%20project/app_build/frontend/src/components/DetectionsMatrix.tsx))**: Tabular grid displaying attack techniques, 10-segment block confidence meters (`████████░░ 0.86`), and route vectors (`➔ SSH-LURE`, `➔ DNS-LURE`).
5. **Panel `[04]` — Honeypot Session Inspector ([HoneypotInspector.tsx](file:///c:/Users/varun/Projects/cn%20project/app_build/frontend/src/components/HoneypotInspector.tsx))**: Hard-bordered tab strip (`[ALL]`, `[SSH:COWRIE]`, `[HTTP:WEB]`, `[DNS]`, `[SMTP]`) with an inline split-view payload inspector showing captured commands and sanitized `[REDACTED]` credentials.

---

## 2. Control API & Orchestration Engine

- **Implementation Path**: [app_build/backend/main.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/main.py), [app_build/backend/routes.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/routes.py), [app_build/backend/event_bus.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/event_bus.py)
- **Technology Stack**: FastAPI, Starlette WebSockets, asyncio, Pydantic v2.
- **Core Responsibilities**:
  - Exposes RESTful endpoints for environment health, topology discovery, run lifecycle management, and session retrieval.
  - Manages active run state machine transitions: `pending` -> `running` <-> `paused` -> `terminated` / `completed`.
  - Maintains the Universal Event Bus, multiplexing real-time telemetry from the adversary loop, passive analyzers, and deception policies to subscribed browser WebSocket clients.
  - Generates the Universal Event Envelope for every atomic state change:
    ```json
    {
      "run_id": "run_20261018_070428_0789",
      "event_id": "evt_a378a083",
      "timestamp": "2026-10-18T07:04:28.123456Z",
      "kind": "action",
      "source": "action-broker",
      "payload": { ... }
    }
    ```

---

## 3. AI Attacker Agent & Autonomous Planner

- **Implementation Path**: [app_build/backend/orchestration/planner.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/orchestration/planner.py)
- **Execution Pipeline**: Strict 3-stage loop:
  $$\text{Observation Summary} \longrightarrow \text{Planner Model / FSM} \longrightarrow \text{Safe Action Request}$$
- **Operational Modes**:
  - **Deterministic State-Machine**: Automatically engaged when no external LLM API key is configured. Executes multi-stage adversarial attack profiles (`reconnaissance`, `credential_probing`, `network_manipulation`, `covert_channel`).
  - **LLM-Augmented Mode**: Employs Google Gemini or OpenAI structured function-calling to analyze real-time observation summaries and select next-hop actions.
- **Fixed 7-Action Allowlist Catalog**:
  1. `discover_lab_services`: Port scanning within designated lab subnets.
  2. `resolve_dns`: Querying the lab internal DNS decoy.
  3. `connect_tcp`: Establishing low-level TCP handshakes to test service availability.
  4. `request_http`: Executing HTTP requests to decoy web endpoints.
  5. `attempt_ssh_to_lure`: Automated authentication attempts against the Cowrie SSH honeypot.
  6. `send_icmp_probe`: Echo request probes to map responsive hosts.
  7. `inspect_session_output`: Polling captured honeypot interaction feeds.

---

## 4. Safety Policy Engine

- **Implementation Path**: [app_build/backend/core/safety_policy.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/core/safety_policy.py)
- **Design Philosophy**: Strict Fail-Closed Zero-Trust Enforcement.
- **Verification Invariants**:
  - **CIDR Boundary Verification**: All target IP addresses must strictly reside within the 5 configured lab subnets (`10.0.10.0/24` to `10.0.50.0/24`). Out-of-bounds IPs (e.g., `192.168.1.1`, `8.8.8.8`, `127.0.0.1`) are immediately denied.
  - **Port Allowlist**: Target ports must strictly match the authorized lab port list (`22`, `2222`, `53`, `80`, `8080`, `25`, `587`). All other ports return an immediate denial.
  - **Rate Limiting & Concurrency Guardrails**: Limits execution to a maximum of 30 actions per minute and 2 concurrent in-flight actions.
  - **Container Isolation Inspection**: Verifies that lab containers never mount host sockets (`/var/run/docker.sock`), run in `privileged` mode, or utilize `network_mode: host`.
  - **Global Kill Switch**: Intercepts active runs upon operator termination, immediately rejecting subsequent actions and initiating lab containment.

---

## 5. Action Broker

- **Implementation Path**: [app_build/backend/core/action_broker.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/core/action_broker.py)
- **Role**: Narrow parametric execution engine.
- **Key Safety Guarantee**: **No Arbitrary Shell Invocations**.
  - The Action Broker never calls `subprocess.Popen(..., shell=True)` with model-provided strings.
  - Each allowlisted action maps to an isolated Python network client (e.g., `socket.create_connection`, `http.client.HTTPConnection`, `asyncio.open_connection`, or Scapy packet builders).
  - All outputs are sanitized, structured into standardized JSON schemas, and annotated with exact execution latencies in milliseconds.

---

## 6. Disposable Docker Compose Lab

- **Implementation Path**: [app_build/docker/docker-compose.lab.yml](file:///c:/Users/varun/Projects/cn%20project/app_build/docker/docker-compose.lab.yml)
- **Virtual Network Architecture**: Five custom bridge networks created with Docker Compose v2:
  ```yaml
  networks:
    edge_net:
      driver: bridge
      internal: true
      ipam:
        config:
          - subnet: 10.0.10.0/24
    ssh_net:
      driver: bridge
      internal: true
      ipam:
        config:
          - subnet: 10.0.20.0/24
    web_net:
      driver: bridge
      internal: true
      ipam:
        config:
          - subnet: 10.0.30.0/24
    services_net:
      driver: bridge
      internal: true
      ipam:
        config:
          - subnet: 10.0.40.0/24
    monitor_net:
      driver: bridge
      internal: true
      ipam:
        config:
          - subnet: 10.0.50.0/24
  ```
- **Zero-Egress Invariant**: Setting `internal: true` removes default gateway routing from the bridges. Containers cannot communicate with the host network or external internet, creating a zero-egress sandbox.

---

## 7. Honeypot Adapters & Credential Redaction Engine

- **Implementation Path**: [app_build/backend/intel/honeypot_adapters.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/intel/honeypot_adapters.py), [app_build/backend/intel/credential_redactor.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/intel/credential_redactor.py)
- **Lure Implementations**:
  - **Cowrie SSH Honeypot (`10.0.20.10:2222`)**: Emulates OpenSSH server banner, captures client authentication handshakes, user input keystrokes, and download attempts.
  - **Decoy Web Portal (`10.0.30.10:80`)**: Emulates legacy administrative interface with simulated directory traversal and login forms.
  - **DNS Sinkhole (`10.0.40.10:53`)**: Intercepts domain resolution attempts and logs queried TXT/A records for DNS tunneling analysis.
  - **SMTP Sink (`10.0.40.20:25`)**: Captures outbound exfiltration emails and logs source headers.
- **Automated Credential Redaction**:
  - Traverses incoming payloads and normalizes session data into canonical `HoneypotSession` objects.
  - Automatically replaces passwords, tokens, API keys, and sensitive environment variables with `[REDACTED]` prior to database insertion and WebSocket broadcasting, preventing credential leakage in telemetry feeds.

---

## 8. Passive Telemetry & Protocol Intelligence

- **Implementation Path**: [app_build/backend/intel/protocol_analyzer.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/intel/protocol_analyzer.py)
- **Analysis Capabilities**:
  - **Layer-2 ARP Analysis**: Flags sudden MAC-to-IP binding changes and unsolicited ARP replies indicative of ARP spoofing or poisoned routing.
  - **Layer-3 ICMP Anomaly Detection**: Monitors probe frequencies, echo request packet sizes, and sweeps across internal VLAN boundaries.
  - **Layer-4 TCP Port Sweeps & Half-Open Scans**: Identifies rapid SYN packets without ACK completions, measuring connection rates per source IP.
  - **Layer-7 Protocol Inspection**: Parses HTTP headers for path traversal (`../etc/passwd`), checks SSH key exchange anomalies, and evaluates DNS query lengths for exfiltration signals.

---

## 9. MITRE ATT&CK Mapper & Dynamic Deception Policy

- **Implementation Path**: [app_build/backend/intel/deception_policy.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/intel/deception_policy.py)
- **Behavioral Classification Matrix**:
  | Detected Protocol Behavior | MITRE ATT&CK Technique | Confidence Formula | Deception Target |
  | :--- | :--- | :--- | :--- |
  | Multi-port TCP SYN sweep | **T1046**: Network Service Discovery | $\min(1.0, 0.6 + 0.05 \times \text{ports})$ | `SSH-LURE` (`10.0.20.10`) |
  | HTTP path traversal / SQLi | **T1190**: Exploit Public-Facing Application | $\min(1.0, 0.7 + 0.1 \times \text{payloads})$ | `WEB-LURE` (`10.0.30.10`) |
  | High-frequency SSH authentication | **T1110**: Brute Force | $\min(1.0, 0.75 + 0.05 \times \text{attempts})$ | `SERVICES-LURE` (`10.0.40.20`) |
  | DNS tunneling / abnormal TXT queries | **T1095**: Non-Application Layer Protocol | $\min(1.0, 0.65 + 0.08 \times \text{queries})$ | `DNS-LURE` (`10.0.40.10`) |
- **Threat Scoring & Deception Transitions**:
  - Calculates cumulative run threat score ($00 \le S \le 99$) based on technique severity and frequency.
  - Evaluates active threat profile: `RECONNAISSANCE` $\to$ `CREDENTIAL_PROBING` $\to$ `NETWORK_MANIPULATION` $\to$ `COVERT_CHANNEL`.
  - Re-routes adversary traffic away from critical services into quarantine decoys or isolated honeypots based on policy confidence.

---

## 10. Immutable Event Store

- **Implementation Path**: [app_build/backend/models.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/models.py), [app_build/backend/db.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/db.py)
- **Database Engine**: SQLAlchemy 2.0 with asynchronous and synchronous execution support (SQLite default for zero-dependency standalone operation; PostgreSQL ready for enterprise deployments).
- **Core Entities (6 Immutable Tables)**:
  1. `runs`: Run metadata, operational status, cumulative threat score, active profile, next lure.
  2. `agent_actions`: Audit trail of proposed and executed actions, parameters, statuses (`allowed`, `denied`, `completed`), and execution latencies.
  3. `observations`: Protocol analyzer telemetry records, packet counts, and payload hashes.
  4. `detections`: MITRE ATT&CK mappings, confidence ratings, and behavioral evidence.
  5. `honeypot_sessions`: Captured interaction sessions, sanitized commands, credential redaction logs, and handshake metadata.
  6. `policy_decisions`: Safety policy decisions, allow/deny audit logs, and deception route transitions.
