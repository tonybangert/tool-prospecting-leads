import type { SlackMessage } from "../types/dashboard.types";
import { AtSign, Hash, Loader2, AlertCircle } from "lucide-react";

interface Props {
  messages: SlackMessage[];
  loading?: boolean;
  error?: string | null;
}

export default function SlackPanel({ messages, loading, error }: Props) {
  return (
    <div className="animate-fade-in space-y-3">
      <h2 className="text-lg font-bold text-navy mb-4">Slack</h2>

      {loading && messages.length === 0 && (
        <div className="flex items-center gap-3 text-muted py-8 justify-center">
          <Loader2 size={18} className="animate-spin" />
          <span className="text-sm">Connecting to Slack...</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-3 bg-coral/5 border border-coral/20 rounded-lg p-4">
          <AlertCircle size={16} className="text-coral shrink-0" />
          <span className="text-sm text-coral">{error}</span>
        </div>
      )}

      {!loading && !error && messages.length === 0 && (
        <div className="text-center py-8 text-muted text-sm">
          No recent messages across your channels.
        </div>
      )}

      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`
            flex items-start gap-3 bg-white rounded-lg border border-gray-100 p-4
            hover:shadow-md transition-shadow
            ${msg.isMention ? "ring-1 ring-amber/40" : ""}
          `}
        >
          <div className="pt-0.5">
            {msg.isMention ? (
              <AtSign size={14} className="text-amber" />
            ) : (
              <Hash size={14} className="text-muted" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono text-muted">{msg.channel}</span>
              <span className="text-[0.6rem] text-text-light">{msg.time}</span>
              {msg.isMention && (
                <span className="bg-amber/15 text-amber-dark text-[0.6rem] font-bold px-1.5 py-0.5 rounded">
                  Mention
                </span>
              )}
            </div>
            <p className="text-sm text-navy">
              <span className="font-semibold">{msg.author}</span>{" "}
              <span className="text-muted">{msg.text}</span>
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
