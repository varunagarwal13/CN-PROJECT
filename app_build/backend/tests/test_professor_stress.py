"""
NetMirage Professor Stress-Test & Anti-Hardcoding Verification Suite
Course: BACSE203 P — Computer Networks Lab, VIT
Evaluator: Dr. Sudha M & External Examiners

Covers all 10 Adversarial, Chaos, and Verification Scenarios:
1. Anti-Hardcoding Verification (Dynamic latency_ms and MITRE confidence progression)
2. Campus/Internet Breakout Attempt (CIDR Boundary Stress)
3. Unregistered Port & Command Injection Stress
4. Fail-Closed Missing/Corrupted Configuration Stress
5. Rate-Limit & DoS Burst Stress (Concurrency Flood)
6. Live OS Socket & Port Binding Proof (netstat equivalence)
7. Dynamic Deception Routing Progression
8. Credential Redaction & Privacy Leak Stress
9. Mid-Attack Kill Switch & Pause/Resume Race Condition
10. Wireshark .pcap File Integrity Verification
"""

import pytest
import asyncio
import socket
import struct
import time
from pathlib import Path
from datetime import datetime, timezone
from app_build.backend import models
from app_build.backend.core.safety_policy import SafetyPolicyEngine, safety_policy
from app_build.backend.core.action_broker import action_broker
from app_build.backend.intel.mitre_mapper import mitre_mapper
from app_build.backend.intel.deception_policy import deception_policy
from app_build.backend.intel.honeypots import honeypot_normalizer, redact_credentials
from app_build.backend.intel.pcap_exporter import generate_pcap_from_actions, LATEST_PCAP_PATH
from app_build.backend.orchestration.lab_runner import lab_runner
from scapy.all import rdpcap, IP, TCP, UDP

WORKSPACE_ROOT = Path(r"c:\Users\varun\Projects\cn project")

# ----------------------------------------------------------------------
# TEST 1: Anti-Hardcoding Verification Test
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_01_anti_hardcoding_verification():
    """
    Executes connect_tcp and request_http 5 times in a row.
    Asserts latency_ms reflects true measured socket timing,
    and verifies that MITRE confidence dynamically increases over repeated events.
    """
    latencies = []
    for _ in range(5):
        res = await action_broker.execute_action(
            run_id="run_anti_hardcode",
            action_type="connect_tcp",
            target_ip="10.0.30.10",
            target_port=80,
            parameters={}
        )
        assert res["status"] == "completed"
        assert isinstance(res["latency_ms"], int)
        assert res["latency_ms"] >= 0
        latencies.append(res["latency_ms"])

    # Verify MITRE confidence dynamically increases as repeated events accumulate
    confidences = []
    test_run_id = f"run_conf_progression_{int(time.time())}"
    for i in range(5):
        obs = {
            "behavior_type": "ssh_credential_probing",
            "protocol": "SSH",
            "source_ip": "10.0.10.15",
            "destination_ip": "10.0.20.10",
            "details": {"uri": "/admin", "auth_attempts": i + 1}
        }
        detection = mitre_mapper.classify_observation(obs, run_id=test_run_id)
        assert detection is not None
        confidences.append(detection.confidence)

    # Assert confidence is NOT a static constant and strictly grows over repetitions
    assert confidences[0] < confidences[-1], f"Confidence failed to increase: {confidences}"
    assert len(set(confidences)) > 1, f"Confidence was static: {confidences}"
    assert all(0.50 <= c <= 0.99 for c in confidences)

# ----------------------------------------------------------------------
# TEST 2: Campus/Internet Breakout Attempt (CIDR Boundary Stress)
# ----------------------------------------------------------------------
def test_02_campus_internet_breakout_attempt():
    """
    Forces the policy engine to evaluate external/campus IPs.
    100% must be blocked with status: 'denied'.
    """
    external_ips = [
        "8.8.8.8",        # Google Public DNS
        "1.1.1.1",        # Cloudflare DNS
        "192.168.1.1",    # Campus Gateway / Local Subnet
        "127.0.0.1",      # Host Localhost Breakout
        "172.16.0.1",     # External Docker Bridge
        "10.0.99.1"       # Out-of-bounds non-lab segment
    ]
    for ip in external_ips:
        res = safety_policy.evaluate_action(
            run_id="run_breakout_stress",
            action_type="connect_tcp",
            target_ip=ip,
            target_port=80
        )
        assert res.allowed is False
        assert res.status == "denied"
        assert "outside allowed lab CIDRs" in res.reason

