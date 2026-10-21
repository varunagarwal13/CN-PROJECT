# NetMirage - Professor & External Examiner Live Demonstration Guide
**Course:** BACSE203 P — Computer Networks Lab, Vellore Institute of Technology (VIT)  
**Evaluator:** Dr. Sudha M / External Examiners  
**Platform:** NetMirage Cyber-Range & Deception Defense System  

---

## Executive Summary for Evaluators

NetMirage is a production-grade, zero-egress web cyber-range and adaptive deception platform. Unlike traditional academic simulators that use hardcoded delays, static responses, or synthetic mock objects, NetMirage operates entirely on **real OS network sockets, dynamic mathematical heuristics, live packet generation, and real SQLite persistence**.

This document contains the exact terminal commands and procedures to verify:
1. **Real OS Network Sockets & Port Bindings** (No mock/synthetic networking).
2. **Wireshark Packet Capture Verification** (Standard libpcap binary files).
3. **The 10-Vector Professor Stress-Test Suite** (100% automated pass verification).
4. **Adversarial Live Attack Walkthrough via cURL** (Real HTTP, TCP, SSH, DNS probes).
5. **Database Audit & Data Integrity** (Real relational schema with sanitized telemetry).

---

## 1. Environment & Architecture Verification

All lab networks and services adhere strictly to zero-egress network policies:

| Subnet / VLAN | Network Name | IP Range | Function / Services |
| :--- | :--- | :--- | :--- |
| **VLAN 10** | `dmz_net` | `10.0.10.0/24` | Public Ingress / Web Decoy Lure (`10.0.10.10:80`) |
| **VLAN 20** | `corp_net` | `10.0.20.0/24` | Workstation & User LAN |
| **VLAN 30** | `prod_net` | `10.0.30.0/24` | Internal Servers & SSH Lure (`10.0.30.22:2222`) |
| **VLAN 40** | `infra_net` | `10.0.40.0/24` | Core Infrastructure & DNS Lure (`10.0.40.10:53`) |
| **VLAN 50** | `deception_net` | `10.0.50.0/24` | High-Interaction Honeygrid & Telemetry Collector |

### Check Live Listening Ports on the Host System

To prove to the examiner that real OS network sockets are bound:

```powershell
# In PowerShell:
Get-NetTCPConnection -LocalPort 8000, 5173, 2222, 80 -ErrorAction SilentlyContinue | Format-Table -Property LocalAddress, LocalPort, State, OwningProcess
```

Or using standard `netstat`:

```cmd
netstat -ano | findstr -i "8000 5173 2222 80"
```

*Expected Result:*
- `127.0.0.1:8000` -> **FastAPI Python Uvicorn Server** (LISTENING)
- `127.0.0.1:5173` -> **Vite / React Dashboard Web Application** (LISTENING)
- `0.0.0.0:2222` or `127.0.0.1:2222` -> **Cowrie SSH Honeypot Socket** (LISTENING)
- `0.0.0.0:80` or `127.0.0.1:80` -> **Apache/2.4 Web Decoy Socket** (LISTENING)

---

## 2. Automated 10-Vector Professor Stress-Test Suite

Run the stress test suite written specifically to demonstrate resilience against academic auditing and boundary testing:

```powershell
& "c:\Users\varun\Projects\cn project\app_build\backend\.venv\Scripts\python.exe" -m pytest "c:\Users\varun\Projects\cn project\app_build\backend\tests\test_professor_stress.py" -v
```

### What Each of the 10 Tests Proves to the Examiner:

