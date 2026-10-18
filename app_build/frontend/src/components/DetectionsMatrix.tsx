import React from 'react';
import { Detection, PolicyDecision } from '../types';

interface DetectionsMatrixProps {
  detections: Detection[];
  policyDecisions: PolicyDecision[];
  filterNode?: string;
}

export const DetectionsMatrix: React.FC<DetectionsMatrixProps> = ({
  detections,
  policyDecisions,
  filterNode
}) => {
  const filteredDetections = detections.filter((det) => {
    if (!filterNode) return true;
    if (filterNode.includes('/')) {
      const prefix = filterNode.replace('.0/24', '');
      return det.source_ip.startsWith(prefix);
    }
    return det.source_ip === filterNode;
  });

  const renderConfidenceMeter = (conf: number) => {
    const filled = Math.min(10, Math.max(0, Math.floor(conf * 10)));
    const empty = 10 - filled;
    const meterStr = '█'.repeat(filled) + '░'.repeat(empty);
    const decimal = conf.toFixed(2);

    return (
      <div className="flex items-center gap-1.5 font-mono text-[10px] tabular-nums">
        <span className="text-[#111827] tracking-tighter font-bold bg-[#FAF5E9] px-1 border border-[#111827]">
          {meterStr}
        </span>
        <span className="font-bold text-[#111827]">{decimal}</span>
      </div>
    );
  };

  return (
    <div className="bg-[#FAF5E9] border-b border-[#111827] flex flex-col font-mono select-none h-full">
      {/* Pane Header */}
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#111827] bg-[#FAF5E9]">
        <div className="flex items-center gap-2">
          <span className="font-mono font-black text-xs text-[#111827] tracking-wider">
            03 // MITRE ATT&CK & DECEPTION ROUTER
          </span>
          <span className="text-[10px] bg-[#111827] text-[#FAF5E9] px-1.5 py-0.2 font-bold tabular-nums border border-[#111827]">
            {filteredDetections.length}/{detections.length}
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <span className="text-[9px] text-[#111827]/70 font-bold">COLLECTOR::STATUS:</span>
          <span className="px-1.5 py-0.2 bg-[#009B4D] text-[#FAF5E9] font-black text-[9px] uppercase border border-[#111827]">
            ACTIVE
          </span>
        </div>
      </div>

      {/* Tabular Tape Stream */}
      <div className="overflow-x-auto flex-1 max-h-[220px]">
        {filteredDetections.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-[#111827]/50 text-xs font-bold tracking-wider">
            STATE: SCANNING // 0 DETECTIONS
          </div>
        ) : (
          <table className="w-full text-left text-[10px] font-mono border-collapse">
            <thead>
              <tr className="border-b border-[#111827] bg-[#F4ECD6] text-[#111827] text-[9px] uppercase font-black sticky top-0">
                <th className="py-1 px-2 border-r border-[#111827]">TIME</th>
                <th className="py-1 px-2 border-r border-[#111827]">SRC_IP</th>
                <th className="py-1 px-2 border-r border-[#111827]">TECH_ID</th>
                <th className="py-1 px-2 border-r border-[#111827]">NAME</th>
                <th className="py-1 px-2 border-r border-[#111827]">CONFIDENCE</th>
                <th className="py-1 px-2">DECEPTION_ROUTE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#111827]/20">
              {filteredDetections.map((det, idx) => {
                const policy = policyDecisions[idx] || policyDecisions[policyDecisions.length - 1];

                return (
                  <tr key={det.id || idx} className="hover:bg-[#F4ECD6] transition-none">
                    <td className="py-1 px-2 border-r border-[#111827]/20 text-[#111827]/70 tabular-nums whitespace-nowrap">
                      {new Date(det.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-1 px-2 border-r border-[#111827]/20 text-[#111827] font-bold tabular-nums whitespace-nowrap">
                      {det.source_ip}
                    </td>
                    <td className="py-1 px-2 border-r border-[#111827]/20 whitespace-nowrap">
                      <a
                        href={`https://attack.mitre.org/techniques/${det.technique_id.replace('.', '/')}`}
                        target="_blank"
                        rel="noreferrer"
                        className="px-1.5 py-0.2 bg-[#111827] text-[#FFCC00] font-black text-[9px] hover:bg-black transition-none border border-[#111827] inline-block"
                      >
                        {det.technique_id}
                      </a>
                    </td>
                    <td className="py-1 px-2 border-r border-[#111827]/20 font-bold text-[#111827] uppercase truncate max-w-[160px]">
                      {det.technique_name}
                    </td>
                    <td className="py-1 px-2 border-r border-[#111827]/20 whitespace-nowrap">
                      {renderConfidenceMeter(det.confidence)}
                    </td>
                    <td className="py-1 px-2 whitespace-nowrap font-bold text-[10px]">
                      {policy ? (
                        <span className="font-mono text-[#009B4D] font-black">
                          ➔ {policy.target_zone.toUpperCase()}
                        </span>
                      ) : (
                        <span className="text-[#111827]/40 text-[9px]">EVALUATING</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
