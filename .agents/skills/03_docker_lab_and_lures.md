# Skill 03: Docker Lab Topology & Lure Honeypots

## Purpose
Defines the zero-egress Docker Compose lab topology, container security configurations, honeypot adapters, and network isolation policies.

## 1. Zero-Egress Network Architecture
All networks in `docker-compose.lab.yml` are created with `internal: true` to prevent any packet from leaving the host machine:

| VLAN / Network | Subnet CIDR | Gateway / Main Node | Primary Service & Port | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `edge_net` | `10.0.10.0/24` | `edge-gateway` (`10.0.10.42`) | Port 80, 8080 | Ingress point, simulated perimeter |
| `ssh_net` | `10.0.20.0/24` | `cowrie-ssh-lure` (`10.0.20.10`) | Port 22, 2222 | Cowrie SSH medium-interaction lure |
| `web_net` | `10.0.30.0/24` | `web-lure` (`10.0.30.10`) | Port 80, 8080 | Vulnerable web mock / decoy portal |
| `services_net` | `10.0.40.0/24` | `dns-smtp-lure` (`10.0.40.10`/`20`) | Port 53 (DNS), Port 25/587 (SMTP) | Core infrastructure decoys |
| `monitor_net` | `10.0.50.0/24` | `telemetry-collector` (`10.0.50.10`) | Internal packet capture / tap | Passive observer & Zeek/Scapy adapter |

## 2. Hardened Container Specifications
Every container in the lab must satisfy:
1. `privileged: false` (Explicitly never `privileged: true`).
2. `network_mode` NEVER set to `host`.
3. `security_opt: ["no-new-privileges:true"]`.
4. `cap_drop: ["ALL"]`.
5. `read_only: true` wherever feasible, using `tmpfs` for temporary runtime directories.
6. CPU and memory limits (`cpus: "0.5"`, `mem_limit: "256M"`).

## 3. Honeypot Adapters & Credential Sanitization
1. **Cowrie SSH Lure (`10.0.20.10`)**:
   - Emulates SSH banner `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6`.
   - Records all attempted usernames, passwords, executed commands (`uname -a`, `cat /etc/passwd`, `wget`, etc.).
   - Credential Redaction: All plaintext passwords or private keys are converted to `[REDACTED]` prior to persistence and WebSocket streaming.
2. **Web Decoy Lure (`10.0.30.10`)**:
   - Emulates an administrative dashboard or API endpoint.
   - Captures path traversals, SQLi probes, user-agents, HTTP methods.
3. **DNS Decoy Lure (`10.0.40.10`)**:
   - Logs queries for internal hostnames and potential DNS tunneling/exfiltration attempts (e.g. `*.data.corp`).
4. **SMTP Decoy Lure (`10.0.40.20`)**:
   - Responds to `EHLO`, `MAIL FROM`, `RCPT TO`, capturing phishing / spam reconnaissance.
