// טיפוסים תואמי סכמות הבקאנד (app/schemas.py).

export type ProjectTypeCode =
  | "landing"
  | "store"
  | "mobile"
  | "webapp"
  | "saas"
  | "automation"
  | "bot_chat"
  | "bot_voice"
  | "ai_agents"
  | "other";

export type PricingModel = "hourly" | "after_scoping" | "budget_friendly";
export type Availability = "available" | "limited" | "unavailable";
export type Timeline = "urgent" | "weeks" | "flexible";
export type Involvement = "full_handoff" | "collaborative";

export interface ProjectTypeMeta {
  code: string;
  label_he: string;
  description_he: string | null;
  sort_order: number;
}

export interface MatchRequestBody {
  project_type: string;
  pricing_prefs?: string[];
  timeline: string;
  involvement?: string | null;
  portfolio_only?: boolean;
  description?: string | null;
  stack_pref?: string[];
}

export interface MatchResultItem {
  developer_id: string;
  full_name: string;
  title?: string | null;
  highlight?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
  project_types: string[];
  stack?: string[] | null;
  ai_tools?: string[] | null;
  pricing_models: string[];
  hourly_rate?: number | null;
  availability: Availability;
  portfolio_url?: string | null;
  links?: Record<string, string> | null;
  is_verified: boolean;
  match_score: number;
}

export interface MatchResponse {
  request_id: string;
  results: MatchResultItem[];
}

export interface ReferralResponse {
  whatsapp_e164: string;
  wa_link: string;
}

export interface DeveloperCreateBody {
  full_name: string;
  title?: string | null;
  bio?: string | null;
  highlight?: string | null;
  avatar_url?: string | null;
  whatsapp_e164: string;
  project_types: string[];
  stack?: string[];
  ai_tools?: string[];
  pricing_models: string[];
  hourly_rate?: number | null;
  availability: string;
  portfolio_url?: string | null;
  links?: Record<string, string> | null;
}

export interface DeveloperPublic extends Omit<DeveloperCreateBody, "whatsapp_e164"> {
  id: string;
  is_verified: boolean;
  is_active: boolean;
}

/** תשובת POST /developers — כוללת edit_token חד-פעמי (לעריכה עתידית). */
export interface DeveloperCreateResponse extends DeveloperPublic {
  edit_token: string;
}

/** תשובות הלקוח שנאספות באשף (state פנימי). */
export interface MatchAnswers {
  project_type: ProjectTypeCode | null;
  pricing_prefs: PricingModel[];
  timeline: Timeline | null;
  involvement: Involvement | null;
  portfolio_only: boolean;
  description: string;
  stack_pref: string[];
}
