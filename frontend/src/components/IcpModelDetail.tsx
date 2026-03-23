import type { IcpModel } from "../types/api.types";

interface Props {
  model: IcpModel;
}

function WeightBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="w-40 text-muted capitalize">{label.replace(/_/g, " ")}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full"
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="w-12 text-right font-mono text-xs text-gray-600">
        {Math.round(value * 100)}%
      </span>
    </div>
  );
}

interface Persona {
  title?: string;
  seniority?: string;
  context?: string;
}

export default function IcpModelDetail({ model }: Props) {
  const criteria = model.criteria as Record<string, unknown>;
  const weights = model.scoring_weights;

  // Separate buying_triggers and personas for custom rendering
  const buyingTriggers = Array.isArray(criteria.buying_triggers)
    ? (criteria.buying_triggers as string[])
    : [];
  const personas = Array.isArray(criteria.personas)
    ? (criteria.personas as Persona[])
    : [];

  const criteriaEntries = Object.entries(criteria).filter(
    ([key, v]) =>
      v != null && v !== "" && key !== "buying_triggers" && key !== "personas",
  );

  return (
    <div className="mt-4 space-y-5">
      {model.description && (
        <p className="text-sm text-muted">{model.description}</p>
      )}

      {criteriaEntries.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-muted mb-2">
            Criteria
          </h4>
          <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-sm">
            {criteriaEntries.map(([key, val]) => (
              <div key={key} className="flex gap-2">
                <span className="text-muted capitalize">{key.replace(/_/g, " ")}:</span>
                <span className="text-gray-900">
                  {Array.isArray(val) ? val.join(", ") : String(val)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {personas.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-muted mb-2">
            Decision Makers
          </h4>
          <div className="space-y-1.5 text-sm">
            {personas.map((p, i) => (
              <div key={i} className="flex gap-2">
                <span className="font-medium text-gray-900">
                  {p.title}{p.seniority ? ` (${p.seniority})` : ""}
                </span>
                {p.context && (
                  <span className="text-muted">— {p.context}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {buyingTriggers.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-muted mb-2">
            Buying Triggers
          </h4>
          <ul className="list-disc list-inside text-sm text-gray-900 space-y-0.5">
            {buyingTriggers.map((trigger, i) => (
              <li key={i}>{trigger}</li>
            ))}
          </ul>
        </div>
      )}

      {Object.keys(weights).length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-muted mb-2">
            Scoring Weights
          </h4>
          <div className="space-y-2">
            {Object.entries(weights).map(([key, val]) => (
              <WeightBar key={key} label={key} value={val} />
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-4 text-xs text-text-light">
        <span>Version {model.version}</span>
        <span>Created {new Date(model.created_at).toLocaleDateString()}</span>
        {model.updated_at && (
          <span>Updated {new Date(model.updated_at).toLocaleDateString()}</span>
        )}
      </div>
    </div>
  );
}
