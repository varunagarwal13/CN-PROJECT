import React from 'react';
import { TopologyResponse, Run } from '../types';

interface NetworkTopologyProps {
  topology: TopologyResponse | null;
  currentRun: Run | null;
  activeTargetIp?: string;
  selectedFilterNode?: string;
  onSelectFilterNode: (ipOrCidr: string | undefined) => void;
}

export const NetworkTopology: React.FC<NetworkTopologyProps> = ({
  topology,
  currentRun,
  activeTargetIp,
  selectedFilterNode,
  onSelectFilterNode
}) => {
  const currentZone = currentRun?.next_deception_zone || 'edge';

  return (
    <div className="bg-[#FAF5E9] border-b border-[#111827] flex flex-col font-mono select-none">
      {/* Schematic Header Bar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#FAF5E9] border-b border-[#111827]">
        <div className="flex items-center gap-2">
          <span className="font-mono font-black text-xs text-[#111827] tracking-wider">
            01 // VLAN TOPOLOGY [ZERO-EGRESS]
          </span>
          <span className="text-[9px] font-bold px-1.5 py-0.2 bg-[#009B4D] text-[#FAF5E9] border border-[#111827]">
            EGRESS::BLOCKED
          </span>
          {selectedFilterNode && (
            <div className="flex items-center gap-1.5 bg-[#FFCC00] text-[#111827] border border-[#111827] px-2 py-0.2 text-[10px] font-black">
              <span>FILTER: {selectedFilterNode}</span>
              <button
                onClick={() => onSelectFilterNode(undefined)}
                className="hover:text-black font-black cursor-pointer"
                title="Clear Filter"
              >
                [✕]
              </button>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-[10px] text-[#111827]/70 font-bold">DECEPTION_ROUTE:</span>
          <span className="px-2 py-0.2 bg-[#FFCC00] text-[#111827] border border-[#111827] font-black uppercase text-[10px]">
            ➔ {currentZone}
          </span>
        </div>
      </div>

      {/* Schematic Canvas with Dot-Matrix Pattern */}
      <div className="p-3 bg-dot-matrix relative overflow-hidden">
        {/* Orthogonal SVG Routing Bus Lines in Background */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none opacity-40"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Main Bus Line */}
          <line x1="10%" y1="18" x2="90%" y2="18" stroke="#111827" strokeWidth="1.5" strokeDasharray="3 3" />
          {/* Drops to each segment */}
          <line x1="10%" y1="18" x2="10%" y2="40" stroke="#111827" strokeWidth="1.5" />
          <line x1="30%" y1="18" x2="30%" y2="40" stroke="#111827" strokeWidth="1.5" />
          <line x1="50%" y1="18" x2="50%" y2="40" stroke="#111827" strokeWidth="1.5" />
          <line x1="70%" y1="18" x2="70%" y2="40" stroke="#111827" strokeWidth="1.5" />
          <line x1="90%" y1="18" x2="90%" y2="40" stroke="#111827" strokeWidth="1.5" />
        </svg>

        {/* 5 VLAN Architectural Modules */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative z-10">
          {topology?.segments.map((seg, idx) => {
            const isTargetSegment =
              (seg.name === 'edge' && currentZone === 'edge') ||
              (seg.name === 'ssh' && currentZone === 'ssh-lure') ||
              (seg.name === 'web' && currentZone === 'web-lure') ||
              (seg.name === 'services' && (currentZone === 'services-lure' || currentZone === 'dns-lure')) ||
              (seg.name === 'monitor' && currentZone === 'quarantine');

            const isSegmentFiltered = selectedFilterNode === seg.cidr;

            return (
              <div
                key={seg.name}
                className={`border-2 p-2.5 flex flex-col justify-between transition-none bg-[#FAF5E9] ${
                  isTargetSegment
                    ? 'border-[#FFCC00] shadow-[2px_2px_0px_#111827] bg-[#FFF8E1]'
                    : isSegmentFiltered
                    ? 'border-[#009B4D] shadow-[2px_2px_0px_#111827] bg-[#F0FDF4]'
                    : 'border-[#111827]'
                }`}
              >
                <div>
                  {/* Segment Header */}
                  <div className="flex justify-between items-center pb-1 mb-2 border-b border-[#111827]">
                    <span className="font-mono font-black text-[11px] text-[#111827] uppercase tracking-wide">
                      [{String(idx + 1).padStart(2, '0')}] {seg.name}
                    </span>
                    <button
                      onClick={() => onSelectFilterNode(selectedFilterNode === seg.cidr ? undefined : seg.cidr)}
                      className="font-mono text-[9px] font-bold text-[#111827] bg-[#FAF5E9] hover:bg-[#FFCC00] border border-[#111827] px-1 py-0.2 cursor-pointer"
                      title="Toggle Subnet Filter"
                    >
                      {seg.cidr}
                    </button>
                  </div>

                  {/* Nodes List */}
                  <div className="space-y-1">
                    {seg.nodes.map((node) => {
                      const isNodeTargeted = activeTargetIp === node.ip;
                      const isNodeFiltered = selectedFilterNode === node.ip;

                      return (
                        <button
                          key={node.id}
                          onClick={() => onSelectFilterNode(selectedFilterNode === node.ip ? undefined : node.ip)}
                          className={`w-full text-left p-1 text-xs flex items-center justify-between gap-1 border cursor-pointer transition-none ${
                            isNodeTargeted
                              ? 'bg-[#FFCC00] border-[#111827] font-black text-[#111827]'
                              : isNodeFiltered
                              ? 'bg-[#009B4D] text-[#FAF5E9] border-[#111827] font-bold'
                              : 'bg-[#FAF5E9] hover:bg-[#F4ECD6] text-[#111827] border-[#111827]/30'
                          }`}
                        >
                          <div className="overflow-hidden leading-tight">
                            <div className="font-bold text-[10px] truncate">{node.name}</div>
                            <div className="font-mono text-[9px] opacity-80 tabular-nums">{node.ip}</div>
                          </div>
                          <span
                            className={`text-[8px] font-mono px-1 py-0.2 uppercase font-black shrink-0 border border-[#111827] ${
                              node.role === 'honeypot'
                                ? 'bg-[#009B4D] text-[#FAF5E9]'
                                : node.role === 'attacker_ingress'
                                ? 'bg-[#111827] text-[#FFCC00]'
                                : 'bg-[#FAF5E9] text-[#111827]'
                            }`}
                          >
                            {node.role === 'honeypot' ? 'LURE' : node.role === 'attacker_ingress' ? 'ADV' : 'NODE'}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="mt-2 pt-1 border-t border-[#111827]/20 flex justify-between items-center text-[9px] font-mono text-[#111827]/70 font-bold">
                  <span>SEC::STATUS</span>
                  <span className={isTargetSegment ? 'text-[#111827] font-black' : 'text-[#009B4D]'}>
                    {isTargetSegment ? 'ENGAGED' : 'ISOLATED'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Dense Hardware Telemetry Strip Below Topology */}
        <div className="mt-2.5 px-3 py-1 bg-[#FAF5E9] border border-[#111827] flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono">
          <div className="flex items-center gap-1.5 text-[#111827]">
            <span className="text-[#111827]/70 font-bold">VECTOR:</span>
            <span className="px-1.5 py-0.2 bg-[#111827] text-[#FAF5E9] font-bold tabular-nums">10.0.10.15</span>
            <span className="text-[#111827] font-black">──►</span>
            <span className="px-1.5 py-0.2 bg-[#FFCC00] text-[#111827] border border-[#111827] font-black tabular-nums">
              {activeTargetIp || '10.0.10.42'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[#111827]/70 font-bold">ISOLATION_ROUTING:</span>
            <span className="px-1.5 py-0.2 bg-[#009B4D] text-[#FAF5E9] font-bold uppercase border border-[#111827]">
              ACTIVE ({currentZone})
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
