import uuid
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
    Assigns threat profiles and confidence scores (0.0 to 1.0).
    """

    MAPPING_RULES = {
        "port_discovery": {
            "technique_id": "T1046",
            "technique_name": "Network Service Discovery",
            "confidence": 0.90,
            "threat_profile": "reconnaissance"
        },
        "web_path_probing": {
            "technique_id": "T1190",
            "technique_name": "Exploit Public-Facing Application",
            "confidence": 0.85,
            "threat_profile": "reconnaissance"
        },
        "active_scanning": {
            "technique_id": "T1595",
            "technique_name": "Active Scanning",
            "confidence": 0.80,
            "threat_profile": "reconnaissance"
        },
        "ssh_credential_probing": {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "confidence": 0.95,
            "threat_profile": "credential_probing"
        },
        "ssh_remote_service": {
            "technique_id": "T1021.004",
            "technique_name": "Remote Services: SSH",
            "confidence": 0.92,
            "threat_profile": "credential_probing"
        },
        "dns_anomaly": {
            "technique_id": "T1071.004",
            "technique_name": "Application Layer Protocol: DNS",
            "confidence": 0.88,
            "threat_profile": "covert_channel"
        },
        "arp_spoof_candidate": {
            "technique_id": "T1557",
            "technique_name": "Adversary-in-the-Middle",
            "confidence": 0.92,
            "threat_profile": "network_manipulation"
        },
        "icmp_payload_anomaly": {
            "technique_id": "T1095",
            "technique_name": "Non-Application Layer Protocol",
            "confidence": 0.80,
            "threat_profile": "covert_channel"
        }
    }

    def classify_observation(self, observation: Dict[str, Any]) -> Optional[MitreDetection]:
        behavior = observation.get("behavior_type")
        rule = self.MAPPING_RULES.get(behavior)
        if not rule:
            return None

        evidence = {
            "behavior_type": behavior,
            "protocol": observation.get("protocol"),
            "source_ip": observation.get("source_ip"),
            "destination_ip": observation.get("destination_ip"),
            "details": observation.get("details", {})
        }

        return MitreDetection(
            technique_id=rule["technique_id"],
            technique_name=rule["technique_name"],
            confidence=rule["confidence"],
            threat_profile=rule["threat_profile"],
            evidence=evidence
        )

mitre_mapper = MitreAttackMapper()
