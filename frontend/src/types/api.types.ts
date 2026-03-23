/* ── ICP Models ─────────────────────────────────────────── */
export interface IcpModel {
  id: string;
  name: string;
  description: string | null;
  criteria: Record<string, unknown>;
  scoring_weights: Record<string, number>;
  version: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface ConversationResponse {
  icp_model: IcpModel;
  follow_up_questions: string[];
}

/* ── Prospects ─────────────────────────────────────────── */
export interface Prospect {
  id: string;
  icp_model_id: string;
  apollo_person_id: string | null;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  phone: string | null;
  title: string | null;
  seniority: string | null;
  linkedin_url: string | null;
  company_name: string | null;
  company_domain: string | null;
  industry: string | null;
  employee_count: number | null;
  company_location: string | null;
  icp_fit_score: number | null;
  score_breakdown: Record<string, number> | null;
  source: string | null;
  discovery_data: Record<string, unknown> | null;
  enriched_at: string | null;
  status: string;
  created_at: string;
}

export interface ProspectResult {
  items: Prospect[];
  total: number;
}

export type PipelineStep = "discover" | "select" | "enrich" | "results";
