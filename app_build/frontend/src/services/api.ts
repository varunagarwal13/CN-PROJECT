import { Run, TopologyResponse, HoneypotSession, AgentAction, Detection, PolicyDecision } from '../types';

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}

export async function fetchTopology(runId?: string): Promise<TopologyResponse> {
  const url = runId ? `${API_BASE}/topology?run_id=${encodeURIComponent(runId)}` : `${API_BASE}/topology`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch topology');
  return res.json();
}

export async function fetchRuns(): Promise<Run[]> {
  const res = await fetch(`${API_BASE}/runs`);
  if (!res.ok) throw new Error('Failed to fetch runs');
  return res.json();
}

export async function createRun(scenario: string = 'full_adversary_emulation'): Promise<Run> {
  const res = await fetch(`${API_BASE}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario, metadata: { triggered_by: 'operator_ui' } })
  });
  if (!res.ok) throw new Error('Failed to create run');
  return res.json();
}

export async function pauseRun(runId: string): Promise<Run> {
  const res = await fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/pause`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to pause run');
  return res.json();
}

export async function resumeRun(runId: string): Promise<Run> {
  const res = await fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/resume`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to resume run');
  return res.json();
}

export async function terminateRun(runId: string): Promise<Run> {
  const res = await fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/terminate`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to terminate run');
  return res.json();
}

export async function fetchSession(sessionId: string): Promise<HoneypotSession | HoneypotSession[]> {
  const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(sessionId)}`);
  if (!res.ok) throw new Error('Failed to fetch session');
  return res.json();
}

export async function fetchRunActions(runId: string): Promise<AgentAction[]> {
  const res = await fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/actions`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchRunDetections(runId: string): Promise<Detection[]> {
  const res = await fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/detections`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchRunPolicies(runId: string): Promise<PolicyDecision[]> {
  const res = await fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/policies`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchRunSessions(runId: string): Promise<HoneypotSession[]> {
  const res = await fetch(`${API_BASE}/runs/${encodeURIComponent(runId)}/sessions`);
  if (!res.ok) return [];
  return res.json();
}

