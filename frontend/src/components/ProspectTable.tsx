import type { Prospect } from "../types/api.types";

interface Props {
  prospects: Prospect[];
}

function scoreClass(score: number | null): string {
  if (score == null) return "bg-bg text-text-light";
  if (score >= 0.7) return "bg-success-bg text-success";
  if (score >= 0.4) return "bg-warning-bg text-warning";
  return "bg-coral-bg text-coral";
}

function fmtScore(score: number | null): string {
  if (score == null) return "N/A";
  return `${Math.round(score * 100)}%`;
}

const BREAKDOWN_LABELS: Record<string, string> = {
  firmographic_fit: "Firmographic",
  tech_fit: "Tech",
  persona_match: "Persona",
  timing_signals: "Timing",
  data_confidence: "Confidence",
};

function barColor(value: number): string {
  if (value >= 0.7) return "bg-success";
  if (value >= 0.4) return "bg-amber";
  return "bg-coral";
}

function renderScoreBreakdown(
  breakdown: Record<string, number> | null,
): React.ReactNode {
  if (!breakdown) return <span className="text-text-light">—</span>;

  return (
    <div className="flex flex-col gap-0.5 min-w-[120px]">
      {Object.entries(BREAKDOWN_LABELS).map(([key, label]) => {
        const value = breakdown[key] ?? 0;
        return (
          <div key={key} className="flex items-center gap-1.5">
            <span className="text-[0.6rem] text-muted w-16 text-right">{label}</span>
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${barColor(value)}`}
                style={{ width: `${Math.round(value * 100)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function ProspectTable({ prospects }: Props) {
  if (prospects.length === 0) {
    return <p className="text-muted text-center py-8">No prospects to display.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-[0.8rem]">
        <thead>
          <tr>
            {["Name", "Title", "Company", "Location", "Seniority", "Email", "Phone", "ICP Fit", "Breakdown", "Status", "Profile"].map(
              (h) => (
                <th
                  key={h}
                  className="text-left font-semibold text-muted py-2 px-3 border-b-2 border-navy uppercase text-[0.68rem] tracking-wide"
                >
                  {h}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {prospects.map((p) => (
            <tr key={p.id} className="hover:bg-bg">
              <td className="py-2 px-3 border-b border-gray-200 font-semibold whitespace-nowrap">
                {p.first_name ?? ""} {p.last_name ?? ""}
              </td>
              <td className="py-2 px-3 border-b border-gray-200">{p.title ?? "—"}</td>
              <td className="py-2 px-3 border-b border-gray-200">{p.company_name ?? "—"}</td>
              <td className="py-2 px-3 border-b border-gray-200">{p.company_location ?? "—"}</td>
              <td className="py-2 px-3 border-b border-gray-200 capitalize">{p.seniority ?? "—"}</td>
              <td className="py-2 px-3 border-b border-gray-200">
                {p.email ? (
                  <a href={`mailto:${p.email}`} className="text-navy hover:underline">
                    {p.email}
                  </a>
                ) : "—"}
              </td>
              <td className="py-2 px-3 border-b border-gray-200 whitespace-nowrap">
                {p.phone ? (
                  <a href={`tel:${p.phone}`} className="text-navy hover:underline">
                    {p.phone}
                  </a>
                ) : "—"}
              </td>
              <td className="py-2 px-3 border-b border-gray-200">
                <span
                  className={`inline-block px-2 py-0.5 rounded-[3px] text-[0.72rem] font-bold font-mono ${scoreClass(p.icp_fit_score)}`}
                >
                  {fmtScore(p.icp_fit_score)}
                </span>
              </td>
              <td className="py-2 px-3 border-b border-gray-200">
                {renderScoreBreakdown(p.score_breakdown)}
              </td>
              <td className="py-2 px-3 border-b border-gray-200">
                {p.enriched_at ? (
                  <span className="inline-block px-2 py-0.5 rounded-[3px] text-[0.68rem] font-semibold bg-success-bg text-success">
                    Enriched
                  </span>
                ) : (
                  <span className="inline-block px-2 py-0.5 rounded-[3px] text-[0.68rem] font-semibold bg-amber-bg text-amber-dark capitalize">
                    {p.status}
                  </span>
                )}
              </td>
              <td className="py-2 px-3 border-b border-gray-200">
                {p.linkedin_url ? (
                  <a
                    href={p.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-navy no-underline font-medium hover:underline"
                  >
                    LinkedIn
                  </a>
                ) : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
