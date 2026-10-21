import pytest
from app_build.backend.intel.honeypots import honeypot_normalizer, redact_credentials
from app_build.backend.intel.analyzer import protocol_analyzer
from app_build.backend.intel.mitre_mapper import mitre_mapper
from app_build.backend.intel.deception_policy import deception_policy

def test_credential_redaction_engine():
    raw_payload = {
        "username": "admin",
        "password": "SuperSecretPassword123!",
        "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "nested": {
            "api_key": "live_key_998877",
            "safe_field": "hello world"
        },
        "command_list": [
            {"cmd": "curl -u admin:hunter2 http://internal.corp"},
            {"cmd": "export SECRET_KEY=xyz123"}
        ]
    }
    sanitized = redact_credentials(raw_payload)
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["auth_token"] == "[REDACTED]"
    assert sanitized["nested"]["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["safe_field"] == "hello world"
    assert "hunter2" not in str(sanitized)

def test_cowrie_ssh_normalization_and_redaction():
    event = honeypot_normalizer.normalize_cowrie_event(
        run_id="run_intel_01",
        session_id="ses_cowrie_test",
        source_ip="10.0.10.15",
        source_port=44321,
        username="root",
        password="MyPlainTextPassword!",
        command="cat /etc/shadow",
        raw_metadata={"private_key": "BEGIN RSA PRIVATE KEY"}
    )
    assert event["lure_type"] == "cowrie_ssh"
    assert event["source_ip"] == "10.0.10.15"
    cmd_entry = event["commands_or_requests"][0]
    assert cmd_entry["username"] == "root"
    assert cmd_entry["password"] == "[REDACTED]"
    assert cmd_entry["command"] == "cat /etc/shadow"
    assert event["metadata"]["private_key"] == "[REDACTED]"

def test_web_lure_normalization():
    event = honeypot_normalizer.normalize_web_event(
        run_id="run_intel_01",
        session_id="ses_web_test",
        source_ip="10.0.10.15",
        method="POST",
        path="/admin/login",
        user_agent="SqlMap/1.4",
        body={"username": "admin", "password": "pass123Password!"}
    )
    assert event["lure_type"] == "web_lure"
    req_entry = event["commands_or_requests"][0]
    assert req_entry["path"] == "/admin/login"
    assert req_entry["body"]["password"] == "[REDACTED]"

def test_protocol_analyzer_and_mitre_mapping():
    # 1. Port discovery -> T1046
    obs_list = protocol_analyzer.analyze_action_event(
        run_id="run_intel_01",
        action={"action_type": "discover_lab_services", "target_ip": "10.0.10.42", "target_port": 80}
    )
    assert len(obs_list) >= 1
    obs = obs_list[0]
    assert obs["behavior_type"] == "port_discovery"
    detection = mitre_mapper.classify_observation(obs)
    assert detection is not None
    assert detection.technique_id == "T1046"
    assert detection.technique_name == "Network Service Discovery"
    assert 0.60 <= detection.confidence <= 0.99
    assert detection.threat_profile == "reconnaissance"

    # 2. SSH Credential Probing -> T1110
    obs_ssh = protocol_analyzer.analyze_action_event(
        run_id="run_intel_01",
        action={"action_type": "attempt_ssh_to_lure", "target_ip": "10.0.20.10", "target_port": 22}
    )
    det_ssh = mitre_mapper.classify_observation(obs_ssh[0])
    assert det_ssh.technique_id == "T1110"
    assert 0.60 <= det_ssh.confidence <= 0.99
    assert det_ssh.threat_profile == "credential_probing"

    # 3. Web Path Probing -> T1190
    obs_web = protocol_analyzer.analyze_action_event(
        run_id="run_intel_01",
        action={"action_type": "request_http", "target_ip": "10.0.30.10", "target_port": 80, "parameters": {"path": "/admin"}}
    )
    det_web = mitre_mapper.classify_observation(obs_web[0])
    assert det_web.technique_id == "T1190"
    assert det_web.threat_profile == "reconnaissance"

    # 4. DNS covert-channel / anomaly -> T1071.004
    obs_dns = protocol_analyzer.analyze_action_event(
        run_id="run_intel_01",
        action={"action_type": "resolve_dns", "target_ip": "10.0.40.10", "target_port": 53, "parameters": {"query": "adversary-exfil.net"}}
    )
    det_dns = mitre_mapper.classify_observation(obs_dns[0])
    assert det_dns.technique_id == "T1071.004"
    assert det_dns.threat_profile == "covert_channel"

    # 5. ICMP anomaly -> T1095
    obs_icmp = protocol_analyzer.analyze_action_event(
        run_id="run_intel_01",
        action={"action_type": "send_icmp_probe", "target_ip": "10.0.40.20", "target_port": 25}
    )
    det_icmp = mitre_mapper.classify_observation(obs_icmp[0])
    assert det_icmp.technique_id == "T1095"
    assert det_icmp.threat_profile == "covert_channel"

def test_dynamic_deception_policy_transitions():
    # Reconnaissance -> ssh-lure or web-lure
    d1 = deception_policy.evaluate_policy("reconnaissance", 0.90, {"protocol": "TCP"})
    assert d1.target_zone == "ssh-lure"

    d1_web = deception_policy.evaluate_policy("reconnaissance", 0.85, {"protocol": "HTTP"})
    assert d1_web.target_zone == "web-lure"

    # Credential probing -> deeper services-lure
    d2 = deception_policy.evaluate_policy("credential_probing", 0.95, {})
    assert d2.target_zone == "services-lure"

    # Network manipulation -> quarantine
    d3 = deception_policy.evaluate_policy("network_manipulation", 0.92, {})
    assert d3.target_zone == "quarantine"

    # Covert channel -> dns-lure
    d4 = deception_policy.evaluate_policy("covert_channel", 0.88, {})
    assert d4.target_zone == "dns-lure"
