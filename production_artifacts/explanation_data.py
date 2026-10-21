"""
Structured technical content and data for NetMirage Project Explanation & Code Walkthrough.
Course: BACSE203 P - Computer Networks Lab (Innovative Lab Assessment ELA 1.0)
Institution: Vellore Institute of Technology (VIT), Vellore
Faculty Guide: Dr. Sudha M, Professor, School of Computer Science and Engineering
Candidates:
  - Abhisumat Panda (25BYB0202)
  - Atharva Parmar (25BYB0180)
  - Manas Patel (25BYB0190)
  - Varun Agarwal (25BYB0186)
"""

METADATA = {
    "project_title": "NetMirage: Autonomous Cyber-Range with Adaptive Deception Routing",
    "document_title": "NetMirage — Defensive Cyber-Range Architecture & Codebase Guide",
    "course_code": "BACSE203 P",
    "course_title": "Computer Networks Lab",
    "assessment_type": "Innovative Lab Assessment (ELA 1.0)",
    "institution": "Vellore Institute of Technology (VIT), Vellore",
    "department": "School of Computer Science and Engineering (SCOPE)",
    "faculty_guide": "Dr. Sudha M, Professor, School of Computer Science and Engineering",
    "team": [
        {"name": "Abhisumat Panda", "reg_no": "25BYB0202", "role": "Network Virtualization & Docker Infrastructure"},
        {"name": "Atharva Parmar", "reg_no": "25BYB0180", "role": "Adversary AI Planning & Safety Policy Engine"},
        {"name": "Manas Patel", "reg_no": "25BYB0190", "role": "Protocol Analysis & MITRE ATT&CK Classification"},
        {"name": "Varun Agarwal", "reg_no": "25BYB0186", "role": "Full-Stack Integration, WebSocket Bus & Operator Console"}
    ]
}

# -------------------------------------------------------------------------------------------------
# CHAPTER 1: THE BIG PICTURE — WHAT IS NETMIRAGE & WHY DOES IT EXIST?
# -------------------------------------------------------------------------------------------------
CHAPTER_1 = {
    "title": "CHAPTER 1: THE BIG PICTURE — WHAT IS NETMIRAGE & WHY DOES IT EXIST?",
    "intro": (
        "Modern cybersecurity education faces an unprecedented dilemma: generative AI models and autonomous "
        "agents can synthesize sophisticated offensive reconnaissance and lateral movement scripts in seconds. "
        "However, unleashing an autonomous AI agent onto physical lab networks or open cloud environments creates "
        "catastrophic risks of accidental denial-of-service, unintended IP leakage, self-propagating worms, and "
        "host system breakout. NetMirage was conceived, architected, and built as an academic defensive cyber-range "
        "that solves this crisis completely. It allows security researchers and students to observe, analyze, "
        "and manipulate autonomous AI attack behavior safely in real time without any possibility of host or internet harm."
    ),
    "sections": [
        {
            "id": "1.1",
            "title": "The Core Problem: Why Studying Autonomous AI Attackers is Dangerous",
            "simple": (
                "Imagine giving an eager learner a real flamethrower inside a crowded wooden house to study how fire spreads. "
                "That is exactly what happens when you give an AI attacker raw terminal access on a real network: a single "
                "hallucination, infinite retry loop, or unexpected subnet scan can crash hospital servers, corrupt databases, "
                "or leak private credentials to the public internet."
            ),
            "technical": (
                "Large Language Models (LLMs) and autonomous reinforcement-learning planners exhibit non-deterministic "
                "decision pathways. When provided with an unrestricted command-line interface (e.g., bash/sh) or raw network "
                "sockets, AI agents suffer from three fundamental architectural hazards:\n"
                "1. Hallucinatory Amplification: The model may generate invalid CIDR ranges or broadcast floods (e.g., ping sweeps "
                "against 255.255.255.255 or public subnets like 8.8.8.8) that trigger upstream ISP abuse flags.\n"
                "2. Arbitrary Code Execution & Host Escape: Allowing an agent to execute arbitrary shell scripts permits model prompt "
                "injections where an adversarial decoy payload instructs the AI to execute 'rm -rf /' or spawn reverse shells back "
                "to the developer's host OS.\n"
                "3. Cascading Resource Exhaustion: Without hardware and concurrency boundaries, an autonomous agent can spawn "
                "thousands of parallel socket connections, causing TCP SYN floods that exhaust ephemeral ports and crash the testing host."
            ),
            "where": "app_build/backend/core/safety_policy.py (SafetyPolicyEngine.evaluate_action) & app_build/docker/docker-compose.lab.yml"
        },
        {
            "id": "1.2",
            "title": "The NetMirage Solution: Disposable Lab, Action Broker, & Dynamic Deception",
            "simple": (
                "NetMirage acts like a high-tech stunt arena surrounded by blast-proof glass. The AI attacker thinks it is breaking "
                "into a real corporate enterprise, but every computer it touches is a harmless toy decoy (honeypot). As soon as the AI "
                "tries to steal passwords or scan for secrets, our system automatically shifts the fake maze to steer the attacker deeper "
                "into containment while we watch every move on a live radar screen."
            ),
            "technical": (
                "NetMirage implements a multi-tier cyber-range architecture governed by five synchronized defense layers:\n"
                "1. Disposable Zero-Egress Lab: Five isolated Docker bridge networks (10.0.10.0/24 to 10.0.50.0/24) with 'internal: true' "
                "ensuring mathematical impossibility of internet routing.\n"
                "2. Allowlisted Action Broker: A mediating proxy between the AI Planner and the network. The AI cannot run shell commands; "
                "it can only submit structured JSON parameter requests for one of 7 allowlisted actions.\n"
                "3. Passive Protocol Analyzers: Telemetry taps that inspect Layer 2 ARP frames, Layer 3 IP headers, Layer 4 TCP states, "
                "and Layer 7 application transactions without altering host configurations.\n"
                "4. MITRE ATT&CK Classification Engine: Real-time mapping of observed wire behavior to industry-standard adversary "
                "techniques (e.g., T1046 Network Service Discovery, T1110 Brute Force, T1071.004 DNS Exfiltration) with confidence scoring.\n"
                "5. Dynamic Deception Policy Engine: An adaptive state machine that recalculates the attacker's threat score and reroutes "
                "subsequent adversary interactions away from perimeter services into specialized honeynet zones (Cowrie SSH, Web decoys, "
                "DNS/SMTP decoys, or a quarantine sinkhole)."
            ),
            "where": "app_build/backend/orchestration/lab_runner.py (LabRunner._run_loop) & app_build/backend/intel/deception_policy.py"
        },
        {
            "id": "1.3",
            "title": "The Non-Negotiable Boundary: Zero Shell, Zero Host, Zero Internet",
            "simple": (
                "We built an unbreakable vault door: no matter how smart or broken the AI gets, it cannot touch the real operating "
                "system, it cannot access the internet, and it cannot execute any shell commands. It is like an actor reading from a "
                "menu of 7 safe buttons—it cannot invent an 8th button."
            ),
            "technical": (
                "NetMirage enforces three non-negotiable security boundaries that are verified at runtime by automated test suites:\n"
                "1. Zero Arbitrary Shell Execution: The codebase completely forbids 'subprocess.Popen(shell=True)', 'os.system()', or "
                "direct bash piping. Only 7 strict functions in ActionBroker can be executed:\n"
                "   - discover_lab_services (Port sweep simulation)\n"
                "   - resolve_dns (Internal domain lookup)\n"
                "   - connect_tcp (Three-way handshake test)\n"
                "   - request_http (Decoy web path GET/POST)\n"
                "   - attempt_ssh_to_lure (Cowrie credential authentication)\n"
                "   - send_icmp_probe (Decoy echo probe)\n"
                "   - inspect_session_output (Decoy session terminal harvest)\n"
                "2. Zero Host Breakout: Docker Compose strictly mandates 'cap_drop: ALL', 'security_opt: [no-new-privileges:true]', "
                "'read_only: true', and forbids 'network_mode: host' or 'privileged: true'.\n"
                "3. Zero Egress: Docker networks declare 'internal: true', which drops default gateway routing to external interfaces."
            ),
            "where": "app_build/backend/core/safety_policy.py (ALLOWLISTED_ACTIONS & validate_container_security)"
        },
        {
            "id": "1.4",
            "title": "Academic Lab Alignment: VIT BACSE203 P Computer Networks Lab",
            "simple": (
                "This project is not just a theoretical report—it is a working, physical implementation of every single experiment "
                "taught in the VIT Computer Networks curriculum, from subnet calculation and ARP resolution to TCP handshakes and HTTP "
                "protocol exchanges."
            ),
            "technical": (
                "NetMirage maps directly to the official syllabus modules of BACSE203 P:\n"
                "- Module 1 (Layer 2 / Data Link): Ethernet framing, ARP table inspection, and ARP cache poisoning detection.\n"
                "- Module 2 (Layer 3 / Network): IPv4 Classless Inter-Domain Routing (CIDR /24 subnetting), IP header TTL, ICMP echo probes.\n"
                "- Module 3 (Layer 4 / Transport): Socket programming, TCP 3-way handshake analysis, half-open SYN scan detection, port registries.\n"
                "- Module 4 (Layer 7 / Application): Domain Name System (DNS A records), HTTP/1.1 REST endpoints, SSH-2.0 protocol banners, SMTP ESMTP mail exchanges, and WebSockets (RFC 6455).\n"
                "- Module 5 & 6 (Network Security & Deception): Defensive deception routing, MITRE ATT&CK matrix correlation, and honeypot design."
            ),
            "where": "docs/ARCHITECTURE.md, docs/VIVA_PREP_GUIDE.md, and production_artifacts/viva_data.py"
        }
    ]
}

