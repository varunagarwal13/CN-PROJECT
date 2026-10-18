export type EventKind = 'detection' | 'action' | 'observation' | 'honeypot' | 'policy' | 'system';

export interface EventEnvelope {
  run_id: string;
  event_id: string;
  timestamp: string;
  kind: EventKind;
  source: string;
  payload: Record<string, any>;
}

export type RunStatus = 'pending' | 'running' | 'paused' | 'terminated' | 'completed';

export interface Run {
  id: string;
  status: RunStatus;
  threat_score: number;
  active_profile: string | null;
  next_deception_zone: string | null;
  created_at: string;
  started_at: string | null;
  ended_at: string | null;
  metadata_json: Record<string, any>;
}

export interface AgentAction {
  id: string;
  run_id: string;
  timestamp: string;
  action_type: string;
  target_ip: string;
  target_port: number;
  parameters: Record<string, any>;
  status: 'allowed' | 'denied' | 'timed_out' | 'completed';
  latency_ms?: number;
  output?: any;
}

export interface Observation {
  id: string;
  run_id: string;
  timestamp: string;
  source: string;
  source_ip?: string;
  destination_ip?: string;
  protocol: string;
  behavior_type: string;
  raw_payload: any;
  details: Record<string, any>;
}

export interface Detection {
  id: string;
  run_id: string;
  timestamp: string;
  source_ip: string;
  technique_id: string;
  technique_name: string;
  confidence: number;
  evidence: Record<string, any>;
}

export interface HoneypotSession {
  id: string;
  run_id: string;
  lure_type: 'cowrie_ssh' | 'web_lure' | 'dns_lure' | 'smtp_lure';
  session_id: string;
  source_ip: string;
  source_port?: number;
  started_at: string;
  ended_at?: string;
  commands_or_requests: any[];
  metadata_json: Record<string, any>;
}

export interface PolicyDecision {
  id: string;
  run_id: string;
  timestamp: string;
  threat_profile: string;
  confidence: number;
  decision: string;
  target_zone: string;
  evidence: Record<string, any>;
}

export interface TopologyNode {
  id: string;
  name: string;
  ip: string;
  role: string;
  status: string;
}

export interface TopologySegment {
  name: string;
  cidr: string;
  description: string;
  nodes: TopologyNode[];
}

export interface ActiveLure {
  name: string;
  ip: string;
  ports: number[];
  vlan: string;
  type: string;
}

export interface HighlightedPath {
  source: string;
  destination: string;
  target_zone: string;
  threat_score: number;
  status: string;
}

export interface TopologyResponse {
  segments: TopologySegment[];
  active_lures: ActiveLure[];
  highlighted_paths: HighlightedPath[];
}
