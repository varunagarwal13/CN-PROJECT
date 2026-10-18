# NetMirage - Implementation Plan & Engineering Blueprint

## Executive Summary
NetMirage is a real-time defensive cyber-range platform engineered with zero-egress sandboxing, passive protocol intelligence, MITRE ATT&CK mapping, and dynamic deception routing.

This document lays out the exact architecture, directory breakdown, file tree, dependencies, and testing gates for full milestone completion.

---

## 1. Directory Structure

```
C:/Users/varun/Projects/cn project/
├── .agents/
│   └── skills/
│       ├── 01_database_and_contracts.md
│       ├── 02_safety_and_broker.md
│       ├── 03_docker_lab_and_lures.md
│       ├── 04_telemetry_mitre_deception.md
│       └── 05_dashboard_ui.md
├── AGENTS.md
├── .env
├── production_artifacts/
│   ├── implementation_plan.md
│   ├── openapi.json
│   ├── lab_schema.json
│   └── verification_report.md
└── app_build/
    ├── backend/
    │   ├── requirements.txt
    │   ├── main.py
    │   ├── config.py
    │   ├── db.py
    │   ├── models.py
    │   ├── schemas.py
    │   ├── event_bus.py
    │   ├── routes.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── planner.py
    │   │   ├── safety_policy.py
    │   │   └── action_broker.py
    │   ├── intel/
    │   │   ├── __init__.py
    │   │   ├── honeypots.py
    │   │   ├── analyzer.py
    │   │   ├── mitre_mapper.py
    │   │   └── deception_policy.py
    │   ├── orchestration/
    │   │   ├── __init__.py
    │   │   └── lab_runner.py
    │   └── tests/
    │       ├── __init__.py
    │       ├── conftest.py
    │       ├── test_api_and_db.py
    │       ├── test_safety_and_broker.py
    │       ├── test_intel_and_deception.py
    │       ├── test_docker_policy.py
    │       └── test_milestone1_e2e.py
    ├── docker/
    │   ├── docker-compose.lab.yml
    │   ├── edge-gateway/
    │   │   └── Dockerfile
    │   ├── cowrie-ssh-lure/
    │   │   └── Dockerfile
    │   ├── web-lure/
    │   │   └── Dockerfile
    │   ├── dns-smtp-lure/
    │   │   └── Dockerfile
    │   └── telemetry-collector/
    │       └── Dockerfile
    └── frontend/
        ├── package.json
        ├── tsconfig.json
        ├── vite.config.ts
        ├── index.html
        ├── tailwind.config.js
        ├── postcss.config.js
        └── src/
            ├── main.tsx
            ├── App.tsx
            ├── types.ts
            ├── components/
            │   ├── TopControlBar.tsx
            │   ├── NetworkTopology.tsx
            │   ├── AttackerTerminal.tsx
            │   ├── DetectionsMatrix.tsx
            │   └── HoneypotInspector.tsx
            └── services/
                ├── api.ts
                └── websocket.ts
```

---

## 2. Dependency Manifest

### Backend (`app_build/backend/requirements.txt`)
- `fastapi>=0.110.0`
- `uvicorn[standard]>=0.28.0`
- `sqlalchemy>=2.0.28`
- `pydantic>=2.6.4`
- `pydantic-settings>=2.2.1`
- `python-dotenv>=1.0.1`
- `httpx>=0.27.0`
- `pytest>=8.1.0`
- `pytest-asyncio>=0.23.5`
- `websockets>=12.0`
- `pyyaml>=6.0.1`
- `scapy>=2.5.0`

### Frontend (`app_build/frontend/package.json`)
- React 18 (`react`, `react-dom`)
- TypeScript
- Vite (`@vitejs/plugin-react`)
- Tailwind CSS (`tailwindcss`, `postcss`, `autoprefixer`)
- Lucide React (`lucide-react` for icons)

---

## 3. Step-by-Step Implementation & Verification Flow

### Phase 1: Workspace Bootstrap & Contracts
- **Artifacts**: Skills 01-05, `implementation_plan.md`.
- **Status**: Complete.

### Phase 2: Backend Persistence & Core API (`app_build/backend/`)
- Implement `config.py`, `db.py`, `models.py`, `schemas.py`.
- Implement `event_bus.py` with in-memory asyncio pub/sub and DB persistence.
- Implement `routes.py` with the 6 required REST endpoints + WebSocket streaming:
  - `GET /api/health`
  - `GET /api/topology`
  - `GET /api/sessions/:id`
  - `POST /api/runs`
  - `POST /api/runs/:id/pause`
  - `POST /api/runs/:id/terminate`
  - `WS /api/runs/:id/events`
