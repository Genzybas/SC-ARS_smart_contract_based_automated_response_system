"use client";

import { useEffect, useState } from "react";
import { connectWebSocket } from "@/lib/socket";

type EventKind = "threat" | "normal";
type EventFilter = "all" | EventKind;
type GatewayStatus = "connecting" | "connected" | "reconnecting";

interface Alert {
  source?: string;
  message?: string;
  timestamp?: string;
  type?: EventKind;
  threat_type?: string;
  source_ip?: string;
  score?: number;
  severity?: number;
  blockchain_tx?: string | null;
}

export default function Home() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<EventFilter>("all");
  const [query, setQuery] = useState("");
  const [gatewayStatus, setGatewayStatus] = useState<GatewayStatus>("connecting");

  useEffect(() => {
    return connectWebSocket((data) => {
      const alert: Alert = {
        source: typeof data.source === "string" ? data.source : undefined,
        message: typeof data.message === "string" ? data.message : undefined,
        timestamp: typeof data.timestamp === "string" ? data.timestamp : undefined,
        type: data.type === "threat" || data.type === "normal" ? data.type : undefined,
        threat_type: typeof data.threat_type === "string" ? data.threat_type : undefined,
        source_ip: typeof data.source_ip === "string" ? data.source_ip : undefined,
        score: typeof data.score === "number" ? data.score : undefined,
        severity: typeof data.severity === "number" ? data.severity : undefined,
        blockchain_tx:
          typeof data.blockchain_tx === "string" || data.blockchain_tx === null
            ? data.blockchain_tx
            : undefined,
      };
      setAlerts((previous) => [alert, ...previous].slice(0, 50));
    }, setGatewayStatus);
  }, []);

  const threatCount = alerts.filter((alert) => alert.type === "threat").length;
  const normalCount = alerts.filter((alert) => alert.type === "normal").length;
  const chainCount = alerts.filter((alert) => Boolean(alert.blockchain_tx)).length;
  const normalizedQuery = query.trim().toLowerCase();
  const visibleAlerts = alerts.filter((alert) => {
    const matchesFilter = filter === "all" || alert.type === filter;
    const matchesQuery = !normalizedQuery || [alert.source, alert.threat_type, alert.source_ip]
      .some((value) => value?.toLowerCase().includes(normalizedQuery));
    return matchesFilter && matchesQuery;
  });

  const statusLabel = {
    connecting: "Connecting",
    connected: "Live",
    reconnecting: "Reconnecting",
  }[gatewayStatus];

  return (
    <main className="console-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" aria-label="SC-ARS overview">
          <span className="brand-mark" aria-hidden="true">S</span>
          <span className="brand-copy">
            <strong>SC-ARS</strong>
            <small>SECURITY RESPONSE</small>
          </span>
        </a>

        <div className="sidebar-section-label">WORKSPACE</div>
        <nav className="primary-nav" aria-label="Primary navigation">
          <a className="nav-item nav-item-active" href="#overview" aria-current="page">
            <span className="nav-indicator" aria-hidden="true" />
            Overview
          </a>
        </nav>

        <div className="sidebar-footer">
          <span className={`status-light status-${gatewayStatus}`} aria-hidden="true" />
          <div>
            <strong>Detection gateway</strong>
            <span>{statusLabel}</span>
          </div>
        </div>
      </aside>

      <section className="workspace" id="overview">
        <header className="topbar">
          <div className="breadcrumb"><span>SC-ARS</span><span aria-hidden="true">/</span><strong>Overview</strong></div>
          <div className={`connection-pill connection-${gatewayStatus}`} role="status" aria-live="polite">
            <span className="status-light" aria-hidden="true" />
            Gateway {statusLabel.toLowerCase()}
          </div>
        </header>

        <div className="dashboard-content">
          <section className="page-heading">
            <div>
              <p className="eyebrow">OPERATIONS CENTER</p>
              <h1>Security overview</h1>
              <p className="page-subtitle">Threat activity and automated response telemetry</p>
            </div>
            <div className="event-window"><span className="live-marker" />LIVE FEED <span className="window-divider" /> LAST 50 EVENTS</div>
          </section>

          <section className="metrics" aria-label="Recent event metrics">
            <article className="metric">
              <span className="metric-label">EVENTS RECEIVED</span>
              <strong className="metric-value">{alerts.length.toString().padStart(2, "0")}</strong>
              <span className="metric-note">In current feed window</span>
            </article>
            <article className="metric metric-threats">
              <span className="metric-label">THREAT EVENTS</span>
              <strong className="metric-value">{threatCount.toString().padStart(2, "0")}</strong>
              <span className="metric-note">Detected in current feed</span>
            </article>
            <article className="metric metric-ledger">
              <span className="metric-label">LEDGER RECORDS</span>
              <strong className="metric-value">{chainCount.toString().padStart(2, "0")}</strong>
              <span className="metric-note">Confirmed transaction hashes</span>
            </article>
            <article className="metric metric-normal">
              <span className="metric-label">NORMAL EVENTS</span>
              <strong className="metric-value">{normalCount.toString().padStart(2, "0")}</strong>
              <span className="metric-note">In current feed window</span>
            </article>
          </section>

          <section className="event-panel" aria-labelledby="event-heading">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">TELEMETRY</p>
                <h2 id="event-heading">Event stream</h2>
              </div>
              <label className="search-field">
                <span className="visually-hidden">Search events</span>
                <input
                  type="search"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Search source or threat"
                />
              </label>
            </div>

            <div className="table-controls">
              <div className="filter-tabs" role="group" aria-label="Filter events">
                {(["all", "threat", "normal"] as const).map((value) => (
                  <button
                    className={filter === value ? "filter-tab filter-tab-active" : "filter-tab"}
                    key={value}
                    onClick={() => setFilter(value)}
                    type="button"
                    aria-pressed={filter === value}
                  >
                    {value === "all" ? "All events" : value === "threat" ? "Threats" : "Normal"}
                  </button>
                ))}
              </div>
              <span className="result-count">{visibleAlerts.length} {visibleAlerts.length === 1 ? "event" : "events"}</span>
            </div>

            <div className="table-scroll">
              <table className="event-table">
                <thead>
                  <tr>
                    <th scope="col">CLASSIFICATION</th>
                    <th scope="col">SOURCE</th>
                    <th scope="col">SOURCE IP</th>
                    <th scope="col">MODEL SCORE</th>
                    <th scope="col">SEVERITY</th>
                    <th scope="col">LEDGER</th>
                    <th scope="col">RECEIVED</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleAlerts.map((alert, index) => {
                    const eventType = alert.type ?? "normal";
                    const severityLabel = alert.severity === 2 ? "High" : alert.severity === 1 ? "Medium" : "Low";
                    const timestamp = alert.timestamp ? new Date(alert.timestamp.replace(" ", "T")) : null;
                    const timeLabel = timestamp && !Number.isNaN(timestamp.getTime())
                      ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "medium" }).format(timestamp)
                      : alert.timestamp ?? "—";
                    return (
                      <tr key={`${alert.timestamp ?? "event"}-${alert.source_ip ?? index}-${index}`}>
                        <td>
                          <div className="classification-cell">
                            <span className={`event-mark event-mark-${eventType}`} aria-hidden="true" />
                            <div>
                              <strong>{alert.threat_type ?? (eventType === "threat" ? "Threat detected" : "Normal traffic")}</strong>
                              <span>{alert.message ?? "Inference event"}</span>
                            </div>
                          </div>
                        </td>
                        <td><span className="source-label">{alert.source ?? "—"}</span></td>
                        <td><code>{alert.source_ip ?? "—"}</code></td>
                        <td className="score-value">{typeof alert.score === "number" ? `${(alert.score * 100).toFixed(1)}%` : "—"}</td>
                        <td><span className={`severity severity-${severityLabel.toLowerCase()}`}>{severityLabel}</span></td>
                        <td>
                          {alert.blockchain_tx ? (
                            <code className="ledger-hash" title={alert.blockchain_tx}>{`${alert.blockchain_tx.slice(0, 8)}…${alert.blockchain_tx.slice(-5)}`}</code>
                          ) : <span className="ledger-empty">Not recorded</span>}
                        </td>
                        <td className="time-cell">{timeLabel}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {visibleAlerts.length === 0 && (
                <div className="empty-state">
                  <span className="empty-state-mark" aria-hidden="true">—</span>
                  <strong>{alerts.length === 0 ? "No events received" : "No matching events"}</strong>
                  <span>{alerts.length === 0 ? "The event stream is ready for gateway telemetry." : "Adjust the search or event filter."}</span>
                </div>
              )}
            </div>

            <footer className="panel-footer">
              <span>{chainCount} ledger {chainCount === 1 ? "record" : "records"} in current feed</span>
              <span className="footer-status"><span className={`status-light status-${gatewayStatus}`} aria-hidden="true" />{statusLabel}</span>
            </footer>
          </section>
          <footer className="page-footer">SC-ARS <span>·</span> SMART CONTRACT-BASED AUTOMATED RESPONSE SYSTEM</footer>
        </div>
      </section>
    </main>
  );
}
