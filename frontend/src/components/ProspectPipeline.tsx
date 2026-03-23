import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  fetchIcpModels,
  discoverProspects,
  selectProspects,
  enrichProspects,
  listProspects,
} from "../lib/api";
import type { Prospect, PipelineStep, ProspectResult } from "../types/api.types";
import Card from "./Card";
import StepIndicator from "./StepIndicator";
import DiscoveryTable from "./DiscoveryTable";
import ProspectTable from "./ProspectTable";

interface Props {
  initialModelId?: string | null;
}

export default function ProspectPipeline({ initialModelId }: Props) {
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [step, setStep] = useState<PipelineStep>("discover");
  const [discovered, setDiscovered] = useState<Prospect[]>([]);
  const [enrichedResults, setEnrichedResults] = useState<ProspectResult | null>(null);
  const [statusMsg, setStatusMsg] = useState<{ type: string; text: string } | null>(null);

  const { data: models } = useQuery({
    queryKey: ["icp-models"],
    queryFn: fetchIcpModels,
  });

  const activeModel = models?.find((m) => m.is_active);
  const effectiveModel =
    selectedModel ||
    initialModelId ||
    activeModel?.id ||
    models?.[0]?.id ||
    "";

  useEffect(() => {
    if (initialModelId) setSelectedModel(initialModelId);
  }, [initialModelId]);

  // ── Discover ──────────────────────────────────────────
  const discoverMutation = useMutation({
    mutationFn: async () => discoverProspects(effectiveModel),
    onSuccess: (data) => {
      setDiscovered(data.items);
      setStatusMsg({ type: "success", text: `Discovered ${data.total} prospects from LinkedIn` });
      setStep("select");
    },
    onError: (err: Error) => {
      setStatusMsg({ type: "error", text: `Discovery failed: ${err.message}` });
    },
  });

  // ── Select + Enrich ───────────────────────────────────
  const enrichMutation = useMutation({
    mutationFn: async (ids: string[]) => {
      // First mark as selected
      await selectProspects(effectiveModel, ids);
      // Then enrich
      return enrichProspects(effectiveModel, ids);
    },
    onMutate: () => {
      setStep("enrich");
      setStatusMsg({ type: "info", text: "Enriching prospects via Apollo…" });
    },
    onSuccess: (data) => {
      setEnrichedResults(data);
      setStatusMsg({ type: "success", text: `Enriched ${data.items.length} prospects with Apollo data` });
      setStep("results");
    },
    onError: (err: Error) => {
      setStatusMsg({ type: "error", text: `Enrichment failed: ${err.message}` });
      setStep("select");
    },
  });

  // ── Load existing enriched results ────────────────────
  const loadMutation = useMutation({
    mutationFn: async () => listProspects(effectiveModel, 1, 100, "enriched"),
    onSuccess: (data) => {
      if (data.total === 0) {
        setStatusMsg({ type: "muted", text: "No enriched prospects yet. Run the pipeline first." });
      } else {
        setEnrichedResults(data);
        setStatusMsg({ type: "success", text: `${data.total} enriched prospects` });
        setStep("results");
      }
    },
    onError: (err: Error) => {
      setStatusMsg({ type: "error", text: `Load failed: ${err.message}` });
    },
  });

  function handleReset() {
    setStep("discover");
    setDiscovered([]);
    setEnrichedResults(null);
    setStatusMsg(null);
  }

  const statusColors: Record<string, string> = {
    success: "text-success font-semibold",
    error: "text-coral",
    muted: "text-muted",
    info: "text-amber-dark",
  };

  const isPending = discoverMutation.isPending || enrichMutation.isPending || loadMutation.isPending;

  return (
    <Card>
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-bold text-gray-900">Prospect Pipeline</h2>
        {step !== "discover" && (
          <button
            onClick={handleReset}
            className="text-[0.75rem] text-muted hover:text-navy transition-colors"
          >
            Start Over
          </button>
        )}
      </div>

      <StepIndicator current={step} />

      {/* ── Step 1: Discover controls ── */}
      {step === "discover" && (
        <div className="animate-fade-in">
          <div className="flex items-end gap-3 mb-4 flex-wrap">
            <div className="flex flex-col gap-1 flex-1 min-w-[200px]">
              <label className="text-[0.7rem] font-semibold uppercase tracking-wide text-muted">
                ICP Model
              </label>
              <select
                value={effectiveModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                disabled={!models || models.length === 0}
                className="py-2 px-3 border border-gray-200 rounded-sm text-sm bg-white text-gray-900 cursor-pointer"
              >
                {!models ? (
                  <option>Loading models…</option>
                ) : models.length === 0 ? (
                  <option>No ICP models — create one first</option>
                ) : (
                  models.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                      {m.is_active ? " (active)" : ""}
                    </option>
                  ))
                )}
              </select>
            </div>

            <button
              onClick={() => discoverMutation.mutate()}
              disabled={!effectiveModel || discoverMutation.isPending}
              className="py-2 px-5 rounded-sm text-[0.82rem] font-semibold bg-amber text-navy whitespace-nowrap transition-opacity hover:opacity-85 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {discoverMutation.isPending ? "Discovering…" : "Discover Prospects"}
            </button>

            <button
              onClick={() => loadMutation.mutate()}
              disabled={!effectiveModel || loadMutation.isPending}
              className="py-2 px-5 rounded-sm text-[0.82rem] font-semibold bg-navy text-white whitespace-nowrap transition-opacity hover:opacity-85 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadMutation.isPending ? "Loading…" : "View Enriched"}
            </button>
          </div>
        </div>
      )}

      {/* ── Loading indicator ── */}
      {isPending && (
        <div className="text-amber-dark text-[0.82rem] mb-3">
          {discoverMutation.isPending && "Claude is searching the web for matching prospects…"}
          {enrichMutation.isPending && "Enriching prospects via Apollo API…"}
          {loadMutation.isPending && "Loading enriched prospects…"}
          <div className="mt-2 h-1.5 w-full rounded shimmer-loading" />
        </div>
      )}

      {/* ── Status message ── */}
      {statusMsg && !isPending && (
        <div className={`text-[0.82rem] mb-3 ${statusColors[statusMsg.type] ?? ""}`}>
          {statusMsg.text}
        </div>
      )}

      {/* ── Step 2: Select from discovered ── */}
      {step === "select" && (
        <DiscoveryTable
          prospects={discovered}
          onEnrich={(ids) => enrichMutation.mutate(ids)}
          isEnriching={enrichMutation.isPending}
        />
      )}

      {/* ── Step 3: Enriching (loading state handled above) ── */}
      {step === "enrich" && !enrichMutation.isPending && (
        <p className="text-muted text-center py-8">Waiting for enrichment…</p>
      )}

      {/* ── Step 4: Enriched results ── */}
      {step === "results" && enrichedResults && (
        <div className="animate-fade-in">
          <ProspectTable prospects={enrichedResults.items} />
        </div>
      )}
    </Card>
  );
}