# -------------------------------------------------------------------------------------------------
# CHAPTER 2: END-TO-END LIFECYCLE OF A SINGLE RUN (STEP-BY-STEP STORY)
# -------------------------------------------------------------------------------------------------
CHAPTER_2 = {
    "title": "CHAPTER 2: END-TO-END LIFECYCLE OF A SINGLE RUN (STEP-BY-STEP STORY)",
    "intro": (
        "To truly understand how NetMirage operates, we follow the complete chronological life of a single "
        "adversarial emulation run. From the millisecond the human operator presses 'START RUN' to the instant "
        "the global kill switch terminates all active processes, every event flows through a deterministic, "
        "fail-closed pipeline."
    ),
    "steps": [
        {
            "step": 1,
            "name": "Operator Initiates Run from Dashboard",
            "simple": (
                "The user clicks the glowing green 'START RUN' button on the web console. This sends a quick 'wake-up' message "
                "to the backend server saying: 'Create a brand new experiment run right now.'"
            ),
            "technical": (
                "The React frontend invokes 'createRun()' in 'app_build/frontend/src/services/api.ts', triggering an HTTP "
                "POST request to 'http://localhost:8000/api/runs' with a JSON payload specifying the scenario ('full_adversary_emulation'). "
                "The server generates a unique run identifier 'run_YYYYMMDD_HHMMSS_xxxx' and persists a record in SQLite with status 'pending'."
            ),
            "where": "app_build/frontend/src/App.tsx (handleStartRun) -> app_build/backend/routes.py (create_run)"
        },
        {
            "step": 2,
            "name": "Control API Spawns Lab Runner & Establishes WebSocket Stream",
            "simple": (
                "The server starts the background emulation engine and opens a live, two-way walkie-talkie channel (WebSocket) "
                "with the browser so the dashboard can display live updates without refreshing."
            ),
            "technical": (
                "FastAPI's 'create_run' handler passes the new 'run_id' to 'lab_runner.start_run(run_id)', which creates an asynchronous "
                "task via 'asyncio.create_task(self._run_loop(run_id))'. Simultaneously, the React frontend connects to "
                "'ws://localhost:8000/api/runs/{run_id}/events'. The Event Bus allocates a dedicated 'asyncio.Queue' for this connection, "
                "emits an initial system envelope, and begins streaming events in real time."
            ),
            "where": "app_build/backend/orchestration/lab_runner.py (start_run) & app_build/backend/event_bus.py (subscribe)"
        },
        {
            "step": 3,
            "name": "AI Attacker Executes 3-Layer Planning Loop",
            "simple": (
                "The AI attacker looks around at what it has learned so far (Observation), thinks about what to do next (Planner), "
                "and writes a safe, polite request to test a specific port (Safe Action Request)."
            ),
            "technical": (
                "Inside '_run_loop', the engine executes the 3-layer adversary loop:\n"
                "Layer 1: 'planner.build_observation_summary()' synthesizes prior actions, discovered nodes, and open ports into an ObservationSummary dataclass.\n"
                "Layer 2: 'planner.plan_next_action()' selects the next tactical objective from the deterministic cyber-range progression state machine.\n"
                "Layer 3: Generates a 'SafeActionRequest' dataclass containing action_type, target_ip, target_port, parameters, and rationale."
            ),
            "where": "app_build/backend/core/planner.py (AIPlanner.build_observation_summary & plan_next_action)"
        },
        {
            "step": 4,
            "name": "Safety Policy Engine Evaluates Guardrails (Fail-Closed)",
            "simple": (
                "Before anything touches the network, a strict security guard checks 7 rules: Is this action on the approved list? "
                "Is the destination IP inside our lab? Is the port registered? Is the emergency kill switch active? If anything fails, "
                "the action is instantly blocked."
            ),
            "technical": (
                "'safety_policy.evaluate_action()' performs seven sequential checks:\n"
                "1. Action Allowlist: Must be in ALLOWLISTED_ACTIONS.\n"
                "2. Kill Switch: Verifies 'run.status == running'; rejects if paused or terminated.\n"
                "3. Duration Cap: Rejects if run duration exceeds 300 seconds.\n"
                "4. CIDR Verification: Target IP must fall strictly within allowed lab networks (10.0.10.0/24 to 10.0.50.0/24).\n"
                "5. Port Registry: Target port must belong to ALLOWED_LAB_PORTS (22, 53, 80, 8080, 25, 587, 2222).\n"
                "6. Rate Limiting: Max 60 actions per minute sliding window.\n"
                "7. Concurrency Lock: Max 5 concurrent active operations. Fails closed (allowed=False, status='denied') on any error."
            ),
            "where": "app_build/backend/core/safety_policy.py (SafetyPolicyEngine.evaluate_action)"
        },
        {
            "step": 5,
            "name": "Action Broker Executes Allowlisted Network Operation",
            "simple": (
                "Once approved, the Action Broker performs the exact requested action (like sending a SYN packet or an HTTP request), "
                "measures how many milliseconds it took, and bundles the result into clean JSON data."
            ),
            "technical": (
                "'action_broker.execute_action()' routes the operation to its dedicated handler (e.g., '_exec_discover_lab_services', "
                "'_exec_request_http', '_exec_attempt_ssh_to_lure'). It measures execution latency via 'time.perf_counter()', releases "
                "the concurrency counter in a 'finally' block, and returns an Action Broker Result dictionary: "
                "{action, target, port, status: 'completed', latency_ms: int, output: dict}."
            ),
            "where": "app_build/backend/core/action_broker.py (ActionBroker.execute_action)"
        },
        {
            "step": 6,
            "name": "Honeypot Decoy Ingestion & Universal Credential Redaction",
            "simple": (
                "If the attacker tried to log into our decoy SSH server with a fake password like 'SuperSecretPassword123!', "
                "our honeypot recorder immediately scrubs that password and replaces it with '[REDACTED]' so no secret leaks."
            ),
            "technical": (
                "When the action targets a honeypot (SSH, Web, DNS, or SMTP), the parameters pass through 'honeypot_normalizer'. "
                "The 'redact_credentials()' engine recursively scans dictionaries, lists, strings, and query parameters using regex "
                "to replace passwords, auth tokens, and API keys with '[REDACTED]'. A sanitized HoneypotSession record is saved to SQLite."
            ),
            "where": "app_build/backend/intel/honeypots.py (redact_credentials & HoneypotNormalizer)"
        },
        {
            "step": 7,
            "name": "Protocol Telemetry Extraction by Protocol Analyzer",
            "simple": (
                "Our passive network wire-tap notices the traffic: 'Aha! The attacker just sent a rapid burst of TCP SYN packets "
                "across the edge gateway!' It records this as a behavioral observation without touching the server."
            ),
            "technical": (
                "'protocol_analyzer.analyze_action_event()' converts the executed action into low-level network observations. "
                "For a service sweep, it generates an observation for 'port_discovery' with raw payload flags 'SYN' and incomplete handshake "
                "metrics. For SSH, it records 'ssh_credential_probing'; for DNS queries containing anomalies, it logs 'dns_anomaly'."
            ),
            "where": "app_build/backend/intel/analyzer.py (ProtocolAnalyzer.analyze_action_event)"
        },
        {
            "step": 8,
            "name": "MITRE ATT&CK Classification & Confidence Scoring",
            "simple": (
                "The system looks up the hacker playbook (MITRE ATT&CK) and says: 'This port sweep is officially Technique T1046 "
                "(Network Service Discovery) with 90% confidence!' It also bumps up the total danger meter (Threat Score)."
            ),
            "technical": (
                "'mitre_mapper.classify_observation()' evaluates the observation against 'MAPPING_RULES'. It maps 'port_discovery' "
                "to MITRE technique 'T1046' (Network Service Discovery, confidence 0.90, profile: 'reconnaissance'). It assigns technique "
                "T1110 (Brute Force) to SSH probing, and T1071.004 to DNS anomalies. The cumulative threat score increments towards 100."
            ),
            "where": "app_build/backend/intel/mitre_mapper.py (MitreAttackMapper.classify_observation)"
        },
        {
            "step": 9,
            "name": "Dynamic Deception Policy Recalculates Target Routing",
            "simple": (
                "Now the defense system strikes back intelligently: 'Because the attacker is doing reconnaissance, don't let them "
                "touch real servers—change the route so their next request lands straight into our Cowrie SSH honeypot!'"
            ),
            "technical": (
                "'deception_policy.evaluate_policy()' consumes the threat profile and confidence. Reconnaissance triggers dynamic diversion "
                "to 'ssh-lure' (10.0.20.10) or 'web-lure' (10.0.30.10). Credential brute forcing diverts the adversary to 'services-lure' "
                "(10.0.40.0/24). Network tampering triggers diversion to the 'quarantine' sinkhole (10.0.50.99). The decision is emitted over WebSocket."
            ),
            "where": "app_build/backend/intel/deception_policy.py (DeceptionPolicyEngine.evaluate_policy)"
        },
        {
            "step": 10,
            "name": "Operator Hits Terminate (Kill Switch & Teardown)",
            "simple": (
                "At any time, the user can click 'TERMINATE'. Instantly, all background loops freeze, the containers stop, "
                "and the run is safely sealed as completed."
            ),
            "technical": (
                "Clicking 'TERMINATE' fires POST '/api/runs/{run_id}/terminate'. FastAPI sets 'run.status = terminated' in SQLite and calls "
                "'lab_runner.terminate_run(run_id)', which invokes 'asyncio.Task.cancel()'. The loop catches 'asyncio.CancelledError', "
                "emits a final system event, releases concurrency locks, and cleanly tears down container network allocations."
            ),
            "where": "app_build/backend/routes.py (terminate_run) & app_build/backend/orchestration/lab_runner.py (terminate_run)"
        }
    ]
}

