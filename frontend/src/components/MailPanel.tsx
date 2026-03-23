import type { MailMessage } from "../types/dashboard.types";
import { Flag, MailOpen, Mail } from "lucide-react";

interface Props {
  messages: MailMessage[];
}

export default function MailPanel({ messages }: Props) {
  return (
    <div className="animate-fade-in space-y-3">
      <h2 className="text-lg font-bold text-navy mb-4">Inbox</h2>
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`
            flex items-start gap-4 rounded-lg border border-gray-100 p-4
            hover:shadow-md transition-shadow
            ${msg.unread ? "bg-white" : "bg-gray-50/60"}
          `}
        >
          <div className="pt-0.5">
            {msg.unread ? (
              <Mail size={16} className="text-navy" />
            ) : (
              <MailOpen size={16} className="text-muted" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-sm ${msg.unread ? "font-semibold text-navy" : "text-muted"}`}>
                {msg.sender}
              </span>
              {msg.flagged && <Flag size={12} className="text-coral fill-coral" />}
              <span className="ml-auto text-[0.65rem] text-text-light">{msg.time}</span>
            </div>
            <p className={`text-sm ${msg.unread ? "font-medium text-navy/90" : "text-muted"} truncate`}>
              {msg.subject}
            </p>
            <p className="text-xs text-muted mt-1 line-clamp-1">{msg.preview}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
