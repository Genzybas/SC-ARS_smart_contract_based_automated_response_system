"use client";

import { useEffect, useState } from "react";
import { connectWebSocket } from "@/lib/socket";

interface Alert {
  message: string;
  timestamp: string;
  type: string;
}

export default function Home() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    connectWebSocket((data: Alert) => {
      setAlerts((prev) => [data, ...prev]);
    });
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">🚨 SC-ARS Threat Monitor</h1>
      <div className="space-y-2">
        {alerts.map((alert, i) => (
          <div key={i} className="p-4 border border-red-500 rounded bg-red-50">
            <p className="font-semibold">⚠️ {alert.message}</p>
            <p className="text-sm text-gray-600">{alert.timestamp}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
