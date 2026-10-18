# Skill 04: Frontend Precision Design System & 100% Wiring Standard

## Purpose
Enforces the strict color palette, zero-wordy text rule, and 100% button-to-API wiring requirements for the NetMirage web console.

## 1. Locked Color Palette
- **Canvas / Surfaces**: Ivory (`#FAF5E9`). Used across the root viewport, cards, headers, table backgrounds, and panels.
- **Primary Brand / Safe / Active**: Green (`#009B4D`). Used for active action badges (`allowed`, `completed`), `Start Run` and `Resume` buttons, verified nodes, and active WebSocket indicators.
- **Accent / Warning / Deception / Lure**: Tangerine Yellow (`#FFCC00`). Used for active attack vectors, `Pause` button, MITRE technique confidence bars, Deception Policy highlights, and target lure indicators.
- **Typography & Structural Borders**: High-contrast Charcoal (`#111827`). High-contrast borders, dividers, dark monospaced technical text, and badges.

## 2. Zero Wordy Lines Rule
- **Prohibited**:
  - No welcome paragraphs, intro summaries, or marketing copy.
  - No filler text ("This panel lets you view...", "Click here to...").
  - No decorative placeholder text.
- **Required**:
  - Every element is an actionable control, CIDR badge, IP:Port readout, MITRE code, latency meter, or sanitized session string.
  - Format: `[10.0.10.42:80] | T1046 (0.90) | ROUTE -> SSH-LURE | 8ms`

## 3. 100% Button Wiring Standards
Every interactive element must execute a real API call or change live filtered state:
- `Start Run`: Invokes `POST /api/runs`, opens WebSocket, and streams events.
- `Pause`: Invokes `POST /api/runs/:id/pause` and updates status to `PAUSED`.
- `Resume`: Invokes `POST /api/runs/:id/resume` and updates status to `RUNNING`.
- `Terminate (Kill Switch)`: Invokes `POST /api/runs/:id/terminate` and immediately kills run loop.
- `VLAN Node Filter`: Clicking any node in the Topology map filters the Action and Session feed to that specific node/CIDR; includes a `Clear Filter` chip.
- `Action Feed Tabs` (`ALL` | `ALLOWED` | `DENIED`): Filter actions based on policy status.
- `Honeypot Lure Tabs` (`ALL` | `SSH` | `WEB` | `DNS` | `SMTP`): Filter lure sessions.
