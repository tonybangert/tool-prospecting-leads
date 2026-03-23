import type { HubCardInfo } from "../lib/hub-utils";
import { Calendar, Mail, MessageCircle, Target, Brain, FolderOpen, type LucideIcon } from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  calendar: Calendar,
  mail: Mail,
  slack: MessageCircle,
  deliverables: Target,
  briefing: Brain,
  googledocs: FolderOpen,
};

interface Props {
  info: HubCardInfo;
  staggerClass: string;
  onClick: () => void;
}

export default function HubCard({ info, staggerClass, onClick }: Props) {
  const Icon = ICONS[info.id] ?? Calendar;

  return (
    <button
      onClick={onClick}
      className={`
        group relative text-left w-full
        bg-white/80 backdrop-blur-sm rounded-xl
        border-l-4 ${info.accent} border border-gray-100
        shadow hover:shadow-lg
        hover:-translate-y-1 transition-all duration-200
        p-5 animate-fade-in ${staggerClass}
      `}
    >
      {/* Count badge — upper right */}
      <span
        className={`
          absolute top-3 right-3
          ${info.isUrgent ? info.accentBg : "bg-navy/80"} text-white
          text-[0.65rem] font-bold px-2.5 py-0.5 rounded-full
        `}
      >
        {info.countText}
      </span>

      {/* Icon + label */}
      <div className="flex items-center gap-3 mb-3">
        <div className={`${info.accentBg} text-white p-2 rounded-lg`}>
          <Icon size={20} strokeWidth={2} />
        </div>
        <h3 className="font-semibold text-navy text-sm">{info.label}</h3>
      </div>

      {/* Preview line */}
      <p className="text-muted text-xs leading-relaxed line-clamp-1">
        {info.preview}
      </p>

      {/* Hover hint */}
      <span className="absolute bottom-3 right-3 text-text-light text-[0.6rem] opacity-0 group-hover:opacity-100 transition-opacity">
        Click to expand &rarr;
      </span>
    </button>
  );
}
