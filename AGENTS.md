# AGENTS.md - NetMirage Project Blueprint & Engineering Standards

## 1. Directory & Isolation Standards
- **Application Target Directory**: ALL application source code, Dockerfiles, frontend assets, and test suites MUST be written inside `<WORKSPACE_ROOT>/app_build/`. Never write application code in the workspace root.
- **Inter-Agent Handoffs**: All multi-agent state, OpenAPI specs, DB schemas, and execution logs MUST be written to `<WORKSPACE_ROOT>/production_artifacts/`.
- **Modular Skills**: Reference `<WORKSPACE_ROOT>/.agents/skills/*.md` before implementing specific subsystems.
- **Pathing**: Use **ABSOLUTE PATHS ONLY** in all terminal commands, file reads/writes, and script invocations.

## 2. Locked Tech Stack
- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2.0 (async/sync SQLite default, PostgreSQL ready), Pydantic v2, WebSockets, Scapy.
- **Frontend**: React 18 (Vite + TypeScript), Tailwind CSS, native WebSocket API.
- **Lab Infrastructure**: Docker Compose v2 with `internal: true` zero-egress bridge networks (`10.0.10.0/24` to `10.0.50.0/24`).
- **Testing**: `pytest`, `pytest-asyncio`, `httpx` (Backend), Vitest (Frontend).
- **Platform Type**: Strictly a Web-based Cyber-Range Platform (Browser UI + Python Server + Docker Engine). DO NOT generate any mobile application code (no Android, iOS, React Native, Flutter, or Expo).
## 3. Non-Negotiable Security & Architectural Boundaries
1. **Zero Host/Network Breakout**: Never configure Docker containers with `network_mode: host` or `privileged: true`. All lab networks MUST set `internal: true` (zero internet egress).
2. **No Arbitrary Shell**: The AI Planner and Action Broker must NEVER use `subprocess.Popen(..., shell=True)` with raw model strings. Only the 7 allowlisted actions (`discover_lab_services`, `resolve_dns`, `connect_tcp`, `request_http`, `attempt_ssh_to_lure`, `send_icmp_probe`, `inspect_session_output`) are permitted.
3. **Fail-Closed Policy Engine**: Any missing config, out-of-CIDR IP, unregistered port, or rate-limit violation MUST immediately return `status: "denied"`.
4. **Universal Event Envelope**: Every WebSocket message and event store entry must conform strictly to:
   `{"run_id": str, "event_id": str, "timestamp": ISO8601_str, "kind": str, "source": str, "payload": dict}`

   # AGENTS.md - NetMirage Project Blueprint & Engineering Standards

## 4. Directory & Multi-Agent Swarm Standards
- **Platform Type**: Strictly a Web-based Cyber-Range Platform (Browser UI + Python FastAPI Server + Docker Engine)[cite: 1, 5, 10]. DO NOT generate any mobile application code (no Android, iOS, React Native, Flutter, or Expo).
- **Application Target Directory**: ALL source code, Dockerfiles, frontend assets, and test suites MUST be written inside `<WORKSPACE_ROOT>/app_build/`.
- **Multi-Agent Swarm Coordination**: Spawn parallel subagents (Backend Agent, Cyber-Intel/Docker Agent, Frontend UI Agent, QA Verification Agent). Subagents MUST use `<WORKSPACE_ROOT>/production_artifacts/` to drop API contracts, schemas, and status locks to prevent cross-agent file overwrite errors.
- **Modular Skills**: Reference `<WORKSPACE_ROOT>/.agents/skills/*.md` before implementing specific subsystems.
- **Pathing**: Use **ABSOLUTE PATHS ONLY** in all terminal commands, file reads/writes, and script invocations.

## 5. Strict UI/UX & Color Palette Rules (Frontend)
- **Locked Color Palette**:
  - **Primary Background / Canvas**: Ivory (`#FAF5E9`)
  - **Primary Brand / Active / Safe / Verified**: Green (`#009B4D`)
  - **Accent / Warning / Deception Reroute / Highlight**: Tangerine Yellow (`#FFCC00`)
  - **Typography / Structural Borders**: High-contrast Charcoal (`#111827`) for readability against Ivory.
- **Zero Wordy Lines**: No paragraphs, no marketing copy, no explanatory tooltips, and no filler text anywhere in the UI. Every element on screen must be a live data readout, metric badge, CIDR tag, MITRE ID, or functional control.
- **100% Functional Wiring**: No dummy buttons, dead links, or static mock states. Every button (`Start Run`, `Pause`, `Resume`, `Terminate`, VLAN node filters, Session inspectors) must trigger a real API call or live state update[cite: 1, 10].

