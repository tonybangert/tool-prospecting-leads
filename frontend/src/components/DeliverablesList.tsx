import type { Deliverable } from "../types/dashboard.types";
import { AlertTriangle, Clock, CheckCircle2 } from "lucide-react";

const STATUS_STYLES: Record<Deliverable["status"], { icon: typeof Clock; color: string; badge: string }> = {
  urgent:    { icon: AlertTriangle, color: "text-coral", badge: "bg-coral/10 text-coral" },
  active:    { icon: Clock, color: "text-amber-dark", badge: "bg-amber/10 text-amber-dark" },
  completed: { icon: CheckCircle2, color: "text-success", badge: "bg-success/10 text-success" },
};

interface Props {
  deliverables: Deliverable[];
}

export default function DeliverablesList({ deliverables }: Props) {
  return (
    <div className="animate-fade-in space-y-3">
      <h2 className="text-lg font-bold text-navy mb-4">Deliverables</h2>
      {deliverables.map((d) => {
        const style = STATUS_STYLES[d.status];
        const Icon = style.icon;
        return (
          <div
            key={d.id}
            className="flex items-center gap-4 bg-white rounded-lg border border-gray-100 p-4 hover:shadow-md transition-shadow"
          >
            <Icon size={18} className={style.color} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-navy truncate">{d.name}</p>
              <p className="text-[0.65rem] text-muted">Owner: {d.owner}</p>
            </div>
            <span className={`text-[0.65rem] font-bold px-2.5 py-1 rounded-full ${style.badge}`}>
              {d.status === "urgent" ? `Due ${d.dueDate}` : d.dueDate}
            </span>
          </div>
        );
      })}
    </div>
  );
}
