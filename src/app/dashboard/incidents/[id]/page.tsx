"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

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

type AnalystResponse = {
  analyst: string;
  threat_summary: string;
  attack_type: string;
  severity_reason: string;
  confidence: number;
  recommended_actions: string[];
  automation_note: string;
};

type IncidentStatus = "OPEN" | "INVESTIGATING" | "RESOLVED";

const API_URL = "http://localhost:8000";

function severityStyle(severity: string) {
  if (severity === "CRITICAL") {
    return "border-rose-500/40 bg-rose-500/10 text-rose-300";
  }

  if (severity === "HIGH") {
    return "border-orange-500/40 bg-orange-500/10 text-orange-300";
  }

  if (severity === "MEDIUM") {
    return "border-yellow-500/40 bg-yellow-500/10 text-yellow-300";
  }

  return "border-emerald-500/40 bg-emerald-500/10 text-emerald-300";
}

export default function IncidentDetailPage() {
  const params = useParams<{ id: string }>();
  const incidentId = Array.isArray(params.id) ? params.id[0] : params.id;

  const [incident, setIncident] = useState<Incident | null>(null);
  const [analysis, setAnalysis] = useState<AnalystResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  useEffect(() => {
    async function loadIncident() {
      try {
        setLoading(true);
        setError("");

        const [incidentResponse, analysisResponse] = await Promise.all([
          fetch(`${API_URL}/api/v1/incidents/${incidentId}`),
          fetch(`${API_URL}/api/v1/incidents/${incidentId}/analysis`),
        ]);

        if (!incidentResponse.ok || !analysisResponse.ok) {
          throw new Error("Unable to load incident details.");
        }

        const incidentData = await incidentResponse.json();
        const analysisData = await analysisResponse.json();

        setIncident(incidentData);
        setAnalysis(analysisData);
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to connect to the CyberGuard AI API."
        );
      } finally {
        setLoading(false);
      }
    }

    if (incidentId) {
      loadIncident();
    }
  }, [incidentId]);

  async function updateIncidentStatus(status: IncidentStatus) {
    try {
      setIsUpdatingStatus(true);
      setStatusMessage("");

      const response = await fetch(
        `${API_URL}/api/v1/incidents/${incidentId}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status }),
        }
      );

      const updatedIncident = await response.json();

      if (!response.ok) {
        throw new Error(
          updatedIncident.detail || "Unable to update incident status."
        );
      }

      setIncident(updatedIncident);
      setStatusMessage(`Incident marked as ${updatedIncident.status}.`);
    } catch (updateError) {
      setStatusMessage(
        updateError instanceof Error
          ? updateError.message
          : "Unable to update incident status."
      );
    } finally {
      setIsUpdatingStatus(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-[#020617] p-10 text-white">
        Loading incident analysis...
      </main>
    );
  }

  if (error || !incident || !analysis) {
    return (
      <main className="min-h-screen bg-[#020617] p-10 text-white">
        <div className="mx-auto max-w-3xl rounded-2xl border border-red-500/40 bg-red-500/10 p-6">
          <h1 className="text-2xl font-bold">Incident unavailable</h1>
          <p className="mt-2 text-red-200">{error}</p>

          <Link
            href="/dashboard"
            className="mt-5 inline-block rounded-lg border border-slate-600 px-4 py-2"
          >
            Back to Dashboard
          </Link>
        </div>
      </main>
    );
  }

  const targetService =
    incident.target_service === "-"
      ? "Unspecified network service"
      : incident.target_service;

  return (
    <main className="min-h-screen bg-[#020617] px-6 py-10 text-white md:px-12">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-bold tracking-[0.28em] text-cyan-400">
              INCIDENT #{incident.id}
            </p>
            <h1 className="mt-3 text-4xl font-bold">
              {incident.threat_type}
            </h1>
            <p className="mt-3 text-slate-400">
              Detected {new Date(incident.detected_at).toLocaleString()}
            </p>
          </div>

          <Link
            href="/dashboard"
            className="rounded-xl border border-slate-700 px-5 py-3 font-semibold transition hover:border-cyan-400 hover:text-cyan-300"
          >
            Back to Dashboard
          </Link>
        </header>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 md:p-8">
          <div className="grid gap-5 md:grid-cols-2">
            <InfoCard label="Severity">
              <span
                className={`inline-flex rounded-full border px-3 py-1 text-sm font-bold ${severityStyle(
                  incident.severity
                )}`}
              >
                {incident.severity}
              </span>
            </InfoCard>

            <InfoCard label="Confidence">
              <p className="text-2xl font-bold text-cyan-300">
                {(incident.confidence * 100).toFixed(1)}%
              </p>
            </InfoCard>

            <InfoCard label="Status">
              <p className="text-xl font-bold text-cyan-300">
                {incident.status}
              </p>
            </InfoCard>

            <InfoCard label="Target Service">
              <p className="text-xl font-bold">{targetService}</p>
            </InfoCard>

            <InfoCard label="Source IP">
              <p className="font-mono text-xl font-bold">
                {incident.source_ip}
              </p>
            </InfoCard>

            <InfoCard label="Detection Model">
              <p className="text-xl font-bold">Random Forest / Rules</p>
            </InfoCard>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 md:p-8">
          <h2 className="text-2xl font-bold">Detection Evidence</h2>

          <div className="mt-5 space-y-3">
            {incident.evidence.map((item, index) => (
              <div
                key={`${item}-${index}`}
                className="rounded-xl border border-slate-700 bg-slate-950 p-4 text-slate-200"
              >
                {item}
              </div>
            ))}
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-6 md:p-8">
          <p className="text-sm font-bold tracking-[0.25em] text-emerald-400">
            RESPONSE MANAGEMENT
          </p>

          <h2 className="mt-3 text-2xl font-bold">Incident Lifecycle</h2>

          <p className="mt-3 text-slate-300">
            Update the investigation state after your security team reviews the
            incident. These actions update only the CyberGuard AI incident
            record.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => updateIncidentStatus("INVESTIGATING")}
              disabled={
                isUpdatingStatus || incident.status === "RESOLVED"
              }
              className="rounded-xl bg-amber-400 px-5 py-3 font-bold text-slate-950 transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Mark as Investigating
            </button>

            <button
              onClick={() => updateIncidentStatus("RESOLVED")}
              disabled={
                isUpdatingStatus || incident.status === "RESOLVED"
              }
              className="rounded-xl bg-emerald-400 px-5 py-3 font-bold text-slate-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Mark as Resolved
            </button>
          </div>

          {statusMessage && (
            <p className="mt-5 rounded-xl border border-slate-700 bg-slate-950 p-4 text-slate-200">
              {statusMessage}
            </p>
          )}
        </section>

        <section className="mt-8 rounded-2xl border border-cyan-500/40 bg-cyan-500/5 p-6 md:p-8">
          <p className="text-sm font-bold tracking-[0.25em] text-cyan-400">
            {analysis.analyst.toUpperCase()}
          </p>

          <h2 className="mt-3 text-3xl font-bold">Threat Assessment</h2>

          <p className="mt-4 text-lg leading-8 text-slate-200">
            {analysis.threat_summary}
          </p>

          <div className="mt-6 rounded-xl border border-slate-700 bg-slate-950/70 p-5">
            <p className="text-sm font-semibold text-slate-400">
              Severity reasoning
            </p>
            <p className="mt-2 text-slate-100">{analysis.severity_reason}</p>
          </div>

          <h3 className="mt-8 text-xl font-bold">
            Recommended Defensive Actions
          </h3>

          <ol className="mt-4 space-y-3">
            {analysis.recommended_actions.map((action, index) => (
              <li
                key={action}
                className="flex gap-4 rounded-xl border border-slate-700 bg-slate-950/70 p-4"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-cyan-400 font-bold text-slate-950">
                  {index + 1}
                </span>
                <span className="pt-0.5 text-slate-100">{action}</span>
              </li>
            ))}
          </ol>

          <p className="mt-6 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
            {analysis.automation_note}
          </p>
        </section>
      </div>
    </main>
  );
}

function InfoCard({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950 p-5">
      <p className="text-sm font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>
      <div className="mt-3">{children}</div>
    </div>
  );
}