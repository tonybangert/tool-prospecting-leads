import type { GoogleDoc, GoogleDocAnalysis } from "../types/dashboard.types";
import { Loader2, AlertCircle, ExternalLink, LogIn } from "lucide-react";

interface Props {
  files: GoogleDoc[];
  analysis: GoogleDocAnalysis | null;
  loading?: boolean;
  error?: string | null;
  authenticated: boolean;
  authUrl?: string | null;
}

/** Format an ISO timestamp as a relative "X ago" string. */
function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

const PRIORITY_COLORS: Record<string, string> = {
  high: "bg-coral/15 text-coral",
  medium: "bg-amber/15 text-amber-dark",
  low: "bg-navy/10 text-navy/70",
};

export default function GoogleDocsPanel({ files, analysis, loading, error, authenticated, authUrl }: Props) {
  return (
    <div className="animate-fade-in space-y-3">
      <h2 className="text-lg font-bold text-navy mb-4">Google Docs — Last 12 Hours</h2>

      {/* Not authenticated — show connect button */}
      {!authenticated && authUrl && (
        <a
          href={authUrl}
          className="flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-6 rounded-lg transition-colors"
        >
          <LogIn size={18} />
          Connect Google Drive
        </a>
      )}

      {/* Loading */}
      {loading && files.length === 0 && (
        <div className="flex items-center gap-3 text-muted py-8 justify-center">
          <Loader2 size={18} className="animate-spin" />
          <span className="text-sm">Loading Drive activity...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 bg-coral/5 border border-coral/20 rounded-lg p-4">
          <AlertCircle size={16} className="text-coral shrink-0" />
          <span className="text-sm text-coral">{error}</span>
        </div>
      )}

      {/* AI Analysis Section */}
      {analysis && (analysis.summary || analysis.todos.length > 0 || analysis.correlations.length > 0) && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-navy flex items-center gap-2">
            <span className="bg-blue-500 text-white text-[0.6rem] px-2 py-0.5 rounded-full font-bold">AI</span>
            Activity Analysis
          </h3>

          {analysis.summary && (
            <p className="text-sm text-muted leading-relaxed">{analysis.summary}</p>
          )}

          {analysis.todos.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-navy/60 uppercase tracking-wide mb-2">Action Items</h4>
              <ul className="space-y-2">
                {analysis.todos.map((todo, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className={`shrink-0 text-[0.6rem] font-bold px-1.5 py-0.5 rounded mt-0.5 ${PRIORITY_COLORS[todo.priority] ?? PRIORITY_COLORS.low}`}>
                      {todo.priority}
                    </span>
                    <span className="text-navy">{todo.text}</span>
                    {todo.source && (
                      <span className="shrink-0 text-[0.6rem] text-muted ml-auto">from {todo.source}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysis.correlations.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-navy/60 uppercase tracking-wide mb-2">Connections</h4>
              <ul className="space-y-1.5">
                {analysis.correlations.map((c, i) => (
                  <li key={i} className="text-sm text-muted flex items-start gap-2">
                    <span className="text-blue-400 shrink-0">&#8226;</span>
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {authenticated && !loading && !error && files.length === 0 && (
        <div className="text-center py-8 text-muted text-sm">
          No documents modified in the last 12 hours.
        </div>
      )}

      {/* File list */}
      {files.map((doc) => (
        <a
          key={doc.id}
          href={doc.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-start gap-3 bg-white rounded-lg border border-gray-100 p-4 hover:shadow-md transition-shadow group"
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-semibold text-navy truncate">{doc.name}</span>
              <ExternalLink size={12} className="text-text-light opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
            </div>
            <div className="flex items-center gap-3 text-xs text-muted">
              {doc.modifiedBy && <span>{doc.modifiedBy}</span>}
              <span>{timeAgo(doc.modifiedTime)}</span>
            </div>
          </div>
        </a>
      ))}
    </div>
  );
}