- Implement `tests/test_api_and_db.py`.
- **Verification Gate**: Execute `pytest app_build/backend/tests/test_api_and_db.py` -> 100% pass.

### Phase 3: Safety Policy, Action Broker & AI Planner (`app_build/backend/core/`)
- Implement `safety_policy.py`:
  - CIDR validation (`10.0.10.0/24` - `10.0.50.0/24`).
  - Port validation (`22, 2222, 53, 80, 8080, 25, 587`).
  - Allowed actions (`discover_lab_services`, `resolve_dns`, `connect_tcp`, `request_http`, `attempt_ssh_to_lure`, `send_icmp_probe`, `inspect_session_output`).
  - Rate limiting (30/min), concurrency (2), duration cap (600s), kill switch check.
  - Fail-closed semantics.
- Implement `action_broker.py`:
  - Zero arbitrary shell, strictly parameterized actions.
  - Emulation/live mode with structured JSON outputs.
- Implement `planner.py`:
  - 3-layer loop: `observation_summary -> planner -> safe_action_request`.
  - Deterministic state machine progression with fallback/optional LLM integration.
- Implement `tests/test_safety_and_broker.py`.
- **Verification Gate**: Execute `pytest app_build/backend/tests/test_safety_and_broker.py` -> 100% pass.

### Phase 4: Honeypots, Telemetry, MITRE ATT&CK & Deception Policy (`app_build/backend/intel/`)
- Implement `honeypots.py`:
  - Normalizers for Cowrie SSH, Web, DNS, SMTP.
  - Credential redaction (`[REDACTED]`).
- Implement `analyzer.py`:
  - Passive protocol event generator & Scapy adapter.
  - Detects port discovery, TCP incomplete handshakes, ARP anomalies, DHCP bursts, ICMP anomalies.
- Implement `mitre_mapper.py`:
  - Maps to `T1046`, `T1110`, `T1021.004`, `T1190`, `T1595`, `T1071.004`, `T1557`, `T1095`.
  - Calculates confidence scores.
- Implement `deception_policy.py`:
  - Evaluates threat profiles and triggers dynamic route changes.
  - Dynamic route to `ssh-lure`, `web-lure`, `services-lure`, `quarantine`, `dns-lure`.
- Implement `tests/test_intel_and_deception.py`.
- **Verification Gate**: Execute `pytest app_build/backend/tests/test_intel_and_deception.py` -> 100% pass.

### Phase 5: Docker Lab Configuration & Zero-Egress Guard (`app_build/docker/`)
- Create `docker-compose.lab.yml` with the 5 segregated subnets and `internal: true`.
- Create container definitions: `edge-gateway`, `cowrie-ssh-lure`, `web-lure`, `dns-smtp-lure`, `telemetry-collector`.
- Implement `tests/test_docker_policy.py` verifying network isolation and container security restrictions.
- **Verification Gate**: Execute `pytest app_build/backend/tests/test_docker_policy.py` -> 100% pass.

### Phase 6: Autonomous Lab Runner & E2E Integration Test
- Implement `app_build/backend/orchestration/lab_runner.py`:
  - Coordinates the full autonomous cyber-range loop: Planner -> Safety Policy -> Broker -> Analyzer -> MITRE Mapper -> Deception Policy -> Event Bus.
- Implement `tests/test_milestone1_e2e.py`:
  - Runs full lifecycle: start run -> stream events -> AI attacker probing -> MITRE mapping -> deception rerouting -> kill switch termination -> cleanup.
- **Verification Gate**: Execute `pytest app_build/backend/tests/test_milestone1_e2e.py` -> 100% pass.

### Phase 7: Operator Web Dashboard (`app_build/frontend/`)
- Scaffold Vite + React + TypeScript + Tailwind CSS application.
- Build TopControlBar, NetworkTopology, AttackerTerminal, DetectionsMatrix, HoneypotInspector.
- Connect WebSocket client to `/api/runs/:id/events`.
- Verify production build with `npm run build`.

### Phase 8: Final Milestone Verification & Report
- Run all tests and builds.
- Generate `production_artifacts/verification_report.md`.
