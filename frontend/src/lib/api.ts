import type {
  IcpModel,
  ConversationResponse,
  ProspectResult,
} from "../types/api.types";
import type { SlackMessage, GoogleDoc, GoogleDocAnalysis } from "../types/dashboard.types";

const BASE = "/api";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`);
  return res.json() as Promise<T>;
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`);
  return res.json() as Promise<T>;
}

/* ── ICP endpoints ─────────────────────────────────────── */
export const fetchIcpModels = () => fetchJSON<IcpModel[]>("/icp/");

export const fetchIcpModel = (id: string) => fetchJSON<IcpModel>(`/icp/${id}`);

export const activateIcpModel = (id: string) =>
  postJSON<IcpModel>(`/icp/${id}/activate`, {});

export const createIcpConversation = (message: string) =>
  postJSON<ConversationResponse>("/icp/conversation", { message });

/* ── Google Drive ─────────────────────────────────────── */
export interface GoogleDriveFeedResponse {
  files: GoogleDoc[];
  analysis: GoogleDocAnalysis | null;
  authenticated: boolean;
  authUrl: string | null;
  error: string | null;
}

export const fetchGoogleDriveFiles = () =>
  fetchJSON<GoogleDriveFeedResponse>("/google/files");

/* ── Slack ────────────────────────────────────────────── */
export const fetchSlackMessages = () =>
  fetchJSON<{ messages: SlackMessage[]; error: string | null }>("/slack/messages");

/* ── Prospect search (legacy, unused) ─────────────────── */
export const searchProspects = (modelId: string, page = 1) =>
  postJSON<ProspectResult>(`/prospects/discover/${modelId}`, { page });

/* ── Prospect pipeline endpoints ──────────────────────── */
export const discoverProspects = (modelId: string, page = 1) =>
  postJSON<ProspectResult>(`/prospects/discover/${modelId}`, { page });

export const selectProspects = (modelId: string, ids: string[]) =>
  postJSON<ProspectResult>(`/prospects/select/${modelId}`, {
    prospect_ids: ids,
  });

export const enrichProspects = (modelId: string, ids: string[]) =>
  postJSON<ProspectResult>(`/prospects/enrich/${modelId}`, {
    prospect_ids: ids,
  });

export const listProspects = (
  modelId: string,
  page = 1,
  perPage = 25,
  status?: string,
) => {
  let url = `/prospects/${modelId}?page=${page}&per_page=${perPage}`;
  if (status) url += `&status=${status}`;
  return fetchJSON<ProspectResult>(url);
};
