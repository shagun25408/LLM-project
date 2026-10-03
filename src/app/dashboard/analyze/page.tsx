"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

type AnalysisResponse = {
  filename: string;
  rows_analyzed: number;
  attacks_detected: number;
  normal_flows: number;
  incidents_created: number;
};

export default function AnalyzeTrafficPage() {
  const [file, setFile] = useState<File | null>(null);
  const [sourceIp, setSourceIp] = useState("203.0.113.200");
  const [targetService, setTargetService] = useState("Network Gateway");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!file) {
      setError("Please select a CSV file first.");
      return;
    }

    setIsAnalyzing(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_ip", sourceIp);
    formData.append("target_service", targetService);

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/ml/predict/csv",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Traffic analysis failed.");
      }

      setResult(data);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to the CyberGuard AI API."
      );
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#020617] px-6 py-10 text-white md:px-12">
      <div className="mx-auto max-w-5xl">
        <header className="mb-10 flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="mb-3 text-sm font-bold tracking-[0.28em] text-cyan-400">
              CYBERGUARD AI
            </p>
            <h1 className="text-4xl font-bold tracking-tight">
              Analyze Network Traffic
            </h1>
            <p className="mt-3 max-w-2xl text-lg text-slate-400">
              Upload a UNSW-NB15-compatible CSV file and let the Random Forest
              model identify suspicious network flows.
            </p>
          </div>

          <Link
            href="/dashboard"
            className="rounded-xl border border-slate-700 px-5 py-3 font-semibold text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300"
          >
            Back to Dashboard
          </Link>
        </header>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl md:p-8">
          <div className="mb-8">
            <h2 className="text-2xl font-bold">CSV Threat Detection</h2>
            <p className="mt-2 text-slate-400">
              The file is analyzed locally by your CyberGuard AI backend. Attack
              predictions are saved as dashboard incidents.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="csv-file"
                className="mb-2 block font-semibold text-slate-200"
              >
                Network Traffic CSV
              </label>

              <input
                id="csv-file"
                type="file"
                accept=".csv,text/csv"
                onChange={(event) =>
                  setFile(event.target.files?.[0] ?? null)
                }
                className="block w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-cyan-500 file:px-4 file:py-2 file:font-semibold file:text-slate-950 hover:file:bg-cyan-400"
              />

              <p className="mt-2 text-sm text-slate-500">
                Recommended: UNSW_NB15_testing-set.csv
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <label
                  htmlFor="source-ip"
                  className="mb-2 block font-semibold text-slate-200"
                >
                  Source IP label
                </label>

                <input
                  id="source-ip"
                  value={sourceIp}
                  onChange={(event) => setSourceIp(event.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
                />
              </div>

              <div>
                <label
                  htmlFor="target-service"
                  className="mb-2 block font-semibold text-slate-200"
                >
                  Target service label
                </label>

                <input
                  id="target-service"
                  value={targetService}
                  onChange={(event) => setTargetService(event.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
                />
              </div>
            </div>

            {error && (
              <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-300">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isAnalyzing}
              className="w-full rounded-xl bg-cyan-400 px-5 py-4 text-lg font-bold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isAnalyzing
                ? "Analyzing Network Traffic..."
                : "Run ML Threat Analysis"}
            </button>
          </form>
        </section>

        {result && (
          <section className="mt-8 rounded-2xl border border-cyan-500/30 bg-cyan-500/5 p-6 md:p-8">
            <p className="text-sm font-bold tracking-[0.2em] text-cyan-400">
              ANALYSIS COMPLETE
            </p>

            <h2 className="mt-2 text-2xl font-bold">{result.filename}</h2>

            <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <ResultCard
                label="Flows analyzed"
                value={result.rows_analyzed}
                color="text-cyan-300"
              />
              <ResultCard
                label="Attacks detected"
                value={result.attacks_detected}
                color="text-rose-300"
              />
              <ResultCard
                label="Normal flows"
                value={result.normal_flows}
                color="text-emerald-300"
              />
              <ResultCard
                label="Incidents created"
                value={result.incidents_created}
                color="text-amber-300"
              />
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

function ResultCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${color}`}>{value}</p>
    </div>
  );
}