# -------------------------------------------------------------------------------------------------
# CHAPTER 3: COMPUTER NETWORKS CONCEPTS USED IN NETMIRAGE
# -------------------------------------------------------------------------------------------------
CHAPTER_3 = {
    "title": "CHAPTER 3: COMPUTER NETWORKS CONCEPTS USED IN NETMIRAGE",
    "intro": (
        "NetMirage is designed as an end-to-end pedagogical demonstration of classical computer networking theory "
        "applied to modern defensive cybersecurity. This chapter dissects the exact networking fundamentals, mathematics, "
        "packet structures, and RFC protocols running inside the system."
    ),
    "topics": [
        {
            "id": "3.1",
            "title": "VLAN Segmentation & IPv4 Subnetting Math (The 5 Lab Subnets)",
            "simple": (
                "Subnetting is like building separate soundproof rooms in an office building. Rather than putting everyone on one loud, "
                "chaotic floor, we assign distinct IP ranges so computers in Room A cannot talk to Room B without going through a controlled gateway."
            ),
            "technical": (
                "NetMirage establishes five distinct Classless Inter-Domain Routing (CIDR) /24 subnets:\n"
                "- Edge Subnet: 10.0.10.0/24 (Netmask 255.255.255.0, Gateway 10.0.10.1, Broadcast 10.0.10.255, Usable: 10.0.10.2 - 10.0.10.254). "
                "Hosts Edge Gateway (10.0.10.42) and Attacker Ingress (10.0.10.15).\n"
                "- SSH Decoy Subnet: 10.0.20.0/24 (Gateway 10.0.20.1). Hosts Cowrie SSH Lure (10.0.20.10).\n"
                "- Web Decoy Subnet: 10.0.30.0/24 (Gateway 10.0.30.1). Hosts Web Decoy Portal (10.0.30.10).\n"
                "- Core Services Subnet: 10.0.40.0/24 (Gateway 10.0.40.1). Hosts DNS Lure (10.0.40.10) and SMTP Lure (10.0.40.20).\n"
                "- Monitor & Quarantine Subnet: 10.0.50.0/24 (Gateway 10.0.50.1). Hosts Telemetry Sensor (10.0.50.10) and Quarantine Sinkhole (10.0.50.99).\n"
                "Docker enforces network isolation via Linux network bridges created with 'internal: true'. This parameter instructs the Docker daemon "
                "to configure iptables with a DROP rule on any packet destined for external network interfaces (eth0/wlan0), preventing internet egress."
            ),
            "where": "app_build/docker/docker-compose.lab.yml (networks section) & app_build/backend/core/safety_policy.py (is_ip_in_lab)"
        },
        {
            "id": "3.2",
            "title": "Layer 2 (Data Link Layer): ARP Framing & MITRE T1557 Detection",
            "simple": (
                "Before two computers can talk using IP addresses, they must find each other's physical hardware address (MAC address) "
                "using ARP: 'Who has IP 10.0.10.42? Tell 10.0.10.15!' If a hacker lies about who they are, that is ARP poisoning."
            ),
            "technical": (
                "Address Resolution Protocol (ARP, RFC 826) maps 32-bit IPv4 addresses to 48-bit MAC addresses within a broadcast domain. "
                "In an Ethernet frame, the EtherType field is set to 0x0806 for ARP and 0x0800 for IPv4. NetMirage's Protocol Analyzer "
                "monitors Gratuitous ARP broadcasts and rapid MAC-to-IP mapping changes. If an attacker attempts an Adversary-in-the-Middle "
                "(AiTM) ARP spoofing attack, the Protocol Analyzer detects the conflicting MAC advertisement and flags MITRE Technique "
                "T1557 with a confidence score of 0.92, triggering dynamic rerouting into the quarantine sinkhole."
            ),
            "where": "app_build/backend/intel/analyzer.py (arp_spoof_candidate) & app_build/backend/intel/mitre_mapper.py (T1557)"
        },
        {
            "id": "3.3",
            "title": "Layer 3 (Network Layer): IPv4 Headers, TTL & ICMP Anomaly Detection (T1095)",
            "simple": (
                "Every packet travelling across our subnets has an envelope containing source and destination IPs, plus a 'Time To Live' (TTL) "
                "counter that prevents packets from looping forever. We also send ICMP 'ping' messages to see if decoy servers are awake."
            ),
            "technical": (
                "An IPv4 packet header consists of 20 bytes minimum: Version (4 bits), IHL (4 bits), Type of Service (8 bits), Total Length (16 bits), "
                "Identification, Flags (DF, MF), Fragment Offset, Time to Live (TTL, 8 bits), Protocol (8 bits, e.g., 1 for ICMP, 6 for TCP, 17 for UDP), "
                "Header Checksum, and 32-bit Source/Destination IP addresses.\n"
                "NetMirage tests ICMP (Internet Control Message Protocol, RFC 792) via Type 8 (Echo Request) and Type 0 (Echo Reply). The Protocol Analyzer "
                "evaluates ICMP payload entropy. Attackers frequently hide exfiltrated data inside the optional payload field of ICMP ping packets. "
                "When anomalous payload entropy (>4.0) is detected, the system maps this to MITRE Technique T1095 (Non-Application Layer Protocol)."
            ),
            "where": "app_build/backend/core/action_broker.py (_exec_send_icmp_probe) & app_build/backend/intel/analyzer.py (icmp_payload_anomaly)"
        },
        {
            "id": "3.4",
            "title": "Layer 4 (Transport Layer): TCP 3-Way Handshake vs Half-Open SYN Scans (T1046)",
            "simple": (
                "To establish a reliable connection, TCP does a 3-step handshake: 'Hello!' (SYN), 'Hello back, ready!' (SYN-ACK), "
                "and 'Great, let us talk!' (ACK). Attackers cheat by sending only the first 'Hello' to see if a door is unlocked, "
                "then hanging up immediately with a 'Reset' (RST) to avoid being logged."
            ),
            "technical": (
                "Transmission Control Protocol (TCP, RFC 793) is connection-oriented and utilizes 16-bit source/destination ports and 32-bit "
                "Sequence/Acknowledgment numbers. A normal connection executes: Client sends SYN -> Server responds SYN-ACK -> Client sends ACK.\n"
                "In stealth reconnaissance (Nmap SYN scan), the attacker sends SYN; if the server replies SYN-ACK (port open), the attacker immediately "
                "replies with RST, terminating the half-open connection before application logs trigger. NetMirage's Protocol Analyzer inspects incomplete "
                "handshake ratios. When sequential SYN sweeps across lab ports (22, 53, 80, 8080) are observed, it generates a 'port_discovery' "
                "observation that maps to MITRE Technique T1046 (Network Service Discovery, confidence 0.90)."
            ),
            "where": "app_build/backend/intel/analyzer.py (port_discovery) & app_build/backend/intel/mitre_mapper.py (T1046)"
        },
        {
            "id": "3.5",
            "title": "Layer 7 (Application Layer): HTTP, SSH-2.0, DNS, SMTP, REST & WebSockets",
            "simple": (
                "At the top layer, real programs communicate: browsers send HTTP web requests, admins log into SSH terminals, computers look up "
                "names via DNS, and our frontend talks to our backend over super-fast WebSockets that stay open 24/7."
            ),
            "technical": (
                "NetMirage exercises five major Layer 7 protocols:\n"
                "1. HTTP/1.1 (RFC 2616): Request methods (GET, POST), URIs, and status codes (200 OK). Decoy web lures inspect path probing (/admin/login) "
                "mapping to MITRE T1190.\n"
                "2. SSH-2.0 (RFC 4253): Medium-interaction Cowrie lure emulates OpenSSH 8.9p1. Performs Diffie-Hellman / Curve25519 key exchange, "
                "harvests adversary authentication attempts, and sanitizes passwords into [REDACTED] (MITRE T1110 / T1021.004).\n"
                "3. DNS (RFC 1035): Port 53 UDP/TCP resolution of 'A' records (e.g., 'ssh.corp.internal' -> 10.0.20.10). Anomaly detector identifies "
                "covert DNS tunneling queries (MITRE T1071.004).\n"
                "4. SMTP (RFC 5321): Port 25 decoy mail server emulating ESMTP banners and recipient probing.\n"
                "5. WebSockets (RFC 6455): Upgraded from HTTP via 'Upgrade: websocket' headers, establishing persistent full-duplex bi-directional "
                "frame streaming between FastAPI backend and React frontend."
            ),
            "where": "app_build/backend/intel/honeypots.py & app_build/backend/event_bus.py & app_build/frontend/src/services/websocket.ts"
        }
    ]
}