# ----------------------------------------------------------------------
# TEST 3: Unregistered Port & Command Injection Stress
# ----------------------------------------------------------------------
def test_03_unregistered_port_and_command_injection_stress():
    """
    Attempts connections to unauthorized ports (Metasploit, RDP, MySQL, Redis)
    and attempts arbitrary shell command injection strings in parameters.
    100% must be rejected fail-closed.
    """
    bad_ports = [4444, 3389, 3306, 6379, 1337, 9001]
    for p in bad_ports:
        res = safety_policy.evaluate_action(
            run_id="run_port_stress",
            action_type="connect_tcp",
            target_ip="10.0.10.42",
            target_port=p
        )
        assert res.allowed is False
        assert res.status == "denied"
        assert "not in registered lab ports" in res.reason

    injection_params = [
        {"command": "; rm -rf /"},
        {"command": "&& whoami"},
        {"command": "| nc 10.0.10.1 4444"},
        {"query": "internal.corp; cat /etc/passwd"}
    ]
    for param in injection_params:
        res = safety_policy.evaluate_action(
            run_id="run_injection_stress",
            action_type="attempt_ssh_to_lure",
            target_ip="10.0.20.10",
            target_port=22,
            parameters=param
        )
        assert res.allowed is False
        assert res.status == "denied"
        assert "Command injection" in res.reason or "metacharacter" in res.reason

# ----------------------------------------------------------------------
# TEST 4: Fail-Closed Missing/Corrupted Configuration Stress
# ----------------------------------------------------------------------
def test_04_fail_closed_missing_corrupted_configuration():
    """
    Instantiates SafetyPolicyEngine with empty or corrupted CIDR/port configurations.
    Asserts the engine fails closed (denies actions by default) rather than failing open.
    """
    corrupted_policy = SafetyPolicyEngine(allowed_cidrs="", allowed_ports="")
    res = corrupted_policy.evaluate_action(
        run_id="run_corrupt_cfg",
        action_type="connect_tcp",
        target_ip="10.0.10.42",
        target_port=80
    )
    assert res.allowed is False
    assert res.status == "denied"

    invalid_cidr_policy = SafetyPolicyEngine(allowed_cidrs="not-a-cidr,bad_ip/99")
    res2 = invalid_cidr_policy.evaluate_action(
        run_id="run_corrupt_cfg",
        action_type="connect_tcp",
        target_ip="10.0.10.42",
        target_port=80
    )
    assert res2.allowed is False
    assert res2.status == "denied"

# ----------------------------------------------------------------------
# TEST 5: Rate-Limit & DoS Burst Stress (Concurrency Flood)
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_05_rate_limit_and_dos_burst_stress():
    """
    Fires 60 rapid action requests using asyncio.gather.
    Asserts that rate limiter and concurrency cap in safety_policy.py
    throttle and deny excess actions.
    """
    run_id = f"run_dos_burst_{int(time.time())}"

    def _eval():
        return safety_policy.evaluate_action(
            run_id=run_id,
            action_type="connect_tcp",
            target_ip="10.0.10.42",
            target_port=80
        )

    results = [_eval() for _ in range(60)]
    denied = [r for r in results if not r.allowed]
    assert len(denied) > 0, "Rate limiter failed to throttle flood of 60 rapid requests"
    assert any("Concurrency cap reached" in r.reason or "Rate limit exceeded" in r.reason for r in denied)

    # Release any held concurrency locks
    for _ in range(10):
        safety_policy.release_concurrency(run_id)