| Test Name | Audit Focus | What It Proves |
| :--- | :--- | :--- |
| **`test_01_anti_hardcoding_verification`** | Zero-Hardcoding Audit | Inspects AST/source code to verify `latency_ms` uses `perf_counter()`, `confidence` uses dynamic heuristics, and honeypot sessions use real socket bytes. |
| **`test_02_campus_internet_breakout_attempt`** | Zero-Egress Enforcement | Attempts outbound egress to `8.8.8.8` (Google DNS) and `192.168.1.1`. Verifies Safety Policy Engine returns `status: "denied"` within < 2 ms. |
| **`test_03_unregistered_port_and_command_injection`** | Protocol & Input Sanitization | Sends ports `4444` (Metasploit) and `9999` plus injection strings (`rm -rf /`, `whoami`). Verifies denial and injection blocking. |
| **`test_04_fail_closed_missing_corrupted_config`** | Fail-Closed Architecture | Passes empty string, invalid IP representations, and corrupted payloads to the policy engine. Proves fail-closed behavior. |
| **`test_05_rate_limit_and_dos_burst_stress`** | Concurrency & Anti-DoS | Fires 50 rapid-fire concurrent requests against the engine. Verifies the concurrency cap strictly enforces backpressure without process crash. |
| **`test_06_live_os_socket_and_port_binding_proof`** | Real Network Sockets | Opens real TCP socket connections (`socket.create_connection`) to the backend and lures, asserting real byte handshakes and real OS ping. |
| **`test_07_dynamic_deception_routing_progression`** | Deception Engine State Machine | Steps an adversary through Recon (`10.0.10.10`) to Lateral Movement (`10.0.30.22`), verifying dynamic rerouting from `MONITOR` to `REROUTE_DECEPTION`. |
| **`test_08_credential_redaction_and_privacy_leak`** | Threat Intel Sanitization | Injects plaintext passwords (`password123`, `Admin@2024!`) and AWS access keys. Proves redaction engine transforms them into `[REDACTED_SECRET]`. |
| **`test_09_mid_attack_kill_switch_and_pause_resume`** | Operator Control Plane | Triggers `POST /api/runs/{id}/kill`. Proves immediate transition to `TERMINATED` and rejection of all subsequent actions. |
| **`test_10_wireshark_pcap_file_integrity_verification`** | Wireshark Packet Captures | Inspects the generated `.pcap` binary file. Reads standard libpcap magic header (`0xa1b2c3d4` or `0xd4c3b2a1`) and verifies real Ethernet/IP/TCP packets. |

---

## 3. Wireshark Live Packet Capture Inspection

NetMirage automatically compiles every network event, TCP handshake, DNS query, and honeypot interaction into standard libpcap files.

### Locating the Capture Files
- **Latest Live Run Capture:** `c:\Users\varun\Projects\cn project\production_artifacts\captures\latest_run.pcap`
- **Historical Run Captures:** `c:\Users\varun\Projects\cn project\production_artifacts\captures\{run_id}.pcap`

### Step-by-Step Examiner Wireshark Inspection:

1. **Launch Wireshark directly via CLI or GUI:**
   ```powershell
   # If Wireshark is installed in standard path:
   & "C:\Program Files\Wireshark\Wireshark.exe" "c:\Users\varun\Projects\cn project\production_artifacts\captures\latest_run.pcap"
   ```
   *(Or double-click `production_artifacts\captures\latest_run.pcap` in Windows File Explorer)*

2. **Recommended Wireshark Display Filters to show the Professor:**

   - **Filter 1: Inspect DNS Resolution Queries**
     ```wireshark
     dns
     ```
     *Demonstrates:* Crafted UDP DNS queries targeting `vlan-prod-db.corp.netmirage.lab` over port 53.

   - **Filter 2: Inspect HTTP Web Decoy Traffic**
     ```wireshark
     http
     ```
     *Demonstrates:* Real HTTP GET requests and HTTP 200 responses returning `Server: Apache/2.4.52 (Ubuntu)`.

   - **Filter 3: Inspect SSH Honeypot Lure Sessions**
     ```wireshark
     tcp.port == 2222
     ```
     *Demonstrates:* Full 3-way TCP handshake and Cowrie SSH identification banner (`SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1`).

   - **Filter 4: Inspect SYN Port Probes (MITRE T1046 Network Service Discovery)**
     ```wireshark
     tcp.flags.syn == 1 && tcp.flags.ack == 0
     ```
     *Demonstrates:* Adversary reconnaissance scanning across lab VLAN subnets (`10.0.10.10`, `10.0.30.22`, `10.0.40.10`).

   - **Filter 5: Inspect ICMP Echo Probes (MITRE T1018 Remote System Discovery)**
     ```wireshark
     icmp
     ```
     *Demonstrates:* Echo request (Type 8) and Echo reply (Type 0) packets measuring true network latency.

---

## 4. Live Attack Simulation via cURL

Open a PowerShell terminal to trigger a live run and observe the UI and packet capture update in real time:

### Step 1: Start a New Attack Run
```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/runs" -Method Post -ContentType "application/json" -Body '{"name":"Prof Sudha Viva Evaluation","scenario":"enterprise_recon_lateral_movement"}'
$runId = $response.run_id
Write-Host "Active Run ID: $runId"
```

Or using standard `curl.exe`:
```cmd
curl.exe -X POST "http://127.0.0.1:8000/api/runs" -H "Content-Type: application/json" -d "{\"name\":\"Prof Sudha Evaluation Run\",\"scenario\":\"enterprise_recon_lateral_movement\"}"
```

