# Skill 03: Zero-Egress Docker Lab Topology & Protocol Intelligence

## Purpose
Specifies the 5 zero-egress Docker bridge networks, container hardening parameters, passive packet telemetry adapters, MITRE ATT&CK mapping, and dynamic deception routing.

## 1. Zero-Egress Network Topology
All networks must strictly declare `internal: true` to prevent any packet egress to external networks or the host interface.

| VLAN Name | CIDR Subnet | Gateway IP | Key Lure / Node | Port(s) | Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `edge_net` | `10.0.10.0/24` | `10.0.10.1` | `edge-gateway` (`10.0.10.42`) | 80, 8080 | Perimeter ingress proxy |
| `ssh_net` | `10.0.20.0/24` | `10.0.20.1` | `cowrie-ssh-lure` (`10.0.20.10`) | 22, 2222 | Cowrie SSH decoy |
| `web_net` | `10.0.30.0/24` | `10.0.30.1` | `web-lure` (`10.0.30.10`) | 80, 8080 | Administrative portal lure |
| `services_net` | `10.0.40.0/24` | `10.0.40.1` | `dns-lure` (`10.0.40.10`), `smtp-lure` (`10.0.40.20`) | 53, 25, 587 | Core services decoys |
| `monitor_net` | `10.0.50.0/24` | `10.0.50.1` | `telemetry-collector` (`10.0.50.10`) | 8080 | Passive tap & quarantine sinkhole |

## 2. Container Hardening Constraints
- `network_mode: host` is strictly forbidden.
- `privileged: true` is strictly forbidden.
- `security_opt: ["no-new-privileges:true"]` is required on all services.
- `cap_drop: ["ALL"]` is required on all services.
- `read_only: true` with `/tmp` mounted via `tmpfs: ["/tmp:rw,noexec,nosuid"]`.

## 3. Passive Telemetry & MITRE ATT&CK Mapping
Observations captured passively are mapped to techniques with confidence metrics:
- Port/Service Sweep -> `T1046` (Network Service Discovery, 0.90)
- HTTP Path Traversal / Admin Probe -> `T1190` (Exploit Public-Facing App, 0.85) / `T1595`
- SSH Credential Brute-force -> `T1110` (Brute Force, 0.95) / `T1021.004`
- DNS Covert Tunnel Query -> `T1071.004` (Application Layer Protocol: DNS, 0.88)
- ICMP Payload Anomaly -> `T1095` (Non-Application Layer Protocol, 0.80)
- ARP Spoof Candidate -> `T1557` (Adversary-in-the-Middle, 0.92)

## 4. Dynamic Deception Policy Routing
- `reconnaissance` -> Divert attacker to `ssh-lure` (`10.0.20.10`) or `web-lure` (`10.0.30.10`).
- `credential_probing` -> Divert attacker deeper into `services-lure` (`10.0.40.0/24`).
- `network_manipulation` -> Sever lateral paths and route to `quarantine` (`10.0.50.99`).
- `covert_channel` -> Mirror to `dns-lure` (`10.0.40.10`) with elevated logging.
