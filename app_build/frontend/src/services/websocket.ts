import { EventEnvelope } from '../types';

export class RunWebSocketClient {
  private ws: WebSocket | null = null;
  private runId: string;
  private onMessage: (event: EventEnvelope) => void;
  private onStatusChange?: (status: 'connected' | 'disconnected' | 'connecting') => void;
  private reconnectTimer: any = null;
  private isDestroyed = false;

  constructor(
    runId: string,
    onMessage: (event: EventEnvelope) => void,
    onStatusChange?: (status: 'connected' | 'disconnected' | 'connecting') => void
  ) {
    this.runId = runId;
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
  }

  public connect() {
    if (this.isDestroyed) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/api/runs/${encodeURIComponent(this.runId)}/events`;

    this.onStatusChange?.('connecting');
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.onStatusChange?.('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const parsed: EventEnvelope = JSON.parse(event.data);
        this.onMessage(parsed);
      } catch (err) {
        console.error('Failed to parse WebSocket event:', err);
      }
    };

    this.ws.onclose = () => {
      this.onStatusChange?.('disconnected');
      if (!this.isDestroyed) {
        this.reconnectTimer = setTimeout(() => this.connect(), 2000);
      }
    };

    this.ws.onerror = (err) => {
      console.warn('WebSocket error encountered:', err);
      this.ws?.close();
    };
  }

  public disconnect() {
    this.isDestroyed = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