# -------------------------------------------------------------------------------------------------
# CHAPTER 4: COMPLETE CODEBASE TOUR (FILE-BY-FILE WALKTHROUGH)
# -------------------------------------------------------------------------------------------------
CHAPTER_4 = {
    "title": "CHAPTER 4: COMPLETE CODEBASE TOUR (FILE-BY-FILE WALKTHROUGH)",
    "intro": (
        "This chapter provides an exhaustive technical tour of every file, class, function, and Docker container "
        "inside '<WORKSPACE_ROOT>/app_build/'. It explains the architectural responsibility of each file and how "
        "they interlock to form the NetMirage cyber-range platform."
    ),
    "modules": [
        {
            "file": "app_build/backend/main.py",
            "title": "Application Entry Point & FastAPI Lifespan",
            "simple": "The front door of our backend program. It starts the server, configures CORS security, and mounts all the web routes.",
            "technical": (
                "Initializes the FastAPI application instance ('app = FastAPI(title=\"NetMirage Defensive Cyber-Range\")'). "
                "Configures CORSMiddleware to allow cross-origin requests from the Vite frontend (http://localhost:5173). "
                "Defines the async 'lifespan' context manager that calls 'init_db()' on startup to ensure SQLite tables exist, "
                "and mounts the primary APIRouter from 'routes.py'."
            ),
            "functions": "init_db(), lifespan(), app.include_router(api_router)"
        },
        {
            "file": "app_build/backend/routes.py",
            "title": "RESTful Control Endpoints & WebSocket Event Stream",
            "simple": "The traffic controller. It handles buttons clicked on the web UI (like Start, Pause, Terminate) and powers the live WebSocket cable.",
            "technical": (
                "Defines 11 RESTful endpoints and 1 WebSocket handler:\n"
                "- GET /api/health: Returns operational state, active run count, and zero-egress status.\n"
                "- GET /api/topology: Returns the 5 VLAN segments, active honeypot lures, and highlighted deception paths.\n"
                "- POST /api/runs: Creates a new run, commits to database, and triggers 'lab_runner.start_run()'.\n"
                "- POST /api/runs/{id}/pause, resume, terminate: Manages run lifecycle and kill switches.\n"
                "- GET /api/runs/{id}/actions, detections, policies: Fetches historical forensics.\n"
                "- GET /api/sessions/{session_id}: Fetches honeypot sessions with credential redaction applied.\n"
                "- WS /api/runs/{id}/events: Subscribes client to EventBus queue, emits init envelope, and streams live EventEnvelopes."
            ),
            "functions": "get_health(), get_topology(), create_run(), pause_run(), terminate_run(), websocket_events()"
        },
        {
            "file": "app_build/backend/models.py & db.py",
            "title": "SQLAlchemy 2.0 ORM & The 6 Immutable Tables",
            "simple": "The permanent memory vault. It creates a local SQLite database with 6 organized tables that store every event forever.",
            "technical": (
                "'db.py' configures the SQLite engine ('sqlite:///./netmirage.db') with 'check_same_thread=False' and establishes 'SessionLocal'. "
                "'models.py' declares the 6 immutable tables using SQLAlchemy 2.0 ORM with ForeignKeys and cascading deletions:\n"
                "1. Run (runs): id, status, threat_score, active_profile, next_deception_zone, created_at, started_at, ended_at.\n"
                "2. AgentAction (agent_actions): id, run_id, timestamp, action_type, target_ip, target_port, status, latency_ms, output.\n"
                "3. Observation (observations): id, run_id, timestamp, source, protocol, behavior_type, raw_payload, details.\n"
                "4. Detection (detections): id, run_id, timestamp, source_ip, technique_id, technique_name, confidence, evidence.\n"
                "5. HoneypotSession (honeypot_sessions): id, run_id, lure_type, session_id, source_ip, commands_or_requests, metadata_json.\n"
                "6. PolicyDecision (policy_decisions): id, run_id, timestamp, threat_profile, confidence, decision, target_zone."
            ),
            "functions": "Run, AgentAction, Observation, Detection, HoneypotSession, PolicyDecision, init_db(), get_db()"
        },
        {
            "file": "app_build/backend/event_bus.py",
            "title": "Universal Event Bus & Database Event Sinks",
            "simple": "The central loudspeaker. Whenever an action, detection, or route change happens, Event Bus broadcasts it to the browser and saves it in the database.",
            "technical": (
                "Maintains an in-memory subscription map 'Dict[str, Set[asyncio.Queue]]' and history cache 'Dict[str, List[EventEnvelope]]' "
                "guarded by an 'asyncio.Lock()'. The 'publish()' method distributes incoming envelopes to all subscriber queues and invokes "
                "'_persist_event()', which maps the envelope kind ('system', 'action', 'observation', 'detection', 'honeypot', 'policy') "
                "directly into SQLite table rows within a transactional commit/rollback block."
            ),
            "functions": "EventBus.subscribe(), EventBus.unsubscribe(), EventBus.publish(), EventBus.emit(), EventBus._persist_event()"
        },
        {
            "file": "app_build/backend/core/planner.py",
            "title": "3-Layer Adversary Emulation Planner",
            "simple": "The simulated brain of the hacker. It looks at what it already discovered and chooses the next tactical move from a list of safe steps.",
            "technical": (
                "Implements a 3-layer architecture for safe adversary emulation:\n"
                "1. Layer 1 (Observation Summary): 'build_observation_summary()' parses previous actions and observations into an ObservationSummary dataclass.\n"
                "2. Layer 2 (Planner): 'plan_next_action()' advances through DETERMINISTIC_PROGRESSION (7-stage cyber-range progression: discovery -> DNS -> Web -> SSH brute force -> Session harvest -> ICMP probe -> TCP verify).\n"
                "3. Layer 3 (Safe Action Request): Returns a 'SafeActionRequest' dataclass with strict typing."
            ),
            "functions": "ObservationSummary, SafeActionRequest, AIPlanner.build_observation_summary(), AIPlanner.plan_next_action()"
        },
        {
            "file": "app_build/backend/core/safety_policy.py",
            "title": "Zero-Trust Fail-Closed Safety Policy Engine",
            "simple": "The strict bouncer. It checks every requested action against CIDR boundaries, registered ports, rate limits, and kill switches before allowing it.",
            "technical": (
                "'SafetyPolicyEngine' implements strict fail-closed security. Checks include: membership in 'ALLOWLISTED_ACTIONS', "
                "'run.status == running', duration <= 300s, IP in 'allowed_networks' (via ipaddress.ip_network containment check), "
                "port in 'allowed_ports', sliding window rate limit <= 60 actions/min, and active concurrency <= 5. "
                "Returns a 'PolicyResult(allowed=True/False, status=\"allowed\"/\"denied\", reason=str)'. Any check failure immediately halts execution."
            ),
            "functions": "SafetyPolicyEngine.evaluate_action(), is_ip_in_lab(), is_port_allowed(), check_rate_limit(), validate_container_security()"
        },
        {
            "file": "app_build/backend/core/action_broker.py",
            "title": "Mediated Action Broker (Zero Arbitrary Shell Execution)",
            "simple": "The hands and feet of the system. It executes the 7 approved actions, measures latency, and returns structured JSON.",
            "technical": (
                "Translates abstract requests into concrete operations without raw shell calls. Contains seven isolated methods:\n"
                "- '_exec_discover_lab_services': Returns subnet-tailored service inventories.\n"
                "- '_exec_resolve_dns': Resolves internal corporate hostnames via mock authoritative DNS table.\n"
                "- '_exec_connect_tcp': Simulates TCP 3-way handshake completion.\n"
                "- '_exec_request_http': Emulates HTTP GET/POST to decoy endpoints (/admin/login).\n"
                "- '_exec_attempt_ssh_to_lure': Simulates SSH-2.0 authentication handshake with banner exchange.\n"
                "- '_exec_send_icmp_probe': Simulates ICMP Echo Request/Reply with TTL verification.\n"
                "- '_exec_inspect_session_output': Harvests decoy session keystroke logs."
            ),
            "functions": "ActionBroker.execute_action(), _exec_discover_lab_services(), _exec_resolve_dns(), _exec_attempt_ssh_to_lure()"
        },
        {
            "file": "app_build/backend/orchestration/lab_runner.py",
            "title": "Lab Orchestration & Run Loop Lifecycle",
            "simple": "The master conductor. It ties together the planner, safety engine, broker, analyzers, and deception router in a smooth loop.",
            "technical": (
                "Manages active asyncio background tasks for running emulations. The '_run_loop(run_id)' method coordinates the 10-step lifecycle:\n"
                "Checks run status in DB -> Generates observation summary -> Plans action -> Evaluates safety policy -> Executes via ActionBroker -> "
                "Normalizes honeypot interactions -> Runs ProtocolAnalyzer -> Classifies via MitreAttackMapper -> Evaluates DeceptionPolicyEngine -> "
                "Emits envelopes over EventBus -> Paces execution with asyncio.sleep(). Handles cancellation and exceptions cleanly."
            ),
            "functions": "LabRunner.start_run(), pause_run(), resume_run(), terminate_run(), _run_loop()"
        },
        {
            "file": "app_build/backend/intel/analyzer.py",
            "title": "Passive Protocol Telemetry Analyzer",
            "simple": "The wire-tap. It inspects packet traffic to spot port scans, SSH brute force attacks, and hidden data channels.",
            "technical": (
                "'ProtocolAnalyzer' derives passive network observations from action events. Generates structured observation payloads for:\n"
                "- 'port_discovery': Sequential SYN sweeps across lab subnets.\n"
                "- 'tcp_syn_pattern': Established TCP handshakes with RTT latency.\n"
                "- 'web_path_probing': HTTP URI probing of administrative paths.\n"
                "- 'ssh_credential_probing': SSH cipher negotiations and auth attempts.\n"
                "- 'dns_anomaly': Anomaly detection on domain length or 'exfil' substrings.\n"
                "- 'icmp_payload_anomaly': High entropy or oversized echo payloads."
            ),
            "functions": "ProtocolAnalyzer.analyze_action_event(), ProtocolAnalyzer.analyze_scapy_packet()"
        },
        {
            "file": "app_build/backend/intel/mitre_mapper.py",
            "title": "MITRE ATT&CK Classification Engine",
            "simple": "The threat intelligence index. It tags network traffic with official MITRE IDs (like T1046) and calculates confidence scores.",
            "technical": (
                "'MitreAttackMapper' matches behavioral observations against 'MAPPING_RULES':\n"
                "- port_discovery -> T1046 (Network Service Discovery, 0.90)\n"
                "- web_path_probing -> T1190 (Exploit Public-Facing App, 0.85)\n"
                "- ssh_credential_probing -> T1110 (Brute Force, 0.95)\n"
                "- dns_anomaly -> T1071.004 (Application Layer: DNS, 0.88)\n"
                "- arp_spoof_candidate -> T1557 (Adversary-in-the-Middle, 0.92)\n"
                "- icmp_payload_anomaly -> T1095 (Non-App Layer Protocol, 0.80)\n"
                "Returns a 'MitreDetection' dataclass containing technique_id, technique_name, confidence, threat_profile, and evidence."
            ),
            "functions": "MitreDetection, MitreAttackMapper.classify_observation()"
        },
        {
            "file": "app_build/backend/intel/deception_policy.py",
            "title": "Dynamic Deception Policy Engine",
            "simple": "The active defense strategist. It decides whether to route the attacker to an SSH honeypot, a fake website, or a quarantine box.",
            "technical": (
                "'DeceptionPolicyEngine.evaluate_policy()' consumes threat profiles and confidence scores:\n"
                "- 'reconnaissance' -> Reroutes adversary to 'ssh-lure' (10.0.20.10) or 'web-lure' (10.0.30.10).\n"
                "- 'credential_probing' -> Diverts adversary deeper into 'services-lure' (10.0.40.0/24).\n"
                "- 'network_manipulation' -> Immediately restricts adversary to 'quarantine' sinkhole (10.0.50.99).\n"
                "- 'covert_channel' -> Mirrors traffic to 'dns-lure' tap (10.0.40.10).\n"
                "Returns a 'DeceptionDecision' dataclass that updates 'run.next_deception_zone'."
            ),
            "functions": "DeceptionDecision, DeceptionPolicyEngine.evaluate_policy()"
        },
        {
            "file": "app_build/backend/intel/honeypots.py",
            "title": "Honeypot Decoy Normalizers & Universal Credential Redaction",
            "simple": "The sanitizer. It cleans stolen passwords and sensitive data into '[REDACTED]' before saving to the database or showing on screen.",
            "technical": (
                "Contains 'redact_credentials(obj)': A recursive scrubbing engine that traverses dicts, lists, and strings. Redacts dictionary keys matching "
                "SENSITIVE_KEYS ('password', 'secret', 'token', 'key', 'auth_token', 'api_key'). Uses regex to scrub key-value strings (password=xxx -> password=[REDACTED]), "
                "CLI user flags (-u user:pass -> -u user:[REDACTED]), and Basic Auth headers. 'HoneypotNormalizer' defines standard normalizers for "
                "Cowrie SSH, Web lures, DNS taps, and SMTP decoys."
            ),
            "functions": "redact_credentials(), HoneypotNormalizer.normalize_cowrie_event(), normalize_web_event(), normalize_dns_event()"
        },
        {
            "file": "app_build/docker/docker-compose.lab.yml",
            "title": "Hardened Zero-Egress Docker Cyber-Range Lab",
            "simple": "The physical laboratory. Spawns 5 isolated virtual network bridges and 5 decoy microservice containers with zero internet access.",
            "technical": (
                "Defines 5 bridge networks with 'internal: true' (edge_net 10.0.10.0/24, ssh_net 10.0.20.0/24, web_net 10.0.30.0/24, "
                "services_net 10.0.40.0/24, monitor_net 10.0.50.0/24). Defines 5 microservices:\n"
                "- edge-gateway (10.0.10.42)\n"
                "- cowrie-ssh-lure (10.0.20.10)\n"
                "- web-lure (10.0.30.10)\n"
                "- dns-smtp-lure (10.0.40.10)\n"
                "- telemetry-collector (10.0.50.10)\n"
                "Every container enforces: 'security_opt: [no-new-privileges:true]', 'cap_drop: [ALL]', 'read_only: true', 'tmpfs: [/tmp:rw,noexec,nosuid]', "
                "and strict CPU/memory limits (0.5 CPUs, 256MB RAM)."
            ),
            "functions": "Networks: edge_net, ssh_net, web_net, services_net, monitor_net. Services: edge-gateway, cowrie-ssh, web-lure, dns-smtp, collector"
        },
        {
            "file": "app_build/frontend/src/App.tsx",
            "title": "React 18 Operator Console Root & State Machine",
            "simple": "The commander's screen. Ties together the top control bar, live network map, terminal feed, detection matrix, and honeypot viewer.",
            "technical": (
                "Central state coordinator written in React 18 with TypeScript. Manages state for: runs, currentRun, topology, actions, detections, "
                "policyDecisions, sessions, activeTargetIp, selectedFilterNode, and wsStatus. Mounts 'RunWebSocketClient' on run change, dynamically handles "
                "incoming EventEnvelopes, and distributes state to the 5 specialized child components."
            ),
            "functions": "App(), handleIncomingEvent(), handleStartRun(), handlePauseRun(), handleResumeRun(), handleTerminateRun()"
        },
        {
            "file": "app_build/frontend/src/components/NetworkTopology.tsx",
            "title": "Interactive VLAN Topology & Dynamic Rerouting Canvas",
            "simple": "The visual network map. Shows all 5 subnets as clean cards with glowing animated lines indicating where traffic is being redirected.",
            "technical": (
                "Renders an interactive SVG/HTML5 schematic displaying the 5 VLAN segments in high-contrast Ivory (#FAF5E9) and Charcoal (#111827). "
                "Nodes render with IP, role, and status badges. Glowing SVG polylines animate traffic paths from attacker (10.0.10.15) to active targets, "
                "turning Tangerine Yellow (#FFCC00) when traffic is diverted into deception honeypots."
            ),
            "functions": "NetworkTopology(segments, activeTargetIp, highlightedPaths, selectedFilterNode, onSelectNode)"
        },
        {
            "file": "app_build/frontend/src/components/TopControlBar.tsx",
            "title": "Operator Control Header & Threat Telemetry Badges",
            "simple": "The top dashboard dashboard. Lets the operator start, pause, resume, or terminate runs, and shows the live Threat Score meter.",
            "technical": (
                "Houses the run selection dropdown, execution buttons (Start Run, Pause, Resume, Terminate Kill Switch), Threat Score progress meter "
                "(0 to 100), active MITRE threat profile tag, current deception target zone tag, and live WebSocket heartbeat indicator."
            ),
            "functions": "TopControlBar(runs, currentRun, onSelectRun, onStartRun, onPauseRun, onResumeRun, onTerminateRun, wsStatus)"
        },
        {
            "file": "app_build/frontend/src/components/AttackerTerminal.tsx",
            "title": "Real-Time Action Broker Telemetry Tape",
            "simple": "The terminal feed. Displays every single action executed by the agent with millisecond timestamps, latency, and status badges.",
            "technical": (
                "Renders a monospace scrolling telemetry log styled in Charcoal (#111827) and Brand Green (#009B4D). Displays action ID, action type, "
                "target socket (IP:Port), latency in milliseconds, execution status (completed/denied), and expandable structured JSON output payloads."
            ),
            "functions": "AttackerTerminal(actions, filterNode)"
        },
        {
            "file": "app_build/frontend/src/components/DetectionsMatrix.tsx",
            "title": "MITRE ATT&CK Matrix & Threat Classifier View",
            "simple": "The threat analysis panel. Shows which MITRE techniques were triggered, the AI confidence level, and underlying packet evidence.",
            "technical": (
                "Renders a real-time table of detected adversary behaviors. Displays MITRE technique IDs (e.g., T1046, T1110, T1071.004), technique names, "
                "confidence progress bars, source IP addresses, and expandable JSON evidence packets containing raw protocol details."
            ),
            "functions": "DetectionsMatrix(detections)"
        },
        {
            "file": "app_build/frontend/src/components/HoneypotInspector.tsx",
            "title": "Honeypot Keystroke & Credential Forensics Drawer",
            "simple": "The forensic microscope. Shows attacker keystrokes, stolen password attempts, and HTTP headers with credentials safely redacted.",
            "technical": (
                "Specialized forensic inspector displaying captured interaction sessions from Cowrie SSH, Web lures, DNS taps, and SMTP decoys. "
                "Features terminal replay view with confirmed '[REDACTED]' badges on sensitive credentials, timing intervals, and remote client banners."
            ),
            "functions": "HoneypotInspector(sessions)"
        }
    ]
}

