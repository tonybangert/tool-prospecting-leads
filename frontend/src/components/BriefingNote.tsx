import type { BriefingAction } from "../types/dashboard.types";
import { Sparkles, ArrowUpRight } from "lucide-react";

const PRIORITY_STYLES: Record<BriefingAction["priority"], string> = {
  high:   "bg-coral/10 text-coral border-coral/20",
  medium: "bg-amber/10 text-amber-dark border-amber/20",
  low:    "bg-navy/5 text-navy border-navy/10",
};

interface Props {
  actions: BriefingAction[];
}

export default function BriefingNote({ actions }: Props) {
  return (
    <div className="animate-fade-in">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles size={18} className="text-status-scored" />
        <h2 className="text-lg font-bold text-navy">AI Morning Briefing</h2>
      </div>
      <p className="text-xs text-muted mb-4">
        Synthesized from your calendar, email, Slack, and deliverables.
      </p>
      <div className="space-y-3">
        {actions.map((action, i) => (
          <div
            key={action.id}
            className={`
              flex items-start gap-3 rounded-lg border p-4
              ${PRIORITY_STYLES[action.priority]}
            `}
          >
            <span className="text-xs font-bold mt-0.5 min-w-[1.25rem]">{i + 1}.</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm leading-relaxed">{action.text}</p>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-[0.6rem] font-mono uppercase opacity-70">{action.category}</span>
                <ArrowUpRight size={10} className="opacity-50" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
