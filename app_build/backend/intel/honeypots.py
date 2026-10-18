import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app_build.backend import models

SENSITIVE_KEYS = {"password", "passwd", "secret", "token", "key", "credential", "auth_token", "api_key"}

def redact_credentials(obj: Any) -> Any:
    """
    Recursively redacts passwords, credentials, tokens, and secrets with [REDACTED].
    """
    if isinstance(obj, dict):
        sanitized = {}
        for k, v in obj.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = redact_credentials(v)
        return sanitized
    elif isinstance(obj, list):
        return [redact_credentials(item) for item in obj]
    elif isinstance(obj, str):
        # 1. Key-value assignment (password=..., secret_key=..., token: ...)
        cleaned = re.sub(
            r'([a-zA-Z0-9_\-]*(?:password|passwd|secret|token|api_key|key))\s*[:=]\s*[^\s,;]+',
            r'\1=[REDACTED]',
            obj,
            flags=re.IGNORECASE
        )
        # 2. Command-line basic auth flags (e.g., -u user:password)
        cleaned = re.sub(
            r'(-u\s+[a-zA-Z0-9_\-\.]+):[^\s]+',
            r'\1:[REDACTED]',
            cleaned
        )
        # 3. HTTP Basic Authorization header / prefix
        cleaned = re.sub(
            r'(Authorization:\s*Basic\s+)[^\s]+',
            r'\1[REDACTED]',
            cleaned,
            flags=re.IGNORECASE
        )
        return cleaned
    return obj

class HoneypotNormalizer:
    """
    Normalizes interaction data from Cowrie SSH, Web, DNS, and SMTP lures into
    sanitized HoneypotSession records and universal observations.
    """

    @staticmethod
    def normalize_cowrie_event(
        run_id: str,
        session_id: str,
        source_ip: str,
        source_port: Optional[int],
        username: str,
        password: Optional[str],
        command: Optional[str],
        raw_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        command_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "username": username,
            "password": "[REDACTED]" if password else None,
            "command": redact_credentials(command) if command else None
        }

        metadata = redact_credentials(raw_metadata or {})
        metadata.update({
            "banner": "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6",
            "lure_ip": "10.0.20.10",
            "lure_port": 22
        })

        return {
            "session_id": session_id,
            "run_id": run_id,
            "lure_type": "cowrie_ssh",
            "source_ip": source_ip,
            "source_port": source_port or 45892,
            "commands_or_requests": [command_entry],
            "metadata": metadata
        }

    @staticmethod
    def normalize_web_event(
        run_id: str,
        session_id: str,
        source_ip: str,
        method: str,
        path: str,
        user_agent: str,
        body: Optional[Any] = None
    ) -> Dict[str, Any]:
        request_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "path": path,
            "user_agent": user_agent,
            "body": redact_credentials(body)
        }
        return {
            "session_id": session_id,
            "run_id": run_id,
            "lure_type": "web_lure",
            "source_ip": source_ip,
            "source_port": 50124,
            "commands_or_requests": [request_entry],
            "metadata": {
                "server": "Apache/2.4.52 (Ubuntu)",
                "lure_ip": "10.0.30.10",
                "lure_port": 80
            }
        }

    @staticmethod
    def normalize_dns_event(
        run_id: str,
        session_id: str,
        source_ip: str,
        query_domain: str,
        record_type: str
    ) -> Dict[str, Any]:
        query_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": query_domain,
            "record_type": record_type
        }
        return {
            "session_id": session_id,
            "run_id": run_id,
            "lure_type": "dns_lure",
            "source_ip": source_ip,
            "source_port": 53535,
            "commands_or_requests": [query_entry],
            "metadata": {
                "server": "BIND 9.18.1",
                "lure_ip": "10.0.40.10",
                "lure_port": 53
            }
        }

    @staticmethod
    def normalize_smtp_event(
        run_id: str,
        session_id: str,
        source_ip: str,
        command: str,
        recipient: Optional[str]
    ) -> Dict[str, Any]:
        smtp_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": command,
            "recipient": recipient
        }
        return {
            "session_id": session_id,
            "run_id": run_id,
            "lure_type": "smtp_lure",
            "source_ip": source_ip,
            "source_port": 49152,
            "commands_or_requests": [smtp_entry],
            "metadata": {
                "banner": "220 mail.corp.netmirage.internal ESMTP",
                "lure_ip": "10.0.40.20",
                "lure_port": 25
            }
        }

honeypot_normalizer = HoneypotNormalizer()
