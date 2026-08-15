"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_URL = "http://localhost:8000";

type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

type Incident = {
  id: number;
  threat_type: string;
  severity: Severity;
  confidence: number;
  source_ip: string;
  target_service: string;
  status: string;
  detected_at: string;
};

type Summary = {
  total_threats: number;
  critical_threats: number;
  high_threats: number;
  active_incidents: number;
  system_status: string;
};

const severityStyle: Record<Severity, string> = {
  CRITICAL: "bg-red-500/20 text-red-300 border-red-400/30",
  HIGH: "bg-orange-500/20 text-orange-300 border-orange-400/30",
  MEDIUM: "bg-yellow-500/20 text-yellow-300 border-yellow-400/30",
  LOW: "bg-green-500/20 text-green-300 border-green-400/30",
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [summaryResponse, incidentResponse] = await Promise.all([
          fetch(`${API_URL}/api/v1/dashboard/summary`),
          fetch(`${API_URL}/api/v1/incidents`),
        ]);

        if (!summaryResponse.ok || !incidentResponse.ok) {
          throw new Error("Could not load dashboard data.");
        }

        setSummary(await summaryResponse.json());
        setIncidents(await incidentResponse.json());
      } catch {
        setError("CyberGuard AI API is offline. Make sure FastAPI is running on port 8000.");
      }
    }

    loadDashboard();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <header className="mb-10 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <p className="text-sm font-semibold tracking-[0.25em] text-cyan-400">
              CYBERGUARD AI
            </p>
            <h1 className="mt-2 text-4xl font-bold">Security Dashboard</h1>
            <p className="mt-2 text-slate-400">
              Monitor detected incidents and security risk signals.
            </p>
          </div>

          <a
            href="/"
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800"
          >
            Back to Home
          </a>
        </header>

        {error ? (
          <div className="rounded-xl border border-red-400/30 bg-red-500/10 p-5 text-red-200">
            {error}
          </div>
        ) : (
          <>
            <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {[
                ["Total Threats", summary?.total_threats ?? "…", "text-cyan-300"],
                ["Critical Threats", summary?.critical_threats ?? "…", "text-red-300"],
                ["High Threats", summary?.high_threats ?? "…", "text-orange-300"],
                ["Active Incidents", summary?.active_incidents ?? "…", "text-yellow-300"],
              ].map(([label, value, color]) => (
                <article
                  key={label}
                  className="rounded-xl border border-slate-800 bg-slate-900/70 p-5"
                >
                  <p className="text-sm text-slate-400">{label}</p>
                  <p className={`mt-2 text-4xl font-bold ${color}`}>{value}</p>
                </article>
              ))}
            </section>

            <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900/70">
              <div className="flex items-center justify-between border-b border-slate-800 p-5">
                <div>
                  <h2 className="text-xl font-semibold">Recent Threats</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Live data from the CyberGuard AI backend.
                  </p>
                </div>
                <span className="rounded-full bg-green-500/15 px-3 py-1 text-xs font-semibold text-green-300">
                  {summary?.system_status ?? "LOADING"}
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <thead className="bg-slate-900 text-slate-400">
                    <tr>
                      <th className="p-4">Threat</th>
                      <th className="p-4">Severity</th>
                      <th className="p-4">Confidence</th>
                      <th className="p-4">Source IP</th>
                      <th className="p-4">Target</th>
                      <th className="p-4">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {incidents.map((incident) => (
                      <tr key={incident.id} className="border-t border-slate-800">
                        <td className="p-4 font-medium">
  <Link
    href={`/dashboard/incidents/${incident.id}`}
    className="text-cyan-300 hover:text-cyan-100 hover:underline"
  >
    {incident.threat_type}
  </Link>
</td>
                        <td className="p-4">
                          <span
                            className={`rounded-full border px-2.5 py-1 text-xs font-bold ${severityStyle[incident.severity]}`}
                          >
                            {incident.severity}
                          </span>
                        </td>
                        <td className="p-4">{Math.round(incident.confidence * 100)}%</td>
                        <td className="p-4 font-mono text-slate-300">{incident.source_ip}</td>
                        <td className="p-4">{incident.target_service}</td>
                        <td className="p-4 text-cyan-300">{incident.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </div>
    </main>
  );
}