# -------------------------------------------------------------------------------------------------
# CHAPTER 5: DATA CONTRACTS & DATABASE SCHEMAS EXPLAINED
# -------------------------------------------------------------------------------------------------
CHAPTER_5 = {
    "title": "CHAPTER 5: DATA CONTRACTS & DATABASE SCHEMAS EXPLAINED",
    "intro": (
        "In a high-security cyber-range, strict data contracts prevent injection attacks and guarantee non-repudiation. "
        "Every event emitted or stored in NetMirage adheres to formal Pydantic v2 schemas and SQLAlchemy ORM models."
    ),
    "envelope_example": """{
  "run_id": "run_20261021_114500_a1b2",
  "event_id": "evt_9c8f3e1a",
  "timestamp": "2026-10-21T06:15:00.123456Z",
  "kind": "action",
  "source": "action-broker",
  "payload": {
    "action_id": "act_f4e2a109",
    "action_type": "attempt_ssh_to_lure",
    "target_ip": "10.0.20.10",
    "target_port": 22,
    "parameters": {
      "username": "root",
      "password": "[REDACTED]",
      "command": "cat /etc/passwd"
    },
    "status": "completed",
    "latency_ms": 24,
    "output": {
      "banner": "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6",
      "auth_status": "accepted_by_lure",
      "session_output": "uid=0(root) gid=0(root) groups=0(root)"
    }
  }
}""",
    "envelope_explanation": [
        ("run_id", "String(64)", "Unique run instance identifier binding this event to its specific emulation lifecycle."),
        ("event_id", "String(64)", "Globally unique event token prefixed with 'evt_' for distributed event tracing and deduplication."),
        ("timestamp", "ISO 8601 UTC", "Microsecond-accurate Zulu timestamp ensuring strict chronological forensic sequencing."),
        ("kind", "Enum String", "Event domain category: 'system', 'action', 'observation', 'detection', 'policy', or 'honeypot'."),
        ("source", "String(64)", "Subsystem that originated the event: 'action-broker', 'safety-policy', 'protocol-analyzer', 'deception-router', or 'system'."),
        ("payload", "JSON Object", "Domain-specific structured data conforming to typed schemas with all sensitive credentials redacted.")
    ],
    "broker_example": """{
  "action": "discover_lab_services",
  "target": "10.0.10.42",
  "port": 80,
  "status": "completed",
  "latency_ms": 12,
  "output": {
    "scanned_target": "10.0.10.42",
    "open_services": [
      {
        "port": 80,
        "service": "HTTP/Reverse-Proxy",
        "banner": "Edge-Gateway-v2.1"
      }
    ],
    "message": "Service discovery completed on 10.0.10.42"
  }
}""",
    "broker_explanation": [
        ("action", "String", "The exact allowlisted action name executed from the 7 permitted functions."),
        ("target", "IPv4 String", "Validated destination IPv4 address inside the authorized /24 lab CIDR blocks."),
        ("port", "Integer", "Target port verified against the registered lab ports registry (e.g., 22, 53, 80)."),
        ("status", "Enum String", "Terminal execution state: 'completed', 'denied', 'failed', or 'timed_out'."),
        ("latency_ms", "Integer", "Round-trip execution latency measured via high-precision hardware timers (perf_counter)."),
        ("output", "JSON Object / String", "Structured result payload containing discovered banners, HTTP response previews, or session text.")
    ],
    "tables": [
        {
            "name": "runs",
            "pk": "id (String 64)",
            "purpose": "Primary root table tracking the lifecycle, threat status, and deception state of each emulation experiment.",
            "columns": "id, status, threat_score, active_profile, next_deception_zone, created_at, started_at, ended_at, metadata_json"
        },
        {
            "name": "agent_actions",
            "pk": "id (String 64)",
            "purpose": "Immutable ledger of all safe action requests submitted by the planner and processed by the Action Broker.",
            "columns": "id, run_id (FK), timestamp, action_type, target_ip, target_port, parameters, status, latency_ms, output"
        },
        {
            "name": "observations",
            "pk": "id (String 64)",
            "purpose": "Passive network telemetry records derived from raw traffic analysis by the Protocol Analyzer.",
            "columns": "id, run_id (FK), timestamp, source, source_ip, destination_ip, protocol, behavior_type, raw_payload, details"
        },
        {
            "name": "detections",
            "pk": "id (String 64)",
            "purpose": "Adversary behavior classifications tagged with MITRE ATT&CK technique IDs, names, and confidence scores.",
            "columns": "id, run_id (FK), timestamp, source_ip, technique_id, technique_name, confidence, evidence"
        },
        {
            "name": "honeypot_sessions",
            "pk": "id (String 64)",
            "purpose": "Forensic records of decoy interactions (SSH, Web, DNS, SMTP) with credentials strictly sanitized.",
            "columns": "id, run_id (FK), lure_type, session_id, source_ip, source_port, started_at, ended_at, commands_or_requests, metadata_json"
        },
        {
            "name": "policy_decisions",
            "pk": "id (String 64)",
            "purpose": "Audit log of dynamic deception routing calculations and active zone containment decisions.",
            "columns": "id, run_id (FK), timestamp, threat_profile, confidence, decision, target_zone, evidence"
        }
    ]
}

