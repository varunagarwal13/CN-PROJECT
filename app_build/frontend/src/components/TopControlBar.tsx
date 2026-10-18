import React, { useState, useEffect } from 'react';
import { Run, RunStatus } from '../types';

interface TopControlBarProps {
  currentRun: Run | null;
  runs: Run[];
  onSelectRun: (runId: string) => void;
  onStartRun: () => void;
  onPauseRun: () => void;
  onResumeRun: () => void;
  onTerminateRun: () => void;
  wsStatus: 'connected' | 'disconnected' | 'connecting';
}

export const TopControlBar: React.FC<TopControlBarProps> = ({
  currentRun,
  runs,
  onSelectRun,
  onStartRun,
  onPauseRun,
  onResumeRun,
  onTerminateRun,
  wsStatus
}) => {
  const [blink, setBlink] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setBlink((b) => !b), 700);
    return () => clearInterval(timer);
  }, []);

  const status = currentRun?.status || 'pending';
  const threatScore = currentRun?.threat_score || 0;
  const activeProfile = currentRun?.active_profile || 'STANDBY';
  const nextZone = currentRun?.next_deception_zone || 'EDGE';

  // Format 10-segment ASCII meter for threat score
  const filledBars = Math.min(10, Math.floor(threatScore / 10));
  const emptyBars = 10 - filledBars;
  const threatMeter = '█'.repeat(filledBars) + '░'.repeat(emptyBars);

  const getStatusBadge = (s: RunStatus | 'pending') => {
    switch (s) {
      case 'running':
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono font-black bg-[#009B4D] text-[#FAF5E9] tracking-widest border border-[#111827]">
            RUNNING {blink ? '●' : '○'}
          </span>
        );
      case 'paused':
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono font-black bg-[#FFCC00] text-[#111827] tracking-widest border border-[#111827]">
            PAUSED
          </span>
        );
      case 'terminated':
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono font-black bg-[#111827] text-[#FFCC00] tracking-widest border border-[#FFCC00]">
            TERMINATED
          </span>
        );
      case 'completed':
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono font-black bg-[#009B4D] text-[#FAF5E9] tracking-widest border border-[#111827]">
            COMPLETED
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 text-[10px] font-mono font-black bg-[#FAF5E9] text-[#111827] tracking-widest border border-[#111827]">
            STANDBY
          </span>
        );
    }
  };

  return (
    <header className="bg-[#FAF5E9] border-b-2 border-[#111827] px-4 py-2 flex flex-wrap items-center justify-between gap-2 z-50 select-none">
      {/* Brand & Hardware Identity Cell */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="bg-[#111827] text-[#FFCC00] px-2 py-0.5 font-mono font-black text-xs tracking-wider border border-[#111827]">
            NM//SYS.01
          </div>
          <div>
            <div className="flex items-center gap-1.5 leading-none">
              <span className="font-mono font-black text-xs text-[#111827] tracking-wider">
                NETMIRAGE
              </span>
              <span className="text-[9px] font-mono font-bold text-[#009B4D]">
                [LIVE {blink ? '█' : ' '}]
              </span>
            </div>
            <div className="flex items-center gap-2 text-[9px] font-mono text-[#111827]/70 mt-0.5">
              <span>WS::{wsStatus.toUpperCase()}</span>
              <span>•</span>
              <span className="font-bold text-[#111827]">ZERO-EGRESS</span>
            </div>
          </div>
        </div>

        <div className="h-5 w-[1px] bg-[#111827] hidden sm:block" />

        {/* Run Selector Cell */}
        <div className="flex items-center gap-1.5">
          {getStatusBadge(status)}
          {runs.length > 0 ? (
            <select
              value={currentRun?.id || ''}
              onChange={(e) => onSelectRun(e.target.value)}
              className="bg-[#FAF5E9] text-[#111827] border border-[#111827] px-2 py-0.5 text-[11px] font-mono font-bold outline-none cursor-pointer hover:bg-[#F4ECD6]"
            >
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.id} [{r.status.toUpperCase()}]
                </option>
              ))}
            </select>
          ) : (
            <span className="font-mono text-[10px] text-[#111827] bg-[#FAF5E9] border border-[#111827] px-2 py-0.5 font-bold">
              {currentRun ? currentRun.id : 'STATE: STANDBY // AWAITING_RUN_INIT'}
            </span>
          )}
        </div>
      </div>

      {/* Industrial Telemetry Cells */}
      <div className="flex items-center gap-2 flex-wrap text-[10px] font-mono">
        {/* Threat Index Cell */}
        <div className="flex items-center gap-1.5 bg-[#FAF5E9] border border-[#111827] px-2 py-1">
          <span className="text-[#111827]/70 font-bold">THREAT_INDEX:</span>
          <span className="font-black text-[#111827] tabular-nums">
            {String(threatScore).padStart(2, '0')}/99
          </span>
          <span className="text-[#FFCC00] tracking-tighter font-bold ml-1">
            [{threatMeter}]
          </span>
        </div>

        {/* Profile Cell */}
        <div className="hidden md:flex items-center gap-1.5 bg-[#FAF5E9] border border-[#111827] px-2 py-1">
          <span className="text-[#111827]/70 font-bold">PROFILE:</span>
          <span className="font-bold text-[#111827] uppercase">{activeProfile}</span>
        </div>

        {/* Next Deception Route Cell */}
        <div className="hidden lg:flex items-center gap-1.5 bg-[#FAF5E9] border border-[#111827] px-2 py-1">
          <span className="text-[#111827]/70 font-bold">NEXT_LURE:</span>
          <span className="px-1.5 py-0.2 bg-[#FFCC00] text-[#111827] font-black border border-[#111827] uppercase text-[9px]">
            {nextZone}
          </span>
        </div>
      </div>

      {/* Industrial Tactile Switch Buttons */}
      <div className="flex items-center gap-2">
        {(!currentRun || status === 'pending' || status === 'completed' || status === 'terminated') ? (
          <button
            onClick={onStartRun}
            className="px-3 py-1 text-xs font-mono font-bold bg-[#009B4D] text-[#FAF5E9] border border-[#111827] shadow-[2px_2px_0px_#111827] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none transition-none cursor-pointer tracking-wider"
          >
            START RUN
          </button>
        ) : (
          <>
            {status === 'running' ? (
              <button
                onClick={onPauseRun}
                className="px-3 py-1 text-xs font-mono font-bold bg-[#FFCC00] text-[#111827] border border-[#111827] shadow-[2px_2px_0px_#111827] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none transition-none cursor-pointer tracking-wider"
              >
                PAUSE
              </button>
            ) : status === 'paused' ? (
              <button
                onClick={onResumeRun}
                className="px-3 py-1 text-xs font-mono font-bold bg-[#009B4D] text-[#FAF5E9] border border-[#111827] shadow-[2px_2px_0px_#111827] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none transition-none cursor-pointer tracking-wider"
              >
                RESUME
              </button>
            ) : null}

            <button
              onClick={onTerminateRun}
              className="px-3 py-1 text-xs font-mono font-bold bg-[#111827] text-[#FFCC00] border-2 border-[#FFCC00] shadow-[2px_2px_0px_#111827] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none transition-none cursor-pointer tracking-wider"
            >
              TERMINATE
            </button>
          </>
        )}
      </div>
    </header>
  );
};
