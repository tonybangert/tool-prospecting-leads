import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchIcpModels, activateIcpModel } from "../lib/api";
import type { ConversationResponse } from "../types/api.types";
import Card from "./Card";
import IcpModelDetail from "./IcpModelDetail";
import IcpConversation from "./IcpConversation";

interface Props {
  onSearchProspects: (modelId: string) => void;
}

export default function IcpModelList({ onSearchProspects }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [lastResult, setLastResult] = useState<ConversationResponse | null>(null);

  const queryClient = useQueryClient();

  const { data: models, isLoading, error } = useQuery({
    queryKey: ["icp-models"],
    queryFn: fetchIcpModels,
  });

  const activateMutation = useMutation({
    mutationFn: activateIcpModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["icp-models"] });
    },
  });

  function handleCreated(response: ConversationResponse) {
    setShowCreate(false);
    setLastResult(response);
    setExpandedId(response.icp_model.id);
  }

  return (
    <div className="space-y-4">
      <Card isLoading={isLoading} error={error?.message}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">ICP Models</h2>
          <button
            onClick={() => {
              setShowCreate(true);
              setLastResult(null);
            }}
            className="py-2 px-4 rounded-sm text-sm font-semibold bg-primary text-white transition-opacity hover:opacity-85"
          >
            + New ICP via Claude
          </button>
        </div>

        {showCreate && (
          <div className="mb-6 p-4 border border-gray-200 rounded bg-gray-50">
            <IcpConversation
              onCreated={handleCreated}
              onCancel={() => setShowCreate(false)}
            />
          </div>
        )}

        {lastResult && lastResult.follow_up_questions.length > 0 && (
          <div className="mb-4 p-4 border border-blue-200 rounded bg-blue-50">
            <h4 className="text-sm font-semibold text-blue-900 mb-2">
              Claude suggests refining your ICP:
            </h4>
            <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
              {lastResult.follow_up_questions.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </div>
        )}

        {models && models.length === 0 && !showCreate && (
          <p className="text-muted text-sm text-center py-8">
            No ICP models yet. Click "New ICP via Claude" to create one.
          </p>
        )}

        {models && models.length > 0 && (
          <div className="space-y-2">
            {models.map((model) => {
              const isExpanded = expandedId === model.id;
              return (
                <div
                  key={model.id}
                  className="border border-gray-200 rounded"
                >
                  <div className="flex items-center gap-3 p-4">
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : model.id)}
                      className="text-xs text-muted w-5"
                    >
                      {isExpanded ? "▼" : "▶"}
                    </button>

                    <span className="font-semibold text-sm flex-1">
                      {model.name}
                    </span>

                    {model.is_active && (
                      <span className="text-[0.65rem] font-bold uppercase tracking-wide bg-success-bg text-success px-2 py-0.5 rounded-sm">
                        Active
                      </span>
                    )}

                    {!model.is_active && (
                      <button
                        onClick={() => activateMutation.mutate(model.id)}
                        disabled={activateMutation.isPending}
                        className="text-xs font-semibold text-primary hover:underline disabled:opacity-50"
                      >
                        Activate
                      </button>
                    )}

                    <button
                      onClick={() => onSearchProspects(model.id)}
                      className="text-xs font-semibold text-navy hover:underline"
                    >
                      Discover Prospects →
                    </button>
                  </div>

                  {isExpanded && (
                    <div className="px-4 pb-4 border-t border-gray-100">
                      <IcpModelDetail model={model} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}