# -------------------------------------------------------------------------------------------------
# CHAPTER 6: HOW TO RUN, DEMO & TEST THE PROJECT
# -------------------------------------------------------------------------------------------------
CHAPTER_6 = {
    "title": "CHAPTER 6: HOW TO RUN, DEMO & TEST THE PROJECT",
    "intro": (
        "This chapter provides the exact operational commands, faculty demonstration script, and test execution procedures "
        "required to run and defend NetMirage during the laboratory evaluation."
    ),
    "startup_script_ps1": "powershell -ExecutionPolicy Bypass -File \"<WORKSPACE_ROOT>/app_build/start_netmirage.ps1\"",
    "manual_commands": [
        ("Step 1: Virtual Environment", "cd app_build/backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt"),
        ("Step 2: Database Setup", "cd app_build/backend && .venv/Scripts/python -c \"from app_build.backend.db import init_db; init_db()\""),
        ("Step 3: Docker Lab Start", "docker compose -f app_build/docker/docker-compose.lab.yml up -d (or rely on built-in emulator)"),
        ("Step 4: Launch Backend API", "cd <WORKSPACE_ROOT> && app_build/backend/.venv/Scripts/python -m uvicorn app_build.backend.main:app --host 0.0.0.0 --port 8000"),
        ("Step 5: Launch Frontend UI", "cd app_build/frontend && npm install && npm run dev -- --host 0.0.0.0 --port 5173")
    ],
    "demo_script": [
        ("00:00 - 00:30", "Project Overview & Topology", "Open http://localhost:5173. Point out the Ivory/Charcoal palette and the 5 VLAN subnet cards. Explain the zero-egress architecture."),
        ("00:30 - 01:15", "Initiate Run & Live WebSocket", "Click 'START RUN'. Point out the WebSocket indicator turning green, the threat score meter starting at 0, and the initial edge scan."),
        ("01:15 - 02:00", "Attacker Terminal & Action Broker", "Show the live Action Broker telemetry tape. Point out the millisecond latency, structured JSON output, and zero raw bash shell."),
        ("02:00 - 02:45", "Protocol Analysis & MITRE Matrix", "Scroll to the Detections Matrix. Point out MITRE Technique T1046, T1110, and T1071.004 appearing live with 0.85-0.95 confidence scores."),
        ("02:45 - 03:30", "Dynamic Deception & Route Diversion", "Show the Network Topology map. Point out the animated path dynamically re-routing from Edge to Cowrie SSH lure and Services lure in Tangerine Yellow."),
        ("03:30 - 04:00", "Honeypot Inspector & Credential Redaction", "Open the Honeypot Inspector drawer. Show the captured SSH login attempt and demonstrate that the password is safe [REDACTED]."),
        ("04:00 - 04:30", "Global Kill Switch Demonstration", "Click 'PAUSE' to freeze emulation; click 'RESUME' to continue; click 'TERMINATE' to trigger immediate container teardown.")
    ],
    "tests_summary": "The test suite inside 'app_build/backend/tests/' consists of 24 automated tests executed via 'pytest':",
    "test_command": "& \"<WORKSPACE_ROOT>/app_build/backend/.venv/Scripts/python.exe\" -m pytest \"<WORKSPACE_ROOT>/app_build/backend/tests\" -v",
    "test_table": [
        ("test_api_and_db.py", "6 tests", "CRUD operations on all 6 tables, /api/health, /api/topology, run lifecycle, session redaction, WebSocket streaming."),
        ("test_docker_policy.py", "3 tests", "docker-compose validation, zero-egress internal: true check, container security boundaries (cap_drop: ALL, read_only)."),
        ("test_intel_and_deception.py", "5 tests", "Credential redaction engine, Cowrie SSH normalization, Web lure normalization, MITRE mapper, Deception routing."),
        ("test_safety_and_broker.py", "9 tests", "Out-of-CIDR denied, unregistered ports denied, unapproved actions denied, rate limiting, kill switch, Action Broker execution."),
        ("test_milestone1_e2e.py", "1 test", "Full end-to-end multi-stage simulation validating all 10 lifecycle stages in a single automated integration run.")
    ]
}

