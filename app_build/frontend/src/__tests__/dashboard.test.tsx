import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';
import * as api from '../services/api';
import { TopologyResponse, Run, AgentAction, Detection, PolicyDecision, HoneypotSession } from '../types';

// Mock API module
vi.mock('../services/api');
// Mock WebSocket Client
vi.mock('../services/websocket', () => {
  return {
    RunWebSocketClient: vi.fn().mockImplementation(() => ({
      connect: vi.fn(),
      disconnect: vi.fn()
    }))
  };
});

const mockTopology: TopologyResponse = {
  segments: [
    {
      name: 'edge',
      cidr: '10.0.10.0/24',
      description: 'Perimeter ingress and gateway routing zone',
      nodes: [
        { id: 'gw', name: 'edge-gateway', ip: '10.0.10.1', role: 'perimeter_router', status: 'isolated' },
        { id: 'adv', name: 'adversary-node', ip: '10.0.10.15', role: 'attacker_ingress', status: 'isolated' }
      ]
    },
    {
      name: 'ssh',
      cidr: '10.0.20.0/24',
      description: 'Isolated high-interaction Cowrie SSH lure subnet',
      nodes: [
        { id: 'cowrie', name: 'cowrie-ssh', ip: '10.0.20.10', role: 'honeypot', status: 'isolated' }
      ]
    },
    {
      name: 'web',
      cidr: '10.0.30.0/24',
      description: 'Vulnerable web application and decoy admin portal',
      nodes: [
        { id: 'web', name: 'web-decoy', ip: '10.0.30.10', role: 'honeypot', status: 'isolated' }
      ]
    },
    {
      name: 'services',
      cidr: '10.0.40.0/24',
      description: 'Internal services and deceptive sinkholes',
      nodes: [
        { id: 'dns', name: 'dns-lure', ip: '10.0.40.10', role: 'honeypot', status: 'isolated' }
      ]
    },
    {
      name: 'monitor',
      cidr: '10.0.50.0/24',
      description: 'Passive telemetry tap and isolation subnet',
      nodes: [
        { id: 'tap', name: 'traffic-tap', ip: '10.0.50.10', role: 'sensor', status: 'isolated' }
      ]
    }
  ],
  active_lures: [],
  highlighted_paths: []
};

const mockInitialRun: Run = {
  id: 'run_test123',
  status: 'pending',
  created_at: new Date().toISOString(),
  started_at: new Date().toISOString(),
  ended_at: null,
  threat_score: 10,
  active_profile: 'RECON',
  next_deception_zone: 'edge',
  metadata_json: {}
};

const mockActions: AgentAction[] = [
  {
    id: 'act_1',
    run_id: 'run_test123',
    timestamp: new Date().toISOString(),
    action_type: 'discover_lab_services',
    target_ip: '10.0.10.1',
    target_port: 80,
    parameters: {},
    status: 'completed',
    latency_ms: 12,
    output: 'open'
  },
  {
    id: 'act_2',
    run_id: 'run_test123',
    timestamp: new Date().toISOString(),
    action_type: 'attempt_ssh_to_lure',
    target_ip: '10.0.20.10',
    target_port: 2222,
    parameters: {},
    status: 'allowed',
    latency_ms: 8,
    output: 'connected'
  },
  {
    id: 'act_3',
    run_id: 'run_test123',
    timestamp: new Date().toISOString(),
    action_type: 'connect_tcp',
    target_ip: '192.168.1.1',
    target_port: 4444,
    parameters: {},
    status: 'denied',
    latency_ms: 2,
    output: 'CIDR out of bounds'
  }
];

const mockDetections: Detection[] = [
  {
    id: 'det_1',
    run_id: 'run_test123',
    timestamp: new Date().toISOString(),
    source_ip: '10.0.10.15',
    technique_id: 'T1046',
    technique_name: 'Network Service Discovery',
    confidence: 0.95,
    evidence: { probe: 'SYN scan' }
  }
];

const mockPolicies: PolicyDecision[] = [
  {
    id: 'pol_1',
    run_id: 'run_test123',
    timestamp: new Date().toISOString(),
    threat_profile: 'reconnaissance',
    confidence: 0.95,
    decision: 'reroute_to_cowrie',
    target_zone: 'ssh-lure',
    evidence: {}
  }
];

