# NetMirage: Security Boundaries & Sandbox Isolation Guarantees

## Threat Model & Design Philosophy

NetMirage executes autonomous adversary simulations in conjunction with real-time protocol inspection and deception routing. Because cyber-ranges interact with attack payloads, malicious command simulations, and dynamic network routing, NetMirage enforces a **Zero-Trust, Zero-Breakout** security architecture.

Security invariants are enforced at four independent architectural layers:
1. Docker Virtualization Layer
2. Safety Policy Engine Layer
3. Execution Translation (Action Broker) Layer
4. Global Kill-Switch & Teardown Layer

---

## 1. Zero Host-Network Mode & Zero Privileged Containers

### Container Hardening Invariants
Every service container defined in [app_build/docker/docker-compose.lab.yml](file:///c:/Users/varun/Projects/cn%20project/app_build/docker/docker-compose.lab.yml) must conform to strict isolation rules:

1. **No `network_mode: host`**:
   - Containers are strictly prohibited from sharing the host network namespace.
   - All network access is mediated through isolated Docker bridge networks (`edge_net`, `ssh_net`, `web_net`, `services_net`, `monitor_net`).
2. **No `privileged: true`**:
   - Privileged container execution is explicitly blocked.
   - Containers run without access to `/dev/` host devices, kernel capabilities, or host IPC namespaces.
3. **No Docker Socket Mounting**:
   - Sockets such as `/var/run/docker.sock` are never mounted inside lab containers, preventing container-to-host breakouts and Docker API abuse.
4. **Read-Only Root Filesystems Where Feasible**:
   - Honeypot decoy containers operate with temporary writable scratch layers (`/tmp`), ensuring state resets between runs.

---

## 2. Default `internal: true` Zero-Egress Bridge Isolation

### Layer-3 / Layer-4 Isolation Guarantees
All 5 virtual networks are provisioned with Docker's native `internal: true` flag:

```yaml
networks:
  edge_net:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 10.0.10.0/24
```

### Technical Impact of `internal: true`:
- **No Default Gateway**: Docker creates the virtual bridge without configuring an outbound default gateway (`0.0.0.0/0`) route.
- **Kernel IPTables Filtering**: Linux kernel netfilter/iptables rules actively drop any packets originating from container interfaces destined for external non-bridge IPs.
- **Zero Internet Egress**: Neither the adversary agent nor decoy containers can reach external command-and-control servers, public DNS resolvers (`8.8.8.8`, `1.1.1.1`), or public cloud infrastructure.
- **Host Loopback Protection**: Packets cannot cross into `127.0.0.1` or host physical adapters (`eth0`, `wlan0`).

---

## 3. Prevention of Arbitrary Shell Execution (Fixed 7-Action Catalog)

### The Anti-Shell Guarantee
Many AI-driven security tools rely on passing raw LLM-generated bash strings directly to `subprocess.Popen(cmd, shell=True)`. This represents an existential vulnerability, as prompt injection or model hallucination can cause catastrophic host command execution (`rm -rf /`, reverse shells, or unauthorized network scans).

In NetMirage:
1. **Zero Shell Execution**:
   - The AI Planner and Action Broker never invoke system shells (`bash`, `sh`, `zsh`, `cmd.exe`, `powershell.exe`).
   - `subprocess.Popen(..., shell=True)` is forbidden throughout the backend codebase.
2. **Strict 7-Action Catalog**:
   - The adversary agent can only dispatch actions from a fixed, immutable enum:
     1. `discover_lab_services`
     2. `resolve_dns`
     3. `connect_tcp`
     4. `request_http`
     5. `attempt_ssh_to_lure`
     6. `send_icmp_probe`
     7. `inspect_session_output`
3. **Parametric Execution**:
   - Each action requires structured, strongly-typed parameters (`target_ip: IPv4Address`, `target_port: int`, `parameters: dict`).
   - Handlers use dedicated Python networking libraries (`socket`, `http.client`, `asyncio`, Scapy) that execute only isolated network handshakes without operating system command execution.

---

## 4. Fail-Closed Policy Engine & Immediate Kill Switch

### Fail-Closed Enforcement
The Safety Policy Engine ([app_build/backend/core/safety_policy.py](file:///c:/Users/varun/Projects/cn%20project/app_build/backend/core/safety_policy.py)) intercepts every proposed action prior to broker dispatch:

- **Missing or Malformed Configurations**: Returns `status: "denied"` immediately.
- **Out-of-CIDR Targets**: Any IP address not matching `10.0.10.0/24`, `10.0.20.0/24`, `10.0.30.0/24`, `10.0.40.0/24`, or `10.0.50.0/24` is rejected.
- **Unauthorized Ports**: Any port not in the explicit allowlist (`22`, `2222`, `53`, `80`, `8080`, `25`, `587`) is rejected.
- **Rate Limit Violations**: Executing more than 30 actions/minute triggers policy rate-limiting and logs an alert.

### Global Kill Switch (`POST /api/runs/{id}/terminate`)
Operators retain unilateral, instant control over the range:
- Triggered by clicking the tactile `TERMINATE` button in the UI or issuing a `POST /terminate` REST request.
- Instantly halts the adversary planning thread.
- Revokes active container sessions and resets routing tables.
- Broadcasts a locked `TERMINATED` state to all connected operators and logs the event in the immutable database audit trail.
