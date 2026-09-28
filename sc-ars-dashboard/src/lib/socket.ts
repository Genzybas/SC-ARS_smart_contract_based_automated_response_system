// src/lib/socket.ts
let socket: WebSocket;

export const connectWebSocket = (onMessage: (data: any) => void) => {
  socket = new WebSocket("ws://localhost:8000/ws");

  socket.onopen = () => console.log("📡 WebSocket connected");
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  socket.onclose = () => {
    console.warn("WebSocket closed, attempting reconnect...");
    setTimeout(() => connectWebSocket(onMessage), 3000);
  };
};