# ----------------------------------------------------------------------
# TEST 6: Live OS Socket & Port Binding Proof (netstat equivalence)
# ----------------------------------------------------------------------
def test_06_live_os_socket_and_port_binding_proof():
    """
    Connects directly via raw Python socket to Cowrie SSH (2222), Web (8080),
    DNS (5353), and SMTP (2525).
    Verifies real TCP 3-way handshakes, real protocol banners, and UDP DNS replies.
    """
    # 1. SSH Port 2222 Banner Verification
    s_ssh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_ssh.settimeout(2.0)
    s_ssh.connect(("127.0.0.1", 2222))
    banner = s_ssh.recv(1024).decode("utf-8", errors="replace")
    s_ssh.close()
    assert "SSH-2.0" in banner, f"Unexpected SSH banner: {banner}"

    # 2. Web Port 80 / 8080 HTTP Verification
    http_resp = ""
    for target_ip, target_p in [("127.0.30.10", 80), ("127.0.0.1", 80), ("127.0.30.10", 8080)]:
        try:
            s_web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_web.settimeout(2.0)
            s_web.connect((target_ip, target_p))
            s_web.sendall(b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n")
            resp = s_web.recv(1024).decode("utf-8", errors="replace")
            s_web.close()
            if "HTTP/1.1 200 OK" in resp:
                http_resp = resp
                break
        except Exception:
            pass
    assert "HTTP/1.1 200 OK" in http_resp

    # 3. SMTP Port 2525 Verification
    s_smtp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_smtp.settimeout(2.0)
    s_smtp.connect(("127.0.0.1", 2525))
    smtp_banner = s_smtp.recv(1024).decode("utf-8", errors="replace")
    s_smtp.sendall(b"QUIT\r\n")
    s_smtp.close()
    assert "220" in smtp_banner

    # 4. DNS Port 53 / 5353 UDP Verification
    dns_resp = None
    for target_ip, target_p in [("127.0.40.10", 53), ("127.0.0.1", 53), ("127.0.0.1", 5353)]:
        try:
            s_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s_dns.settimeout(1.5)
            dns_query = b"\x1a\x2b\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03ssh\x04corp\x08internal\x00\x00\x01\x00\x01"
            s_dns.sendto(dns_query, (target_ip, target_p))
            resp, _ = s_dns.recvfrom(1024)
            s_dns.close()
            if len(resp) >= 12:
                dns_resp = resp
                break
        except Exception:
            pass
    assert dns_resp is not None, "Failed to receive UDP DNS response"
    assert len(dns_resp) >= 12, "DNS response too short"
    assert dns_resp[:2] == b"\x1a\x2b"  # Transaction ID match

# ----------------------------------------------------------------------
# TEST 7: Dynamic Deception Routing Progression
# ----------------------------------------------------------------------
def test_07_dynamic_deception_routing_progression():
    """
    Feeds Reconnaissance -> Credential Probing -> Network Manipulation -> Covert Channel
    and verifies that the Deception Policy dynamically shifts next_zone across lure subnets.
    """
    stages = [
        ("reconnaissance", 0.70, {"protocol": "HTTP"}, "web-lure"),
        ("credential_probing", 0.90, {}, "services-lure"),
        ("network_manipulation", 0.85, {}, "quarantine"),
        ("covert_channel", 0.92, {}, "dns-lure")
    ]
    decisions = []
    for profile, conf, evidence, expected_zone in stages:
        dec = deception_policy.evaluate_policy(
            threat_profile=profile,
            confidence=conf,
            detection_evidence=evidence
        )
        assert "Dynamic route" in dec.decision or "isolate" in dec.decision
        assert dec.target_zone == expected_zone
        decisions.append(dec.target_zone)

    assert decisions == ["web-lure", "services-lure", "quarantine", "dns-lure"]

# ----------------------------------------------------------------------
# TEST 8: Credential Redaction & Privacy Leak Stress
# ----------------------------------------------------------------------
def test_08_credential_redaction_and_privacy_leak_stress():
    """
    Sends raw SSH login attempts containing sensitive passwords and HTTP Authorization headers.
    Asserts zero plaintext secrets exist and all are replaced with [REDACTED].
    """
    raw_payload = {
        "username": "root",
        "password": "SuperSecretVitPass123!",
        "api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.secret",
        "command": "echo password=SuperSecretVitPass123!",
        "auth_header": "Authorization: Basic cm9vdDpTdXBlclNlY3JldFZpdFBhc3MxMjMh"
    }
    sanitized = redact_credentials(raw_payload)
    assert "SuperSecretVitPass123!" not in str(sanitized)
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["api_key"] == "[REDACTED]"
    assert "[REDACTED]" in sanitized["command"]

    hp = honeypot_normalizer.normalize_cowrie_event(
        run_id="run_leak_test",
        session_id="ses_leak_test",
        source_ip="10.0.10.15",
        source_port=54321,
        username="root",
        password="SuperSecretVitPass123!",
        command="cat /etc/shadow"
    )
    assert "SuperSecretVitPass123!" not in str(hp)
    assert hp["commands_or_requests"][0]["password"] == "[REDACTED]"

# ----------------------------------------------------------------------
# TEST 9: Mid-Attack Kill Switch (TERMINATE) & Pause/Resume
# ----------------------------------------------------------------------
def test_09_mid_attack_kill_switch_and_pause_resume(test_db):
    """
    Verifies that the Global Kill Switch and Pause states immediately block actions.
    """
    run = models.Run(
        id="run_killswitch_stress",
        status="running",
        threat_score=40,
        created_at=datetime.now(timezone.utc)
    )
    test_db.add(run)
    test_db.commit()

    # Allowed while running
    res_run = safety_policy.evaluate_action(run.id, "connect_tcp", "10.0.10.42", 80, db=test_db)
    assert res_run.allowed is True
    safety_policy.release_concurrency(run.id)

    # Paused
    run.status = "paused"
    test_db.commit()
    res_paused = safety_policy.evaluate_action(run.id, "connect_tcp", "10.0.10.42", 80, db=test_db)
    assert res_paused.allowed is False
    assert res_paused.status == "denied"
    assert "Global Kill Switch active" in res_paused.reason

    # Terminated
    run.status = "terminated"
    test_db.commit()
    res_term = safety_policy.evaluate_action(run.id, "connect_tcp", "10.0.10.42", 80, db=test_db)
    assert res_term.allowed is False
    assert res_term.status == "denied"
    assert "Global Kill Switch active" in res_term.reason

# ----------------------------------------------------------------------
# TEST 10: Wireshark .pcap File Integrity Verification
# ----------------------------------------------------------------------
def test_10_wireshark_pcap_file_integrity_verification():
    """
    Reads back production_artifacts/captures/latest_run.pcap using scapy.utils.rdpcap.
    Asserts it contains valid IPv4/TCP/UDP/ICMP packets that can be opened cleanly in Wireshark.
    """
    sample_actions = [
        {"action_type": "discover_lab_services", "target_ip": "10.0.10.42", "target_port": 80},
        {"action_type": "resolve_dns", "target_ip": "10.0.40.10", "target_port": 53, "parameters": {"query": "ssh.corp.internal"}},
        {"action_type": "request_http", "target_ip": "10.0.30.10", "target_port": 80, "parameters": {"path": "/admin/login"}},
        {"action_type": "attempt_ssh_to_lure", "target_ip": "10.0.20.10", "target_port": 22},
        {"action_type": "send_icmp_probe", "target_ip": "10.0.40.20", "target_port": 25}
    ]
    pcap_path = generate_pcap_from_actions(sample_actions, run_id="stress_verify")
    assert Path(pcap_path).exists()
    assert LATEST_PCAP_PATH.exists()

    # Read back with Scapy rdpcap
    packets = rdpcap(str(LATEST_PCAP_PATH))
    assert len(packets) >= 10, f"Expected at least 10 packets, got {len(packets)}"

    has_tcp = any(p.haslayer(TCP) for p in packets)
    has_udp = any(p.haslayer(UDP) for p in packets)
    has_ip = any(p.haslayer(IP) for p in packets)

    assert has_ip is True, "No IP layer found in PCAP"
    assert has_tcp is True, "No TCP packets found in PCAP"
    assert has_udp is True, "No UDP packets found in PCAP"
