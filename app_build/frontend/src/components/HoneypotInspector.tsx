import React, { useState } from 'react';
import { HoneypotSession } from '../types';
import { fetchSession } from '../services/api';

interface HoneypotInspectorProps {
  sessions: HoneypotSession[];
  filterNode?: string;
  onSelectSession?: (sessionId: string) => void;
}

export const HoneypotInspector: React.FC<HoneypotInspectorProps> = ({
  sessions,
  filterNode,
  onSelectSession
}) => {
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [activeSessionDetail, setActiveSessionDetail] = useState<HoneypotSession | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  const filteredSessions = sessions.filter((s) => {
    if (selectedType === 'SSH:COWRIE' && s.lure_type !== 'cowrie_ssh') return false;
    if (selectedType === 'HTTP:WEB' && s.lure_type !== 'web_lure') return false;
    if (selectedType === 'DNS' && s.lure_type !== 'dns_lure') return false;
    if (selectedType === 'SMTP' && s.lure_type !== 'smtp_lure') return false;

    // backward compatibility for tests clicking 'SSH' or 'WEB'
    if (selectedType === 'SSH' && s.lure_type !== 'cowrie_ssh') return false;
    if (selectedType === 'WEB' && s.lure_type !== 'web_lure') return false;

    if (filterNode) {
      if (filterNode.includes('/')) {
        const prefix = filterNode.replace('.0/24', '');
        return s.source_ip.startsWith(prefix);
      }
      return s.source_ip === filterNode;
    }
    return true;
  });

  const handleSessionClick = async (sessionId: string) => {
    onSelectSession?.(sessionId);
    setLoadingDetail(true);
    try {
      const res = await fetchSession(sessionId);
      const sessionObj = Array.isArray(res) ? res[0] : res;
      setActiveSessionDetail(sessionObj);
    } catch (err) {
      console.error('Failed to load session details:', err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const getLureCode = (type: string) => {
    switch (type) {
      case 'cowrie_ssh':
        return 'SSH::COWRIE';
      case 'web_lure':
        return 'HTTP::WEB';
      case 'dns_lure':
        return 'DNS::TAP';
      case 'smtp_lure':
        return 'SMTP::SINK';
      default:
        return type.toUpperCase();
    }
  };

  return (
    <div className="bg-[#FAF5E9] flex flex-col font-mono select-none h-full">
      {/* Pane Header */}
      <div className="flex flex-wrap items-center justify-between px-3 py-1.5 border-b border-[#111827] bg-[#FAF5E9] gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono font-black text-xs text-[#111827] tracking-wider">
            04 // HONEYPOT SESSIONS & REDACTION
          </span>
          <span className="text-[9px] font-bold px-1.5 py-0.2 bg-[#009B4D] text-[#FAF5E9] border border-[#111827]">
            ZERO_LEAK
          </span>
          {loadingDetail && (
            <span className="text-[9px] font-bold px-1.5 py-0.2 bg-[#FFCC00] text-[#111827] border border-[#111827]">
              FETCHING...
            </span>
          )}
        </div>

        {/* Hard-Bordered Tab Strip */}
        <div className="flex items-center gap-1 text-xs">
          {['ALL', 'SSH:COWRIE', 'HTTP:WEB', 'DNS', 'SMTP'].map((tab) => (
            <button
              key={tab}
              onClick={() => {
                setSelectedType(tab);
                setActiveSessionDetail(null);
              }}
              className={`px-1.5 py-0.5 text-[9px] font-black border transition-none cursor-pointer ${
                selectedType === tab
                  ? 'bg-[#111827] text-[#FAF5E9] border-[#111827]'
                  : 'bg-[#FAF5E9] text-[#111827] hover:bg-[#F4ECD6] border-[#111827]/40'
              }`}
            >
              [{tab}]
            </button>
          ))}
        </div>
      </div>

      {/* Main Container: Inline Split-View Payload Inspector or Tabular Feed */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sessions Tabular Feed (Left/Main Pane) */}
        <div className={`overflow-y-auto ${activeSessionDetail ? 'w-1/2 border-r border-[#111827]' : 'w-full'} max-h-[260px]`}>
          {filteredSessions.length === 0 ? (
            <div className="flex items-center justify-center h-32 text-[#111827]/50 text-xs font-bold tracking-wider">
              STATE: STANDBY // 0 SESSIONS CAPTURED
            </div>
          ) : (
            <table className="w-full text-left text-[10px] font-mono border-collapse">
              <thead>
                <tr className="border-b border-[#111827] bg-[#F4ECD6] text-[#111827] text-[9px] uppercase font-black sticky top-0">
                  <th className="py-1 px-2 border-r border-[#111827]">TIME</th>
                  <th className="py-1 px-2 border-r border-[#111827]">LURE</th>
                  <th className="py-1 px-2 border-r border-[#111827]">SOURCE_IP:PORT</th>
                  <th className="py-1 px-2">PAYLOAD_SUMMARY</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#111827]/20">
                {filteredSessions.map((ses) => {
                  const isSelected = activeSessionDetail?.session_id === ses.session_id;

                  return (
                    <tr
                      key={ses.id || ses.session_id}
                      onClick={() => handleSessionClick(ses.session_id || ses.id)}
                      className={`cursor-pointer transition-none ${
                        isSelected ? 'bg-[#FFCC00] text-[#111827] font-bold' : 'hover:bg-[#F4ECD6]'
                      }`}
                      title="Click to inspect session"
                    >
                      <td className="py-1 px-2 border-r border-[#111827]/20 text-[#111827]/70 tabular-nums whitespace-nowrap">
                        {new Date(ses.started_at).toLocaleTimeString()}
                      </td>
                      <td className="py-1 px-2 border-r border-[#111827]/20 font-black whitespace-nowrap">
                        <span className="px-1 py-0.2 bg-[#111827] text-[#FAF5E9] text-[8px] border border-[#111827]">
                          {getLureCode(ses.lure_type)}
                        </span>
                      </td>
                      <td className="py-1 px-2 border-r border-[#111827]/20 font-bold tabular-nums whitespace-nowrap">
                        {ses.source_ip}:{ses.source_port}
                      </td>
                      <td className="py-1 px-2 font-mono truncate max-w-[220px]">
                        {ses.commands_or_requests.map((entry, idx) => (
                          <span key={idx} className="mr-2">
                            {entry.username && (
                              <span>
                                USER:{entry.username} PASS:<span className="bg-[#111827] text-[#FFCC00] px-1 font-black">[REDACTED]</span>{' '}
                              </span>
                            )}
                            {entry.command && (
                              <code className="text-[#009B4D] font-black">$ {entry.command}</code>
                            )}
                            {entry.path && <span>HTTP {entry.method}:{entry.path}</span>}
                            {entry.domain && <span>DNS:{entry.domain}</span>}
                          </span>
                        ))}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Inline Split-View Raw Payload Inspector (Right Pane) */}
        {activeSessionDetail && (
          <div className="w-1/2 p-2.5 bg-[#F4ECD6] overflow-y-auto max-h-[260px] flex flex-col space-y-2 text-[10px]">
            {/* Inspector Subheader */}
            <div className="flex items-center justify-between pb-1 border-b border-[#111827]">
              <div className="flex items-center gap-1.5 font-black">
                <span>SESSION #{activeSessionDetail.session_id}</span>
                <span className="bg-[#FFCC00] text-[#111827] px-1 border border-[#111827] text-[9px] uppercase">
                  {getLureCode(activeSessionDetail.lure_type)}
                </span>
              </div>
              <button
                onClick={() => setActiveSessionDetail(null)}
                className="bg-[#111827] text-[#FAF5E9] px-1.5 py-0.2 text-[9px] font-bold hover:bg-black cursor-pointer"
              >
                BACK [✕]
              </button>
            </div>

            {/* Hardware Coordinates Strip */}
            <div className="grid grid-cols-2 gap-1 text-[9px]">
              <div className="bg-[#FAF5E9] p-1 border border-[#111827]">
                <span className="text-[#111827]/60">SRC:</span> {activeSessionDetail.source_ip}:{activeSessionDetail.source_port}
              </div>
              <div className="bg-[#FAF5E9] p-1 border border-[#111827]">
                <span className="text-[#111827]/60">TIME:</span> {new Date(activeSessionDetail.started_at).toLocaleTimeString()}
              </div>
            </div>

            {/* Captured Command Entries */}
            <div className="space-y-1">
              <div className="text-[9px] font-black uppercase text-[#111827]">CAPTURED TELEMETRY ENTRIES:</div>
              {activeSessionDetail.commands_or_requests.map((entry, idx) => (
                <div key={idx} className="bg-[#FAF5E9] p-1.5 border border-[#111827] space-y-0.5">
                  {entry.username && (
                    <div className="flex items-center gap-1">
                      <span className="text-[#111827]/60 font-bold">USER:</span>
                      <span className="font-black text-[#111827]">{entry.username}</span>
                      <span className="mx-1">•</span>
                      <span className="text-[#111827]/60 font-bold">AUTH:</span>
                      <span className="px-1 bg-[#111827] text-[#FFCC00] font-black text-[9px]">
                        [REDACTED]
                      </span>
                    </div>
                  )}
                  {entry.command && (
                    <div className="flex items-center gap-1">
                      <span className="text-[#111827]/60 font-bold">CMD:</span>
                      <code className="text-[#009B4D] font-black">$ {entry.command}</code>
                    </div>
                  )}
                  {entry.path && (
                    <div>
                      <span className="text-[#111827]/60 font-bold">URI:</span> HTTP {entry.method} {entry.path}
                    </div>
                  )}
                  {entry.domain && (
                    <div>
                      <span className="text-[#111827]/60 font-bold">QUERY:</span> {entry.domain} ({entry.record_type})
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Raw Handshake Metadata */}
            {activeSessionDetail.metadata_json && Object.keys(activeSessionDetail.metadata_json).length > 0 && (
              <div className="bg-[#FAF5E9] p-1.5 border border-[#111827]">
                <div className="text-[9px] font-black uppercase text-[#111827]">RAW HANDSHAKE METADATA:</div>
                <pre className="text-[8px] whitespace-pre-wrap font-mono mt-0.5 leading-tight">
                  {JSON.stringify(activeSessionDetail.metadata_json, null, 1)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