const mockSessions: HoneypotSession[] = [
  {
    id: 'ses_1',
    run_id: 'run_test123',
    session_id: 'cowrie-session-001',
    lure_type: 'cowrie_ssh',
    source_ip: '10.0.10.15',
    source_port: 43210,
    started_at: new Date().toISOString(),
    commands_or_requests: [
      {
        username: 'root',
        password: '[REDACTED]',
        command: 'cat /etc/shadow'
      }
    ],
    metadata_json: {
      banner: 'SSH-2.0-OpenSSH_8.2p1',
      lure_ip: '10.0.20.10',
      lure_port: 2222
    }
  }
];

describe('NetMirage Full-Stack Operator Dashboard Wiring', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.fetchTopology).mockResolvedValue(mockTopology);
    vi.mocked(api.fetchRuns).mockResolvedValue([mockInitialRun]);
    vi.mocked(api.fetchRunActions).mockResolvedValue(mockActions);
    vi.mocked(api.fetchRunDetections).mockResolvedValue(mockDetections);
    vi.mocked(api.fetchRunPolicies).mockResolvedValue(mockPolicies);
    vi.mocked(api.fetchRunSessions).mockResolvedValue(mockSessions);
    vi.mocked(api.fetchSession).mockResolvedValue(mockSessions[0]);
  });

  it('enforces strict Ivory palette and zero prose lines across the console', async () => {
    const { container } = render(<App />);

    await waitFor(() => {
      expect(screen.getAllByText('NETMIRAGE').length).toBeGreaterThan(0);
    });

    // Check canvas has Ivory background token
    const rootDiv = container.querySelector('.bg-\\[\\#FAF5E9\\]');
    expect(rootDiv).toBeInTheDocument();

    // Verify zero wordy marketing copy or filler paragraphs exist
    const paragraphs = container.querySelectorAll('p');
    paragraphs.forEach((p) => {
      // Must not contain marketing filler or lorem ipsum
      expect(p.textContent?.toLowerCase()).not.toContain('lorem ipsum');
      expect(p.textContent?.toLowerCase()).not.toContain('welcome to');
      expect(p.textContent?.toLowerCase()).not.toContain('getting started');
    });

    // Check presence of locked architectural telemetry chips
    expect(screen.getAllByText(/ZERO-EGRESS/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/10\.0\.10\.0\/24 - 10\.0\.50\.0\/24/i)).toBeInTheDocument();
  });

  it('fires createRun API when clicking Start Run button', async () => {
    const newRun: Run = {
      ...mockInitialRun,
      id: 'run_new_888',
      status: 'running'
    };
    vi.mocked(api.createRun).mockResolvedValue(newRun);

    render(<App />);

    const startBtn = await screen.findByRole('button', { name: /START RUN/i });
    expect(startBtn).toBeInTheDocument();
    expect(startBtn.className).toContain('bg-[#009B4D]');

    fireEvent.click(startBtn);

    await waitFor(() => {
      expect(api.createRun).toHaveBeenCalledTimes(1);
      expect(screen.getAllByText(/RUNNING/i).length).toBeGreaterThan(0);
    });
  });

  it('fires pauseRun and resumeRun APIs sequentially', async () => {
    const runningRun: Run = { ...mockInitialRun, status: 'running' };
    const pausedRun: Run = { ...mockInitialRun, status: 'paused' };
    const resumedRun: Run = { ...mockInitialRun, status: 'running' };

    vi.mocked(api.fetchRuns).mockResolvedValue([runningRun]);
    vi.mocked(api.pauseRun).mockResolvedValue(pausedRun);
    vi.mocked(api.resumeRun).mockResolvedValue(resumedRun);

    render(<App />);

    const pauseBtn = await screen.findByRole('button', { name: /PAUSE/i });
    expect(pauseBtn.className).toContain('bg-[#FFCC00]');

    fireEvent.click(pauseBtn);

    await waitFor(() => {
      expect(api.pauseRun).toHaveBeenCalledWith('run_test123');
      expect(screen.getAllByText(/PAUSED/i).length).toBeGreaterThan(0);
    });

    const resumeBtn = await screen.findByRole('button', { name: /RESUME/i });
    expect(resumeBtn.className).toContain('bg-[#009B4D]');

    fireEvent.click(resumeBtn);

    await waitFor(() => {
      expect(api.resumeRun).toHaveBeenCalledWith('run_test123');
      expect(screen.getAllByText(/RUNNING/i).length).toBeGreaterThan(0);
    });
  });

  it('fires terminateRun API on Terminate button click', async () => {
    const runningRun: Run = { ...mockInitialRun, status: 'running' };
    const terminatedRun: Run = { ...mockInitialRun, status: 'terminated' };

    vi.mocked(api.fetchRuns).mockResolvedValue([runningRun]);
    vi.mocked(api.terminateRun).mockResolvedValue(terminatedRun);

    render(<App />);

    const termBtn = await screen.findByRole('button', { name: /TERMINATE/i });
    fireEvent.click(termBtn);

    await waitFor(() => {
      expect(api.terminateRun).toHaveBeenCalledWith('run_test123');
      expect(screen.getAllByText(/TERMINATED/i).length).toBeGreaterThan(0);
    });
  });

  it('filters actions, detections, and honeypot sessions when clicking VLAN CIDR or node', async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/ACTION BROKER/i)).toBeInTheDocument();
    });

    // Click on CIDR 10.0.20.0/24 button in topology
    const cidrBtn = screen.getByText('10.0.20.0/24');
    fireEvent.click(cidrBtn);

    // Filter badge appears
    await waitFor(() => {
      expect(screen.getByText(/FILTER: 10\.0\.20\.0\/24/i)).toBeInTheDocument();
    });

    // Clear filter
    const clearFilterBtn = screen.getByTitle('Clear Filter');
    fireEvent.click(clearFilterBtn);

    await waitFor(() => {
      expect(screen.queryByText(/FILTER: 10\.0\.20\.0\/24/i)).not.toBeInTheDocument();
    });
  });

  it('handles action filter tabs (ALL, ALLOWED, DENIED)', async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/ACTION BROKER/i)).toBeInTheDocument();
    });

    // Click DENIED tab
    const deniedTab = screen.getByRole('button', { name: /DENIED/i });
    fireEvent.click(deniedTab);

    // DENIED action should be visible
    expect(screen.getByText('CIDR out of bounds')).toBeInTheDocument();

    // Click ALLOWED tab
    const allowedTab = screen.getByRole('button', { name: /ALLOWED/i });
    fireEvent.click(allowedTab);
    expect(screen.getByText('attempt_ssh_to_lure')).toBeInTheDocument();
  });

  it('displays sanitized [REDACTED] credentials in Honeypot Inspector and switches lure tabs', async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/HONEYPOT SESSIONS/i)).toBeInTheDocument();
    });

    // Verify sanitized credential badge exists
    expect(screen.getAllByText('[REDACTED]').length).toBeGreaterThan(0);
    expect(screen.getByText(/cat \/etc\/shadow/)).toBeInTheDocument();

    // Click SSH:COWRIE tab
    const sshTab = screen.getByRole('button', { name: /SSH:COWRIE/i });
    fireEvent.click(sshTab);
    expect(screen.getAllByText('[REDACTED]').length).toBeGreaterThan(0);

    // Click HTTP:WEB tab (no web sessions in mock)
    const webTab = screen.getByRole('button', { name: /HTTP:WEB/i });
    fireEvent.click(webTab);
    expect(screen.getByText(/0 SESSIONS CAPTURED/i)).toBeInTheDocument();
  });

  it('fetches and displays session details when clicking an individual honeypot session', async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/HONEYPOT SESSIONS/i)).toBeInTheDocument();
    });

    // Click on the session card
    const sessionCard = screen.getByTitle('Click to inspect session');
    fireEvent.click(sessionCard);

    await waitFor(() => {
      expect(api.fetchSession).toHaveBeenCalledWith('cowrie-session-001');
      expect(screen.getByText(/SESSION #cowrie-session-001/i)).toBeInTheDocument();
      expect(screen.getByText(/RAW HANDSHAKE METADATA/i)).toBeInTheDocument();
    });

    // Click Back
    const backBtn = screen.getByRole('button', { name: /BACK/i });
    fireEvent.click(backBtn);

    await waitFor(() => {
      expect(screen.queryByText('RAW HANDSHAKE METADATA:')).not.toBeInTheDocument();
    });
  });
});
