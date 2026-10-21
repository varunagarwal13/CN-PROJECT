"""
NetMirage MITRE ATT&CK Intelligence Mapper
Correlates passive protocol observations into MITRE ATT&CK technique classifications.
Dynamically computes confidence scores based on heuristic telemetry rather than static constants.
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class MitreDetection:
    technique_id: str
    technique_name: str
    confidence: float
    threat_profile: str
    evidence: Dict[str, Any]

class MitreAttackMapper:
    """
    Correlates passive protocol observations into MITRE ATT&CK technique classifications.
    Assigns threat profiles and dynamically calculated confidence scores (0.0 to 1.0).
    """

    MAPPING_RULES = {
        "port_discovery": {
            "technique_id": "T1046",
            "technique_name": "Network Service Discovery",
            "base_confidence": 0.70,
            "threat_profile": "reconnaissance"
        },
        "web_path_probing": {
            "technique_id": "T1190",
            "technique_name": "Exploit Public-Facing Application",
            "base_confidence": 0.72,
            "threat_profile": "reconnaissance"
        },
        "active_scanning": {
            "technique_id": "T1595",
            "technique_name": "Active Scanning",
            "base_confidence": 0.68,
            "threat_profile": "reconnaissance"
        },
        "ssh_credential_probing": {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "base_confidence": 0.75,
            "threat_profile": "credential_probing"
        },
        "ssh_remote_service": {
            "technique_id": "T1021.004",
            "technique_name": "Remote Services: SSH",
            "base_confidence": 0.74,
            "threat_profile": "credential_probing"
        },
        "dns_anomaly": {
            "technique_id": "T1071.004",
            "technique_name": "Application Layer Protocol: DNS",
            "base_confidence": 0.70,
            "threat_profile": "covert_channel"
        },
        "arp_spoof_candidate": {
            "technique_id": "T1557",
            "technique_name": "Adversary-in-the-Middle",
            "base_confidence": 0.76,
            "threat_profile": "network_manipulation"
        },
        "icmp_payload_anomaly": {
            "technique_id": "T1095",
            "technique_name": "Non-Application Layer Protocol",
            "base_confidence": 0.65,
            "threat_profile": "covert_channel"
        }
    }

    def __init__(self):
        # run_id -> { technique_id -> count }
        self._technique_counts: Dict[str, Dict[str, int]] = {}
        # run_id -> list of float timestamps
        self._event_timestamps: Dict[str, List[float]] = {}

    def calculate_confidence(
        self,
        base_confidence: float,
        technique_id: str,
        observation: Dict[str, Any],
        run_id: str = "default"
    ) -> float:
        """
        Calculates dynamic MITRE confidence based on:
        1. Repetition count in active run (accumulated certainty)
        2. Port scan velocity (time delta between events)
        3. Protocol header anomalies (unusual paths, incomplete handshakes, covert queries)
        """
        now = time.time()
        if run_id not in self._technique_counts:
            self._technique_counts[run_id] = {}
            self._event_timestamps[run_id] = []

        counts = self._technique_counts[run_id]
        current_count = counts.get(technique_id, 0) + 1
        counts[technique_id] = current_count

        timestamps = self._event_timestamps[run_id]
        timestamps.append(now)

        # 1. Repetition Boost: More occurrences = higher certainty (+0.04 per repeat, up to +0.20)
        repetition_boost = min(0.20, (current_count - 1) * 0.04)

        # 2. Velocity Boost: Rapid successive probes (< 1.5s interval) indicate automated tooling (+0.05)
        velocity_boost = 0.0
        if len(timestamps) >= 2:
            delta = timestamps[-1] - timestamps[-2]
            if delta < 1.5:
                velocity_boost = 0.05

        # 3. Protocol Header & Payload Anomaly Boost (+0.03 to +0.08)
        details = observation.get("details", {})
        anomaly_boost = 0.0
        if details.get("incomplete_handshakes", 0) > 1:
            anomaly_boost += 0.04
        if "/admin" in str(details.get("uri", "")) or "login" in str(details.get("uri", "")):
            anomaly_boost += 0.05
        if details.get("potential_covert_channel"):
            anomaly_boost += 0.06
        if details.get("entropy", 0) > 3.5:
            anomaly_boost += 0.04

        dynamic_conf = base_confidence + repetition_boost + velocity_boost + anomaly_boost
        # Bounded between 0.55 and 0.99
        return round(min(0.99, max(0.55, dynamic_conf)), 2)

    def classify_observation(self, observation: Dict[str, Any], run_id: str = "default") -> Optional[MitreDetection]:
        behavior = observation.get("behavior_type")
        rule = self.MAPPING_RULES.get(behavior)
        if not rule:
            return None

        technique_id = rule["technique_id"]
        dynamic_conf = self.calculate_confidence(
            base_confidence=rule["base_confidence"],
            technique_id=technique_id,
            observation=observation,
            run_id=run_id
        )

        evidence = {
            "behavior_type": behavior,
            "protocol": observation.get("protocol"),
            "source_ip": observation.get("source_ip"),
            "destination_ip": observation.get("destination_ip"),
            "details": observation.get("details", {}),
            "repetition_factor": self._technique_counts.get(run_id, {}).get(technique_id, 1)
        }

        return MitreDetection(
            technique_id=technique_id,
            technique_name=rule["technique_name"],
            confidence=dynamic_conf,
            threat_profile=rule["threat_profile"],
            evidence=evidence
        )

    def reset_run(self, run_id: str):
        if run_id in self._technique_counts:
            del self._technique_counts[run_id]
        if run_id in self._event_timestamps:
            del self._event_timestamps[run_id]

mitre_mapper = MitreAttackMapper()
