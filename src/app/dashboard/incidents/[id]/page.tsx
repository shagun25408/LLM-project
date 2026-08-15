"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

const API_URL = "http://localhost:8000";

type Incident = {
  id: number;
  threat_type: string;
  severity: string;
  confidence: number;
  source_ip: string;
  target_service: string;
  status: string;
  detected_at: string;
  evidence: string[];
};

export default function IncidentDetailsPage() {
  const params = useParams();
  const incidentId = params.id;
  const [incident, setIncident] = useState<Incident | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadIncident() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/incidents/${incidentId}`,
        );

        if (!response.ok) throw new Error("Incident not found");
        setIncident(await response.json());
      } catch {
        setError("Could not load this incident. Check that the FastAPI server is running.");
      }
    }

    loadIncident();
  }, [incidentId]);

  if (error) {
    return <main className="min-h-screen bg-slate-950 p-10 text-red-300">{error}</main>;
  }

  if (!incident) {
    return <main className="min-h-screen bg-slate-950 p-10 text-slate-300">Loading incident…</main>;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <Link href="/dashboard" className="text-sm text-cyan-300 hover:underline">
          ← Back to Dashboard
        </Link>

        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900/70 p-6">
          <p className="text-sm font-semibold tracking-[0.2em] text-cyan-400">
            INCIDENT #{incident.id}
          </p>
          <h1 className="mt-2 text-4xl font-bold">{incident.threat_type}</h1>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Info label="Severity" value={incident.severity} />
            <Info label="Confidence" value={`${Math.round(incident.confidence * 100)}%`} />
            <Info label="Status" value={incident.status} />
            <Info label="Target Service" value={incident.target_service} />
          </div>
        </div>

        <section className="mt-6 rounded-xl border border-slate-800 bg-slate-900/70 p-6">
          <h2 className="text-xl font-semibold">Detection Evidence</h2>
          <ul className="mt-4 space-y-3 text-slate-300">
            {incident.evidence.map((item) => (
              <li key={item} className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-6 rounded-xl border border-cyan-400/20 bg-cyan-400/5 p-6">
          <h2 className="text-xl font-semibold text-cyan-200">AI Analyst</h2>
          <p className="mt-2 text-slate-300">
            LLM explanation and recommended response will appear here after the ML and AI-analysis stages are added.
          </p>
        </section>
      </div>
    </main>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs uppercase tracking-wider text-slate-400">{label}</p>
      <p className="mt-2 font-semibold text-cyan-100">{value}</p>
    </div>
  );
}