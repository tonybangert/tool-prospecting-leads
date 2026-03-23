import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import type { DashboardData, PanelId, GoogleDocAnalysis } from "../types/dashboard.types";
import { getCardInfos } from "../lib/hub-utils";
import HubCard from "./HubCard";
import CalendarPanel from "./CalendarPanel";
import MailPanel from "./MailPanel";
import SlackPanel from "./SlackPanel";
import DeliverablesList from "./DeliverablesList";
import BriefingNote from "./BriefingNote";
import GoogleDocsPanel from "./GoogleDocsPanel";

interface Props {
  data: DashboardData;
  slackLoading?: boolean;
  slackError?: string | null;
  googleLoading?: boolean;
  googleError?: string | null;
  googleAuthenticated?: boolean;
  googleAuthUrl?: string | null;
  googleAnalysis?: GoogleDocAnalysis | null;
}

const PANEL_LABELS: Record<PanelId, string> = {
  calendar: "Schedule",
  mail: "Email",
  slack: "Slack",
  deliverables: "Deliverables",
  briefing: "AI Briefing",
  googledocs: "Google Docs",
};

const STAGGER: string[] = [
  "hub-stagger-1", "hub-stagger-2", "hub-stagger-3",
  "hub-stagger-4", "hub-stagger-5", "hub-stagger-6",
];

export default function DashboardHub({
  data, slackLoading, slackError,
  googleLoading, googleError, googleAuthenticated, googleAuthUrl, googleAnalysis,
}: Props) {
  const [expanded, setExpanded] = useState<PanelId | null>(null);
  const cards = getCardInfos(data);

  /* ── Expanded: single panel ──────────────────────────── */
  if (expanded) {
    return (
      <div className="animate-fade-in">
        <button
          onClick={() => setExpanded(null)}
          className="flex items-center gap-2 text-sm text-muted hover:text-navy transition-colors mb-5 group"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-0.5 transition-transform" />
          Back to Hub
          <span className="text-text-light">· {PANEL_LABELS[expanded]}</span>
        </button>
        {renderPanel(expanded, data, {
          slackLoading, slackError,
          googleLoading, googleError, googleAuthenticated, googleAuthUrl, googleAnalysis,
        })}
      </div>
    );
  }

  /* ── Hub: card grid (3 + 3) ────────────────────────────── */
  return (
    <div className="animate-fade-in">
      {/* Top row: 3 cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {cards.slice(0, 3).map((info, i) => (
          <HubCard
            key={info.id}
            info={info}
            staggerClass={STAGGER[i] ?? ""}
            onClick={() => setExpanded(info.id)}
          />
        ))}
      </div>

      {/* Bottom row: 3 cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.slice(3).map((info, i) => (
          <HubCard
            key={info.id}
            info={info}
            staggerClass={STAGGER[i + 3] ?? ""}
            onClick={() => setExpanded(info.id)}
          />
        ))}
      </div>
    </div>
  );
}

/* ── Panel renderer ────────────────────────────────────── */
interface PanelExtras {
  slackLoading?: boolean;
  slackError?: string | null;
  googleLoading?: boolean;
  googleError?: string | null;
  googleAuthenticated?: boolean;
  googleAuthUrl?: string | null;
  googleAnalysis?: GoogleDocAnalysis | null;
}

function renderPanel(id: PanelId, data: DashboardData, extras: PanelExtras) {
  switch (id) {
    case "calendar":
      return <CalendarPanel events={data.calendar} />;
    case "mail":
      return <MailPanel messages={data.mail} />;
    case "slack":
      return <SlackPanel messages={data.slack} loading={extras.slackLoading} error={extras.slackError} />;
    case "deliverables":
      return <DeliverablesList deliverables={data.deliverables} />;
    case "briefing":
      return <BriefingNote actions={data.briefing} />;
    case "googledocs":
      return (
        <GoogleDocsPanel
          files={data.googledocs}
          analysis={extras.googleAnalysis ?? null}
          loading={extras.googleLoading}
          error={extras.googleError}
          authenticated={extras.googleAuthenticated ?? false}
          authUrl={extras.googleAuthUrl}
        />
      );
  }
}
