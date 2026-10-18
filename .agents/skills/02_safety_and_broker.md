# Skill 02: Safety Policy Engine & Action Broker

## Purpose
Defines the zero-trust, fail-closed policy engine that intercepts all AI actions and deception routing decisions, and the Action Broker that translates allowed operations into constrained sandbox operations without shell exposure.

## 1. Safety Policy Rules
Every action proposed by the AI Planner and every routing transition proposed by the Deception Router MUST be evaluated against:

1. **Destination IP CIDR Enforcement**:
   - Destination IP must be contained within configured lab CIDRs:
     - `edge`: `10.0.10.0/24`
     - `ssh`: `10.0.20.0/24`
     - `web`: `10.0.30.0/24`
     - `services`: `10.0.40.0/24`
     - `monitor`: `10.0.50.0/24`
   - Any external IP (e.g. `8.8.8.8`, `192.168.1.1`, `127.0.0.1`, `0.0.0.0`) is immediately denied.

2. **Registered Lab Port Enforcement**:
   - Destination port must belong to the registered lab service whitelist:
     `[22, 2222, 53, 80, 8080, 25, 587]`.
   - Any unregistered port is immediately denied.

3. **Allowlisted Action Types (Strictly 7)**:
   - `discover_lab_services`: Scan ports within lab CIDRs.
   - `resolve_dns`: Query lab DNS lure (`10.0.40.10`).
   - `connect_tcp`: Establish TCP handshake to verify open service.
   - `request_http`: Issue HTTP GET/POST to lab web lure (`10.0.30.10`).
   - `attempt_ssh_to_lure`: Simulate SSH auth against Cowrie lure (`10.0.20.10`).
   - `send_icmp_probe`: Send echo request within lab segments.
   - `inspect_session_output`: Retrieve sanitized outputs from prior active sessions.
   - Any other action name is rejected.

4. **Rate Limiting & Concurrency**:
   - Max 30 actions per minute per run.
   - Max 2 concurrent actions per run.
   - Sliding window timestamp tracker.

5. **Run Duration & Lifecycle Guard**:
   - Max run duration: 600 seconds. Runs exceeding this are automatically terminated.
   - Global Kill Switch: If run status is `paused` or `terminated`, all actions are denied immediately.

6. **Container Security Assertions**:
   - Rejects any configuration with `privileged: true` or `network_mode: host`.
   - Rejects missing network configs or missing `internal: true`.

7. **Fail-Closed Principle**:
   - Any missing, malformed, or ambiguous field defaults to `status: "denied"`.
   - Actions are written to `agent_actions` before and after policy evaluation.

## 2. Action Broker Architecture
The Action Broker takes an action that received `allowed` and executes it safely:
- **No Arbitrary Shell**: Under NO circumstances does the broker invoke `shell=True` or execute unparsed strings in a terminal.
- **Parametric Lab Operations**:
  - `discover_lab_services`: Socket or Docker socket connect probes with short timeouts.
  - `resolve_dns`: DNS UDP query to `10.0.40.10`.
  - `connect_tcp`: Raw TCP connect with latency calculation.
  - `request_http`: HTTP client request with structured header/body response capture.
  - `attempt_ssh_to_lure`: SSH banner / auth exchange with Cowrie lure.
  - `send_icmp_probe`: Synthetic ICMP echo or socket probe.
  - `inspect_session_output`: In-memory query to honeypot session store.
- **Dual Mode (Live Docker or High-Fidelity Emulator)**:
  - If Docker daemon / lab containers are reachable on the configured IPs, commands target those services directly.
  - If running in headless CI or when Docker is inactive, high-fidelity mock responder responds according to realistic protocol semantics so all tests and verification pipelines pass deterministically.
- **Output Contract**:
  ```json
  {
    "action": "connect_tcp",
    "target": "10.0.30.10",
    "port": 80,
    "status": "completed",
    "latency_ms": 8,
    "output": "HTTP service responded"
  }
  ```