### Step 2: Query Live Telemetry & Computed Threat Score
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/runs/$runId" | Format-List
```

*Observe:*
- `status`: `"running"` or `"completed"`
- `threat_score`: Dynamically computed value (e.g., `84.6`, NOT hardcoded)
- `deception_status`: `"MONITOR"` -> `"LOW"` -> `"ELEVATED"` -> `"REROUTE_DECEPTION"`

### Step 3: Trigger Mid-Attack Emergency Kill-Switch
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/runs/$runId/kill" -Method Post
```

### Step 4: Download PCAP via API
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/pcap/latest" -OutFile "c:\Users\varun\Projects\cn project\production_artifacts\captures\viva_inspection.pcap"
Write-Host "PCAP downloaded successfully."
```

---

## 5. Persistent SQLite Relational Database Audit

To prove all detections, sessions, and metrics are committed to real relational storage without mocks:

### Inspect Database Schema & Records

```powershell
& "c:\Users\varun\Projects\cn project\app_build\backend\.venv\Scripts\python.exe" -c @'
import sqlite3, json
conn = sqlite3.connect(r"c:\Users\varun\Projects\cn project\netmirage.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== 1. RECENT RUNS (DYNAMIC THREAT SCORING & PROFILES) ===")
for row in cur.execute("SELECT id, status, threat_score, active_profile, next_deception_zone FROM runs ORDER BY created_at DESC LIMIT 3"):
    print(dict(row))

print("\n=== 2. MITRE DETECTIONS (DYNAMIC HEURISTIC CONFIDENCE) ===")
for row in cur.execute("SELECT technique_id, technique_name, confidence, source_ip FROM detections ORDER BY confidence DESC LIMIT 3"):
    print(dict(row))

print("\n=== 3. AGENT ACTIONS (REAL MEASURED SOCKET LATENCY) ===")
for row in cur.execute("SELECT action_type, target_ip, target_port, status, latency_ms FROM agent_actions ORDER BY timestamp DESC LIMIT 3"):
    print(dict(row))

print("\n=== 4. HONEYPOT SESSIONS (REDACTED CREDENTIAL PAYLOADS) ===")
for row in cur.execute("SELECT lure_type, session_id, source_ip, commands_or_requests FROM honeypot_sessions ORDER BY started_at DESC LIMIT 2"):
    print(dict(row))

conn.close()
'@
```

---

## 6. Viva Q&A Cheat Sheet for External Examiners

### Q1: "How do you ensure this cyber-range does not leak packets into VIT campus network?"
> **Answer:** "Every network is governed by a strict zero-egress policy (`internal: true` in Docker networks). Furthermore, our Python `SafetyPolicyEngine` acts as an in-line fail-closed gatekeeper. Any destination IP outside `10.0.10.0/24` through `10.0.50.0/24` or loopback `127.0.0.0/8` is instantly rejected with `status: denied` before any socket is initialized. Test 02 in our test suite verifies this programmatically."

### Q2: "Are your latency metrics and threat scores simulated?"
> **Answer:** "No. All latency is measured using Python's hardware-backed monotonic timer `time.perf_counter()` before and after the actual socket `connect()` or `recv()` call. Threat scores are dynamically computed from active alert severities, MITRE weights, and target asset criticality. Confidence scores use a dynamic heuristic function based on scan velocity, protocol anomaly indicators, and repetition frequency."

### Q3: "How does the Deception Engine work during lateral movement?"
> **Answer:** "When an adversary scans DMZ VLAN 10 and moves laterally toward VLAN 30, the Deception Engine monitors attack velocity. Once the dynamic threat score crosses threshold 70, the engine transitions from `MONITOR` to `REROUTE_DECEPTION`. Connection requests targeting sensitive production servers are transparently diverted to the Cowrie SSH honeypot (`10.0.30.22:2222`) or DNS lure (`10.0.40.10:53`), capturing attacker keystrokes while redacting sensitive tokens."

### Q4: "Can we analyze the network packets captured during the attack?"
> **Answer:** "Yes. NetMirage's `PcapExporter` serializes every packet into standard libpcap binary format using Scapy. You can click `[DOWNLOAD .PCAP]` on the frontend dashboard or open `production_artifacts/captures/latest_run.pcap` directly in Wireshark to inspect Ethernet headers, TCP handshakes, DNS queries, and HTTP headers."

---
*NetMirage Engineering & Security Architecture — Built strictly for academic excellence & industrial network security.*
