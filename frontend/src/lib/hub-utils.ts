import type { DashboardData, GoogleDoc, PanelId } from "../types/dashboard.types";

/* ── Mock dashboard data ───────────────────────────────── */

export const MOCK_DATA: DashboardData = {
  calendar: [
    { id: "c1", title: "Pipeline Review — Q2 Targets", time: "9:00 AM", endTime: "9:45 AM", type: "meeting" },
    { id: "c2", title: "1:1 with Sarah (Eng Lead)", time: "10:30 AM", endTime: "11:00 AM", type: "meeting" },
    { id: "c3", title: "Deep Work — Proposal Draft", time: "1:00 PM", endTime: "3:00 PM", type: "focus" },
    { id: "c4", title: "Client Call — Acme Corp", time: "3:30 PM", endTime: "4:00 PM", type: "external" },
  ],
  mail: [
    { id: "m1", sender: "Lisa Chen", subject: "Re: Partnership proposal — revised terms", preview: "Hi Tony, I've updated the terms per our call. Key change: 18-month commitment...", time: "8:42 AM", unread: true, flagged: true },
    { id: "m2", sender: "Dave Kumar", subject: "Q2 forecast deck ready for review", preview: "Attached the latest numbers. Revenue is tracking 12% above plan...", time: "8:15 AM", unread: true, flagged: false },
    { id: "m3", sender: "Jira", subject: "[PERF-342] Sprint velocity report", preview: "Your team completed 34 story points this sprint, up from 28...", time: "7:30 AM", unread: false, flagged: false },
    { id: "m4", sender: "AWS Billing", subject: "Your March invoice is available", preview: "Total charges: $2,847.33. View your detailed billing breakdown...", time: "6:00 AM", unread: false, flagged: false },
  ],
  slack: [],
  deliverables: [
    { id: "d1", name: "Q2 Revenue Forecast", dueDate: "Today", status: "urgent", owner: "Tony" },
    { id: "d2", name: "Acme Corp SOW", dueDate: "Mar 25", status: "active", owner: "Lisa" },
    { id: "d3", name: "API v2 Migration Plan", dueDate: "Mar 28", status: "active", owner: "Sarah" },
    { id: "d4", name: "Board Deck — March Update", dueDate: "Mar 30", status: "active", owner: "Tony" },
  ],
  briefing: [
    { id: "b1", text: "Review & approve revised Acme Corp partnership terms before client call at 3:30 PM", priority: "high", category: "Deals" },
    { id: "b2", text: "Q2 forecast deck is ready — verify pipeline numbers before tomorrow's board sync", priority: "high", category: "Revenue" },
    { id: "b3", text: "Sarah needs API schema review — blocks staging deploy", priority: "medium", category: "Engineering" },
    { id: "b4", text: "Acme LOI signed ($240k ARR) — update CRM and notify finance", priority: "medium", category: "Deals" },
  ],
  googledocs: [],
};

/* ── Hub greeting ──────────────────────────────────────── */

// TODO(human): Implement getGreeting(data: DashboardData): { headline: string; subtext: string }
export function getGreeting(_data: DashboardData): { headline: string; subtext: string } {
  return { headline: "Good morning", subtext: "Here's your daily snapshot." };
}

/* ── Card metadata ─────────────────────────────────────── */

export interface HubCardInfo {
  id: PanelId;
  label: string;
  countText: string;
  isUrgent: boolean;
  preview: string;
  accent: string;       // Tailwind border color class
  accentBg: string;     // Tailwind badge bg class
}

export function getCardInfos(data: DashboardData): HubCardInfo[] {
  return [
    buildCalendarCard(data),
    buildMailCard(data),
    buildSlackCard(data),
    buildDeliverablesCard(data),
    buildBriefingCard(data),
    buildGoogleDocsCard(data),
  ];
}

/* ── Per-category builders ─────────────────────────────── */

function buildCalendarCard(data: DashboardData): HubCardInfo {
  const count = data.calendar.length;
  const next = data.calendar[0];
  return {
    id: "calendar",
    label: "Schedule",
    countText: `${count} event${count !== 1 ? "s" : ""}`,
    isUrgent: false,
    preview: next ? `${next.title} · ${next.time}` : "No events today",
    accent: "border-l-navy",
    accentBg: "bg-navy",
  };
}

function buildMailCard(data: DashboardData): HubCardInfo {
  const unread = data.mail.filter((m) => m.unread).length;
  const top = data.mail.find((m) => m.unread && m.flagged) ?? data.mail.find((m) => m.unread);
  return {
    id: "mail",
    label: "Email",
    countText: `${unread} unread`,
    isUrgent: unread > 0,
    preview: top ? `${top.sender} — ${top.subject}` : "Inbox zero",
    accent: "border-l-navy",
    accentBg: unread > 0 ? "bg-coral" : "bg-navy",
  };
}

function buildSlackCard(data: DashboardData): HubCardInfo {
  const count = data.slack.length;
  const mentions = data.slack.filter((s) => s.isMention).length;
  const firstMention = data.slack.find((s) => s.isMention);
  const firstMsg = data.slack[0];

  let countText = "No messages";
  if (count > 0) countText = mentions > 0 ? `${mentions} mention${mentions !== 1 ? "s" : ""}` : `${count} message${count !== 1 ? "s" : ""}`;

  let preview = "No recent activity";
  if (firstMention) preview = `${firstMention.author} in ${firstMention.channel}: ${firstMention.text}`;
  else if (firstMsg) preview = `${firstMsg.author} in ${firstMsg.channel}: ${firstMsg.text}`;

  return {
    id: "slack",
    label: "Slack",
    countText,
    isUrgent: mentions > 0,
    preview,
    accent: "border-l-amber",
    accentBg: mentions > 0 ? "bg-coral" : "bg-amber",
  };
}

function buildDeliverablesCard(data: DashboardData): HubCardInfo {
  const urgent = data.deliverables.filter((d) => d.status === "urgent").length;
  const active = data.deliverables.filter((d) => d.status === "active").length;
  const top = data.deliverables.find((d) => d.status === "urgent") ?? data.deliverables[0];
  return {
    id: "deliverables",
    label: "Deliverables",
    countText: urgent > 0 ? `${urgent} urgent` : `${active} active`,
    isUrgent: urgent > 0,
    preview: top ? `${top.name} · due ${top.dueDate}` : "All clear",
    accent: "border-l-coral",
    accentBg: urgent > 0 ? "bg-coral" : "bg-navy",
  };
}

function buildBriefingCard(data: DashboardData): HubCardInfo {
  const count = data.briefing.length;
  const first = data.briefing[0];
  return {
    id: "briefing",
    label: "AI Briefing",
    countText: `${count} action${count !== 1 ? "s" : ""}`,
    isUrgent: false,
    preview: first?.text ?? "No actions today",
    accent: "border-l-status-scored",
    accentBg: "bg-status-scored",
  };
}

function buildGoogleDocsCard(data: DashboardData): HubCardInfo {
  const count = data.googledocs.length;
  const first = data.googledocs[0];
  return {
    id: "googledocs",
    label: "Google Docs",
    countText: count > 0 ? `${count} recent` : "No activity",
    isUrgent: false,
    preview: first ? `${first.name} · ${first.modifiedBy}` : "No recent doc activity",
    accent: "border-l-blue-500",
    accentBg: "bg-blue-500",
  };
}