# -------------------------------------------------------------------------------------------------
# CHAPTER 7: SECURITY INVARIANTS, FAILURE MODES & VIVA DEFENSE
# -------------------------------------------------------------------------------------------------
CHAPTER_7 = {
    "title": "CHAPTER 7: SECURITY INVARIANTS, FAILURE MODES & VIVA DEFENSE",
    "intro": (
        "This chapter consolidates NetMirage's core defense-in-depth engineering principles, fault tolerance mechanisms, "
        "and individual defense preparation topics for the four student candidates during faculty cross-questioning."
    ),
    "security_invariants": [
        ("1. Zero Arbitrary Shell Execution", "Subprocess execution with shell=True is completely banned. All model decisions are translated through the 7 strictly parameterized Action Broker functions."),
        ("2. Fail-Closed Policy Engine", "Any missing parameter, unmapped port, out-of-CIDR IP address, or rate-limit violation immediately returns status: 'denied'. No operation executes without explicit affirmative policy clearance."),
        ("3. Strict Zero Egress", "Docker Compose bridges specify 'internal: true'. Default routing to the host's physical network adapters is omitted, preventing WAN data transmission."),
        ("4. Container Least Privilege", "All lab containers declare 'cap_drop: ALL', 'security_opt: [no-new-privileges:true]', 'read_only: true', and memory/CPU limits."),
        ("5. Universal Credential Redaction", "Passwords, secrets, tokens, and authorization headers are sanitized to '[REDACTED]' before persisting to SQLite or emitting over WebSockets.")
    ],
    "failure_modes": [
        ("Docker Daemon Inactive", "The system automatically falls back to the deterministic zero-egress lab emulator, allowing 100% functional UI demonstration and testing without Docker installed."),
        ("Rate Limit Saturation", "If an autonomous agent exceeds 60 actions/minute, the Safety Policy Engine denies requests with HTTP 429 semantics, preserving host stability."),
        ("WebSocket Client Drop", "If the browser disconnects or reloads, the Event Bus retains event history in memory and replays all historical events upon reconnection."),
        ("Uncaught Planner Exception", "The LabRunner event loop wraps execution in a try-except block, automatically updating run status to 'failed' and cleanly releasing concurrency locks.")
    ],
    "candidate_defense": [
        {
            "name": "Abhisumat Panda",
            "reg_no": "25BYB0202",
            "focus": "Network Virtualization, Subnetting Math & Docker Hardening",
            "files": "app_build/docker/docker-compose.lab.yml & app_build/backend/tests/test_docker_policy.py",
            "defense_topic": "Explains how the 5 /24 CIDRs are segregated, how Docker 'internal: true' modifies host routing tables, and why 'cap_drop: ALL' stops container breakouts."
        },
        {
            "name": "Atharva Parmar",
            "reg_no": "25BYB0180",
            "focus": "AI Planner, Safety Policy Engine & Action Broker",
            "files": "app_build/backend/core/planner.py, safety_policy.py, action_broker.py",
            "defense_topic": "Defends the 3-layer adversary loop, explains the 7-stage deterministic progression, and proves why the fail-closed policy engine rejects out-of-bounds IPs."
        },
        {
            "name": "Manas Patel",
            "reg_no": "25BYB0190",
            "focus": "Protocol Telemetry, MITRE ATT&CK Mapping & Honeypot Forensics",
            "files": "app_build/backend/intel/analyzer.py, mitre_mapper.py, honeypots.py, deception_policy.py",
            "defense_topic": "Explains how TCP SYN scans and DNS queries are detected passively, how confidence scores (0.80-0.95) are calculated, and how regex credential redaction works."
        },
        {
            "name": "Varun Agarwal",
            "reg_no": "25BYB0186",
            "focus": "Control API, WebSocket Event Bus, Database & Operator Console",
            "files": "app_build/backend/main.py, routes.py, event_bus.py, models.py, app_build/frontend/src/App.tsx",
            "defense_topic": "Walks through the FastAPI REST routes, explains how the Event Bus manages asyncio queues and replay, and demonstrates real-time React state synchronization."
        }
    ]
}
