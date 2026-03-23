import { useState } from "react";
import type { Prospect } from "../types/api.types";

interface Props {
  prospects: Prospect[];
  onEnrich: (ids: string[]) => void;
  isEnriching: boolean;
}

function fmtScore(score: number | null): string {
  if (score == null) return "—";
  return `${Math.round(score * 100)}%`;
}

export default function DiscoveryTable({ prospects, onEnrich, isEnriching }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const allSelected = prospects.length > 0 && selected.size === prospects.length;

  function toggleAll() {
    if (allSelected) {
      setSelected(new Set());
    } else {
      setSelected(new Set(prospects.map((p) => p.id)));
    }
  }

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function handleEnrich() {
    onEnrich(Array.from(selected));
  }

  if (prospects.length === 0) {
    return <p className="text-muted text-center py-8">No prospects discovered yet.</p>;
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-3">
        <p className="text-[0.82rem] text-muted">
          {selected.size} of {prospects.length} selected
        </p>
        <button
          onClick={handleEnrich}
          disabled={selected.size === 0 || isEnriching}
          className="py-2 px-5 rounded-sm text-[0.82rem] font-semibold bg-amber text-navy whitespace-nowrap transition-opacity hover:opacity-85 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isEnriching
            ? "Enriching…"
            : `Enrich Selected (${selected.size})`}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-[0.8rem]">
          <thead>
            <tr>
              <th className="text-left py-2 px-3 border-b-2 border-navy">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={toggleAll}
                  className="accent-amber w-4 h-4 cursor-pointer"
                />
              </th>
              {["Name", "Title", "Company", "Location", "Rough Score", "LinkedIn"].map(
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
              <tr
                key={p.id}
                className={`hover:bg-amber-bg cursor-pointer ${
                  selected.has(p.id) ? "bg-amber-bg/50" : ""
                }`}
                onClick={() => toggle(p.id)}
              >
                <td className="py-2 px-3 border-b border-gray-200">
                  <input
                    type="checkbox"
                    checked={selected.has(p.id)}
                    onChange={() => toggle(p.id)}
                    onClick={(e) => e.stopPropagation()}
                    className="accent-amber w-4 h-4 cursor-pointer"
                  />
                </td>
                <td className="py-2 px-3 border-b border-gray-200 font-semibold whitespace-nowrap">
                  {p.first_name ?? ""} {p.last_name ?? ""}
                </td>
                <td className="py-2 px-3 border-b border-gray-200">{p.title ?? "—"}</td>
                <td className="py-2 px-3 border-b border-gray-200">{p.company_name ?? "—"}</td>
                <td className="py-2 px-3 border-b border-gray-200">{p.company_location ?? "—"}</td>
                <td className="py-2 px-3 border-b border-gray-200">
                  <span className="inline-block px-2 py-0.5 rounded-[3px] text-[0.72rem] font-bold font-mono bg-amber-bg text-amber-dark">
                    {fmtScore(p.icp_fit_score)}
                  </span>
                </td>
                <td className="py-2 px-3 border-b border-gray-200">
                  {p.linkedin_url ? (
                    <a
                      href={p.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-navy no-underline font-medium hover:underline"
                      onClick={(e) => e.stopPropagation()}
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
    </div>
  );
}
