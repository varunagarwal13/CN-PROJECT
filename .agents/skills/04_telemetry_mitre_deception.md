# Skill 04: Passive Telemetry, MITRE ATT&CK Mapping & Deception Policy

## Purpose
Defines the passive packet/event telemetry collector, MITRE ATT&CK technique classification engine, and dynamic deception routing policy.

## 1. Passive Protocol Analyzer
The telemetry collector observes lab traffic without modifying host networking interfaces. It supports Scapy packet decoders and event log taps.
Behaviors detected:
1. **Port Discovery**: Multiple rapid TCP SYN or connect attempts across distinct ports -> indicates scanning.
2. **TCP Incomplete Handshake**: SYN sent without completing 3-way handshake or RST packets -> stealth scan.
3. **ARP Identity Changes**: Multiple MAC-IP associations or unexpected gratuitous ARPs -> potential MitM / ARP poisoning.
4. **DHCP Request Bursts**: Rapid DHCP discover/request packets -> network exhaustion / rogue DHCP attempt.
5. **ICMP Anomalies**: Unusually large payload or invalid types -> tunneling or fingerprinting.
6. **Retransmission / Timing**: Abnormal delays or retransmission floods.

## 2. MITRE ATT&CK Mapping Matrix
Observations are correlated into detections with technique IDs and confidence scores:

| Observed Activity | MITRE Technique ID | Technique Name | Confidence | Threat Profile |
| :--- | :--- | :--- | :--- | :--- |
| Port/Service Discovery | `T1046` | Network Service Discovery | 0.90 | `reconnaissance` |
| Web path/banner scan | `T1595` / `T1190` | Active Scanning / Exploit Public-Facing App | 0.85 | `reconnaissance` |
| SSH credential probing | `T1110` / `T1021.004` | Brute Force / Remote Services: SSH | 0.95 | `credential_probing` |
| DNS covert-channel / anomaly | `T1071.004` | Application Layer Protocol: DNS | 0.88 | `covert_channel` |
| ARP spoofing / MitM probe | `T1557` | Adversary-in-the-Middle | 0.92 | `network_manipulation` |
| ICMP payload tunneling | `T1095` | Non-Application Layer Protocol | 0.80 | `covert_channel` |

## 3. Dynamic Deception Policy Engine
Calculates cumulative threat score (0-100) and triggers dynamic deceptive routing:
- **Rule 1: `reconnaissance` (Confidence >= 0.7)**:
  - Route attacker traffic toward `ssh-lure` (`10.0.20.0/24`) or `web-lure` (`10.0.30.0/24`) to prolong engagement and capture TTPs.
- **Rule 2: `credential_probing` (Confidence >= 0.8)**:
  - Route attacker deeper into `services-lure` (`10.0.40.0/24`) with synthetic credential responses to capture downstream exploitation attempts.
- **Rule 3: `network_manipulation` (Confidence >= 0.85)**:
  - Isolate attacker immediately into the `quarantine` zone (`10.0.50.0/24`), severing simulated lateral paths.
- **Rule 4: `covert_channel` (Confidence >= 0.75)**:
  - Redirect DNS traffic to honeynet DNS logger (`10.0.40.10`) and elevate telemetry observation sampling.

Each decision writes a record to `policy_decisions` and broadcasts an event on the event bus with the evidence trail.
