# Skill 05: Operator Dashboard UI Specifications

## Purpose
Defines the React 18, Vite, TypeScript, and Tailwind CSS operator web console, its component breakdown, state management, and real-time WebSocket event ingestion.

## 1. UI Component Architecture

```
Operator Dashboard
├── Top Control Bar
│   ├── Run Status Badge (IDLE, RUNNING, PAUSED, TERMINATED, COMPLETED)
│   ├── Active run_id indicator
│   ├── Threat Score Meter (0 - 100 with dynamic color gradient)
│   ├── Active Threat Profile Badge
│   ├── Next Deception Zone Pill
│   └── Actions: [Start Run] [Pause] [Resume] [Terminate / Kill Switch]
│
├── Main Grid (2-Column / Split Layout)
│   ├── Left Column: Live Network Topology & Dynamic Attack Path
│   │   ├── 5 VLAN Zones: Edge (10.0.10.0/24), SSH (10.0.20.0/24), Web (10.0.30.0/24), Services (10.0.40.0/24), Monitor (10.0.50.0/24)
│   │   ├── Nodes & Lures Status (Active / Engaged / Quarantined)
│   │   ├── Animated Attack Path Connector
│   │   └── Dynamic Redirection Indicator (when Deception Engine alters path)
│   │
│   ├── Right Column: AI Attacker Loop & Action Broker Transcript
│   │   ├── 3-Layer Loop: Observation Summary -> Planner -> Safe Action Request
│   │   ├── Action Cards: Action Name, Target IP/Port, Status (allowed/denied), Latency
│   │   └── Structured Broker Output Payload viewer
│   │
│   └── Bottom Panels (Tabbed or Split View)
│       ├── Detections & MITRE ATT&CK Matrix & Deception Decisions
│       │   ├── MITRE Technique Badge (T1046, T1110, etc.)
│       │   ├── Confidence Percentage Bar
│       │   └── Deception Routing Decision with linked Evidence
│       │
│       └── Honeypot Sessions Inspector
│           ├── Session Selector (Cowrie SSH, Web Lure, DNS, SMTP)
│           ├── Redacted Credentials Indicator ([REDACTED] tag)
│           └── Detailed Command / Request Log Viewer
```

## 2. Real-Time Streaming & WebSocket Contract
- Dashboard connects to `WS /api/runs/:id/events`.
- Incoming Universal Event Envelopes are appended to an in-memory ring buffer.
- Events update the local state stores:
  - `kind: "action"` -> Updates AI Terminal Transcript and Topology active target.
  - `kind: "observation"` -> Updates Protocol Analyzer feeds and node packet counters.
  - `kind: "detection"` -> Updates MITRE Matrix and bumps Threat Score meter.
  - `kind: "policy"` -> Updates Next Deception Zone and draws dynamic route arrow on Topology.
  - `kind: "honeypot"` -> Updates Honeypot Sessions Inspector with sanitized payloads.
  - `kind: "system"` -> Updates top run status badge.
