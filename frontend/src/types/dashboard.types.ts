/* ── Dashboard hub data types ──────────────────────────── */

export interface CalendarEvent {
  id: string;
  title: string;
  time: string;        // e.g. "9:00 AM"
  endTime: string;     // e.g. "9:30 AM"
  type: "meeting" | "focus" | "external";
}

export interface MailMessage {
  id: string;
  sender: string;
  subject: string;
  preview: string;
  time: string;
  unread: boolean;
  flagged: boolean;
}

export interface SlackMessage {
  id: string;
  channel: string;
  author: string;
  text: string;
  time: string;
  isMention: boolean;
}

export interface Deliverable {
  id: string;
  name: string;
  dueDate: string;
  status: "urgent" | "active" | "completed";
  owner: string;
}

export interface BriefingAction {
  id: string;
  text: string;
  priority: "high" | "medium" | "low";
  category: string;
}

export interface GoogleDoc {
  id: string;
  name: string;
  mimeType: string;
  modifiedTime: string;
  modifiedBy: string;
  url: string;
}

export interface GoogleDocTodo {
  text: string;
  source: string;
  priority: "high" | "medium" | "low";
}

export interface GoogleDocAnalysis {
  summary: string;
  todos: GoogleDocTodo[];
  correlations: string[];
}

export interface DashboardData {
  calendar: CalendarEvent[];
  mail: MailMessage[];
  slack: SlackMessage[];
  deliverables: Deliverable[];
  briefing: BriefingAction[];
  googledocs: GoogleDoc[];
}

export type PanelId = "calendar" | "mail" | "slack" | "deliverables" | "briefing" | "googledocs";
