import React, { useState, useRef, useEffect } from 'react';
import { AgentAction } from '../types';

interface AttackerTerminalProps {
  actions: AgentAction[];
  filterNode?: string;
}

export const AttackerTerminal: React.FC<AttackerTerminalProps> = ({ actions, filterNode }) => {
  const [filterStatus, setFilterStatus] = useState<'ALL' | 'ALLOWED' | 'DENIED'>('ALL');
  const scrollRef = useRef<HTMLDivElement>(null);

  const filteredActions = actions.filter((act) => {
    if (filterStatus === 'ALLOWED' && act.status !== 'allowed' && act.status !== 'completed') return false;
    if (filterStatus === 'DENIED' && act.status !== 'denied') return false;
    if (filterNode) {
      if (filterNode.includes('/')) {
        const prefix = filterNode.replace('.0/24', '');
        if (!act.target_ip.startsWith(prefix)) return false;
      } else {
        if (act.target_ip !== filterNode) return false;
      }
    }
    return true;
  });

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [actions]);

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="px-1.5 py-0.2 text-[9px] font-mono font-black border border-[#009B4D] text-[#009B4D] uppercase">
            COMPLETED
          </span>
        );
      case 'denied':
        return (
          <span className="px-1.5 py-0.2 text-[9px] font-mono font-black bg-[#111827] text-[#FFCC00] border border-[#111827] uppercase">
            DENIED
          </span>
        );
      case 'allowed':
        return (
          <span className="px-1.5 py-0.2 text-[9px] font-mono font-black bg-[#009B4D] text-[#FAF5E9] border border-[#009B4D] uppercase">
            ALLOWED
          </span>
        );
      default:
        return (
          <span className="px-1.5 py-0.2 text-[9px] font-mono font-black bg-[#FAF5E9] text-[#111827] border border-[#111827] uppercase">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="bg-[#FAF5E9] border-r border-[#111827] flex flex-col font-mono h-full select-none">
      {/* Pane Header */}
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#111827] bg-[#FAF5E9]">
        <div className="flex items-center gap-2">
          <span className="font-mono font-black text-xs text-[#111827] tracking-wider">
            02 // ACTION BROKER TAPE
          </span>
          <span className="text-[10px] bg-[#111827] text-[#FAF5E9] px-1.5 py-0.2 font-bold tabular-nums border border-[#111827]">
            {filteredActions.length}/{actions.length}
          </span>
        </div>

        {/* Filter Switch Strip */}
        <div className="flex items-center gap-1 text-xs">
          {(['ALL', 'ALLOWED', 'DENIED'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilterStatus(tab)}
              className={`px-2 py-0.5 text-[10px] font-bold border transition-none cursor-pointer ${
                filterStatus === tab
                  ? 'bg-[#111827] text-[#FAF5E9] border-[#111827]'
                  : 'bg-[#FAF5E9] text-[#111827] hover:bg-[#F4ECD6] border-[#111827]/40'
              }`}
            >
              [{tab}]
            </button>
          ))}
        </div>
      </div>

      {/* Hardware Sub-Strip: Pipeline Stages */}
      <div className="grid grid-cols-3 border-b border-[#111827] text-[9px] font-bold text-center bg-[#F4ECD6]">
        <div className="py-0.5 border-r border-[#111827]">[1] OBSERVE::SWEEP</div>
        <div className="py-0.5 border-r border-[#111827]">[2] PLAN::ALLOWLIST</div>
        <div className="py-0.5">[3] BROKER::PARAMETRIC</div>
      </div>

      {/* Dense Wireshark/htop-Style Tabular Tape */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {filteredActions.length === 0 ? (
          <div className="flex items-center justify-center h-48 text-[#111827]/50 text-xs font-bold tracking-wider">
            STATE: STANDBY // 0 ACTIONS RECORDED
          </div>
        ) : (
          <table className="w-full text-left text-[10px] font-mono border-collapse">
            <thead>
              <tr className="border-b border-[#111827] bg-[#FAF5E9] text-[#111827]/70 text-[9px] uppercase font-bold sticky top-0">
                <th className="py-1 px-2 border-r border-[#111827]/20">TIME</th>
                <th className="py-1 px-2 border-r border-[#111827]/20">ACTION</th>
                <th className="py-1 px-2 border-r border-[#111827]/20">TARGET_IP:PORT</th>
                <th className="py-1 px-2 border-r border-[#111827]/20">STATUS</th>
                <th className="py-1 px-2 border-r border-[#111827]/20">LATENCY</th>
                <th className="py-1 px-2">OUTPUT_FEED</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#111827]/20">
              {filteredActions.map((act) => (
                <tr key={act.id} className="hover:bg-[#F4ECD6] transition-none">
                  <td className="py-1 px-2 border-r border-[#111827]/20 text-[#111827]/70 tabular-nums whitespace-nowrap">
                    {new Date(act.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-1 px-2 border-r border-[#111827]/20 font-black text-[#111827] whitespace-nowrap">
                    {act.action_type}
                  </td>
                  <td className="py-1 px-2 border-r border-[#111827]/20 tabular-nums whitespace-nowrap font-bold">
                    {act.target_ip}:{act.target_port}
                  </td>
                  <td className="py-1 px-2 border-r border-[#111827]/20 whitespace-nowrap">
                    {getStatusTag(act.status)}
                  </td>
                  <td className="py-1 px-2 border-r border-[#111827]/20 tabular-nums font-bold text-[#111827]/80 whitespace-nowrap">
                    {act.latency_ms !== undefined ? `${act.latency_ms}ms` : '-'}
                  </td>
                  <td className="py-1 px-2 text-[#111827] font-mono truncate max-w-[280px]">
                    {act.output ? (
                      <span className="truncate">
                        {typeof act.output === 'object' ? JSON.stringify(act.output) : String(act.output)}
                      </span>
                    ) : (
                      <span className="text-[#111827]/40">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
