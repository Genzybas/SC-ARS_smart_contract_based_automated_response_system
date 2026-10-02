// src/lib/socket.ts
type ConnectionStatus = "connecting" | "connected" | "reconnecting";

export const connectWebSocket = (
  onMessage: (data: Record<string, unknown>) => void,
  onStatus?: (status: ConnectionStatus) => void,
) => {
  let socket: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
  let isClosed = false;

  const connect = () => {
    if (isClosed) return;

    onStatus?.("connecting");
    const url = process.env.NEXT_PUBLIC_GATEWAY_WS_URL ??
      `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.hostname}:8000/ws`;
    socket = new WebSocket(url);

    socket.onopen = () => onStatus?.("connected");

    socket.onmessage = (event) => {
      try {
        const data: unknown = typeof event.data === "string" ? JSON.parse(event.data) : event.data;
        if (data && typeof data === "object" && !Array.isArray(data)) {
          onMessage(data as Record<string, unknown>);
        }
      } catch {
        onMessage({ message: String(event.data), timestamp: new Date().toISOString() });
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
      if (!isClosed) {
        onStatus?.("reconnecting");
        reconnectTimer = setTimeout(connect, 3000);
      }
    };
  };

  connect();

  return () => {
    isClosed = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    socket?.close();
  };
};
