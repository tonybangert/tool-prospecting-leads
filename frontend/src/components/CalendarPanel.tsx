import type { CalendarEvent } from "../types/dashboard.types";
import { Clock, Users, Monitor, ExternalLink } from "lucide-react";

const TYPE_STYLES: Record<CalendarEvent["type"], { icon: typeof Clock; bg: string; label: string }> = {
  meeting:  { icon: Users, bg: "bg-navy/10 text-navy", label: "Meeting" },
  focus:    { icon: Monitor, bg: "bg-amber/10 text-amber-dark", label: "Focus" },
  external: { icon: ExternalLink, bg: "bg-coral/10 text-coral", label: "External" },
};

interface Props {
  events: CalendarEvent[];
}

export default function CalendarPanel({ events }: Props) {
  return (
    <div className="animate-fade-in space-y-3">
      <h2 className="text-lg font-bold text-navy mb-4">Today's Schedule</h2>
      {events.map((ev) => {
        const style = TYPE_STYLES[ev.type];
        const Icon = style.icon;
        return (
          <div
            key={ev.id}
            className="flex items-center gap-4 bg-white rounded-lg border border-gray-100 p-4 hover:shadow-md transition-shadow"
          >
            <div className="text-right min-w-[5rem]">
              <p className="text-sm font-semibold text-navy">{ev.time}</p>
              <p className="text-[0.65rem] text-muted">{ev.endTime}</p>
            </div>
            <div className="w-px h-10 bg-gray-200" />
            <div className={`p-2 rounded-lg ${style.bg}`}>
              <Icon size={16} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm text-navy truncate">{ev.title}</p>
              <p className="text-[0.65rem] text-muted">{style.label}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
