import React, { useState, useEffect, useCallback } from 'react';
import {
  Run,
  TopologyResponse,
  AgentAction,
  Detection,
  PolicyDecision,
  HoneypotSession,
  EventEnvelope
} from './types';
import {
  fetchTopology,
  fetchRuns,
  createRun,
  pauseRun,
  resumeRun,
  terminateRun,
  fetchRunActions,
  fetchRunDetections,
  fetchRunPolicies,
  fetchRunSessions
} from './services/api';
import { RunWebSocketClient } from './services/websocket';
import { TopControlBar } from './components/TopControlBar';
import { NetworkTopology } from './components/NetworkTopology';
import { AttackerTerminal } from './components/AttackerTerminal';
import { DetectionsMatrix } from './components/DetectionsMatrix';
import { HoneypotInspector } from './components/HoneypotInspector';

export const App: React.FC = () => {
  const [runs, setRuns] = useState<Run[]>([]);
  const [currentRun, setCurrentRun] = useState<Run | null>(null);
  const [topology, setTopology] = useState<TopologyResponse | null>(null);
  const [actions, setActions] = useState<AgentAction[]>([]);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [policyDecisions, setPolicyDecisions] = useState<PolicyDecision[]>([]);
  const [sessions, setSessions] = useState<HoneypotSession[]>([]);
  const [activeTargetIp, setActiveTargetIp] = useState<string | undefined>();
  const [selectedFilterNode, setSelectedFilterNode] = useState<string | undefined>();
  const [wsStatus, setWsStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');

  // Load initial topology & existing runs
  useEffect(() => {
    fetchTopology().then(setTopology).catch(console.error);
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      const runList = await fetchRuns();
      setRuns(runList);
      if (runList.length > 0 && !currentRun) {
        setCurrentRun(runList[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // When currentRun changes, fetch existing records & connect WebSocket
  useEffect(() => {
    if (!currentRun) return;

    fetchRunActions(currentRun.id).then(setActions).catch(console.error);
    fetchRunDetections(currentRun.id).then(setDetections).catch(console.error);
    fetchRunPolicies(currentRun.id).then(setPolicyDecisions).catch(console.error);
    fetchRunSessions(currentRun.id).then(setSessions).catch(() => setSessions([]));

    // Connect WebSocket
    const wsClient = new RunWebSocketClient(
      currentRun.id,
      (envelope: EventEnvelope) => {
        handleIncomingEvent(envelope);
      },
      (status) => {
        setWsStatus(status);
      }
    );

    wsClient.connect();

    return () => {
      wsClient.disconnect();
    };
  }, [currentRun?.id]);

  const handleIncomingEvent = useCallback((envelope: EventEnvelope) => {
    const { kind, payload } = envelope;

    if (kind === 'action') {
      const newAction: AgentAction = {
        id: payload.action_id || `act_${Date.now()}`,
        run_id: envelope.run_id,
        timestamp: envelope.timestamp,
        action_type: payload.action_type,
        target_ip: payload.target_ip,
        target_port: payload.target_port,
        parameters: payload.parameters || {},
        status: payload.status,
        latency_ms: payload.latency_ms,
        output: payload.output
      };
      setActions((prev) => {
        const idx = prev.findIndex((a) => a.id === newAction.id);
        if (idx >= 0) {
          const updated = [...prev];
          updated[idx] = newAction;
          return updated;
        }
        return [...prev, newAction];
      });
      if (payload.target_ip) {
        setActiveTargetIp(payload.target_ip);
      }
    } else if (kind === 'detection') {
      const newDet: Detection = {
        id: payload.detection_id || `det_${Date.now()}`,
        run_id: envelope.run_id,
        timestamp: envelope.timestamp,
        source_ip: payload.source_ip,
        technique_id: payload.technique_id,
        technique_name: payload.technique_name,
        confidence: payload.confidence,
        evidence: payload.evidence || {}
      };
      setDetections((prev) => [...prev, newDet]);

      setCurrentRun((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          threat_score: payload.threat_score ?? prev.threat_score,
          active_profile: payload.active_profile ?? prev.active_profile
        };
      });
    } else if (kind === 'policy') {
      const newPol: PolicyDecision = {
        id: payload.policy_id || `pol_${Date.now()}`,
        run_id: envelope.run_id,
        timestamp: envelope.timestamp,
        threat_profile: payload.threat_profile,
        confidence: payload.confidence,
        decision: payload.decision,
        target_zone: payload.target_zone,
        evidence: payload.evidence || {}
      };
      setPolicyDecisions((prev) => [...prev, newPol]);

      setCurrentRun((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          next_deception_zone: payload.target_zone ?? prev.next_deception_zone
        };
      });

      fetchTopology(envelope.run_id).then(setTopology).catch(console.error);
    } else if (kind === 'honeypot') {
      const newSes: HoneypotSession = {
        id: payload.session_id,
        run_id: envelope.run_id,
        lure_type: payload.lure_type,
        session_id: payload.session_id,
        source_ip: payload.source_ip,
        source_port: payload.source_port,
        started_at: envelope.timestamp,
        commands_or_requests: payload.commands_or_requests || [],
        metadata_json: payload.metadata || {}
      };
      setSessions((prev) => {
        const idx = prev.findIndex((s) => s.session_id === newSes.session_id);
        if (idx >= 0) {
          const updated = [...prev];
          updated[idx] = newSes;
          return updated;
        }
        return [...prev, newSes];
      });
    } else if (kind === 'system') {
      setCurrentRun((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          status: payload.status || prev.status,
          threat_score: payload.threat_score !== undefined ? payload.threat_score : prev.threat_score,
          active_profile: payload.active_profile || prev.active_profile,
          next_deception_zone: payload.next_deception_zone || prev.next_deception_zone
        };
      });
    }
  }, []);

  const handleSelectRun = (runId: string) => {
    const found = runs.find((r) => r.id === runId);
    if (found) {
      setCurrentRun(found);
    }
  };

  const handleStartRun = async () => {
    try {
      setActions([]);
      setDetections([]);
      setPolicyDecisions([]);
      setSessions([]);
      setActiveTargetIp(undefined);
      setSelectedFilterNode(undefined);
      const newRun = await createRun();
      setCurrentRun(newRun);
      setRuns((prev) => [newRun, ...prev.filter((r) => r.id !== newRun.id)]);
    } catch (err) {
      console.error('Error starting run:', err);
    }
  };

  const handlePauseRun = async () => {
    if (!currentRun) return;
    try {
      const updated = await pauseRun(currentRun.id);
      setCurrentRun(updated);
      setRuns((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
    } catch (err) {
      console.error('Error pausing run:', err);
    }
  };

  const handleResumeRun = async () => {
    if (!currentRun) return;
    try {
      const updated = await resumeRun(currentRun.id);
      setCurrentRun(updated);
      setRuns((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
    } catch (err) {
      console.error('Error resuming run:', err);
    }
  };

  const handleTerminateRun = async () => {
    if (!currentRun) return;
    try {
      const updated = await terminateRun(currentRun.id);
      setCurrentRun(updated);
      setRuns((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
    } catch (err) {
      console.error('Error terminating run:', err);
    }
  };

  return (
    <div className="h-screen w-screen bg-[#FAF5E9] text-[#111827] flex flex-col overflow-hidden font-mono selection:bg-[#FFCC00] selection:text-[#111827]">
      {/* Hardware Command Strip */}
      <TopControlBar
        currentRun={currentRun}
        runs={runs}
        onSelectRun={handleSelectRun}
        onStartRun={handleStartRun}
        onPauseRun={handlePauseRun}
        onResumeRun={handleResumeRun}
        onTerminateRun={handleTerminateRun}
        wsStatus={wsStatus}
      />

      {/* Main Split-Pane Modular Grid */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Row 1: Technical Schematic Topology (Panel [01]) */}
        <section className="shrink-0">
          <NetworkTopology
            topology={topology}
            currentRun={currentRun}
            activeTargetIp={activeTargetIp}
            selectedFilterNode={selectedFilterNode}
            onSelectFilterNode={setSelectedFilterNode}
          />
        </section>

        {/* Row 2: Center/Bottom Split Grid: Action Broker Tape (Left) vs Matrix & Honeypot (Right) */}
        <section className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden border-b border-[#111827]">
          {/* Panel [02] — AI Action Broker Tabular Tape (Left 6 Columns) */}
          <div className="lg:col-span-6 h-full overflow-hidden">
            <AttackerTerminal
              actions={actions}
              filterNode={selectedFilterNode}
            />
          </div>

          {/* Right 6 Columns: Panel [03] Matrix (Top) + Panel [04] Honeypot Inspector (Bottom) */}
          <div className="lg:col-span-6 h-full flex flex-col overflow-hidden">
            {/* Panel [03] — MITRE ATT&CK Matrix */}
            <div className="h-1/2 overflow-hidden">
              <DetectionsMatrix
                detections={detections}
                policyDecisions={policyDecisions}
                filterNode={selectedFilterNode}
              />
            </div>

            {/* Panel [04] — Honeypot Session Inspector */}
            <div className="h-1/2 overflow-hidden">
              <HoneypotInspector
                sessions={sessions}
                filterNode={selectedFilterNode}
              />
            </div>
          </div>
        </section>
      </main>

      {/* Industrial Hardware Status Ticker Footer */}
      <footer className="h-6 shrink-0 bg-[#FAF5E9] px-4 flex items-center justify-between text-[9px] font-mono font-bold text-[#111827] select-none">
        <div className="flex items-center gap-3">
          <span className="bg-[#111827] text-[#FAF5E9] px-1.5 py-0.2 font-black tracking-wider">
            NETMIRAGE HW-01
          </span>
          <span>SANDBOX::10.0.10.0/24 - 10.0.50.0/24</span>
          <span>•</span>
          <span className="text-[#009B4D] font-black">ZERO-EGRESS GUARANTEED</span>
        </div>
        <div className="flex items-center gap-3">
          <span>POLICY::FAIL_CLOSED</span>
          <span>•</span>
          <span>ACTIONS::7_ALLOWLISTED</span>
          <span>•</span>
          <span className="bg-[#FFCC00] text-[#111827] px-1.5 py-0.2 border border-[#111827] font-black">
            DECEPTION_ROUTER::ONLINE
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;
