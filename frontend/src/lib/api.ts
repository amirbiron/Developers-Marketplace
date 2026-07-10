// לקוח API ל-7 ה-endpoints של הבקאנד. תומך ב-mock mode לפיתוח/דמו בלי בקאנד חי.

import * as mock from "./mock";
import type {
  DeveloperCreateBody,
  DeveloperCreateResponse,
  DeveloperPublic,
  MatchRequestBody,
  MatchResponse,
  ProjectTypeMeta,
  ReferralResponse,
} from "./types";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
// ברירת מחדל: בקאנד אמיתי. mock מופעל רק כש-VITE_USE_MOCK="true" (ראה .env.example).
export const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const REQUEST_TIMEOUT_MS = 15000;

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
      signal: controller.signal,
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new ApiError("הבקשה ארכה יותר מדי. נסו שוב מאוחר יותר.", 0);
    }
    throw new ApiError("לא הצלחנו להתחבר לשרת. בדוק את החיבור ונסה שוב.", 0);
  } finally {
    clearTimeout(timer);
  }
  if (!res.ok) {
    let detail = "אירעה שגיאה. נסו שוב.";
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* גוף לא-JSON — נשארים עם ההודעה הגנרית */
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

export async function getProjectTypes(): Promise<ProjectTypeMeta[]> {
  if (USE_MOCK) return mock.getProjectTypes();
  return request<ProjectTypeMeta[]>("/meta/project-types", { method: "GET" });
}

export async function postMatch(body: MatchRequestBody): Promise<MatchResponse> {
  if (USE_MOCK) return mock.postMatch(body);
  return request<MatchResponse>("/match", { method: "POST", body: JSON.stringify(body) });
}

export async function postReferral(
  requestId: string,
  developerId: string,
): Promise<ReferralResponse> {
  if (USE_MOCK) return mock.postReferral(requestId, developerId);
  return request<ReferralResponse>("/referrals", {
    method: "POST",
    body: JSON.stringify({ request_id: requestId, developer_id: developerId }),
  });
}

export async function postDeveloper(
  body: DeveloperCreateBody,
): Promise<DeveloperCreateResponse> {
  if (USE_MOCK) return mock.postDeveloper(body);
  return request<DeveloperCreateResponse>("/developers", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function getDeveloper(id: string): Promise<DeveloperPublic> {
  if (USE_MOCK) return mock.getDeveloper(id);
  return request<DeveloperPublic>(`/developers/${id}`, { method: "GET" });
}

export async function postAvatar(file: File): Promise<{ avatar_url: string }> {
  if (USE_MOCK) return mock.postAvatar(file);
  const form = new FormData();
  form.append("file", file);
  let res: Response;
  try {
    res = await fetch(`${BASE}/avatars`, { method: "POST", body: form });
  } catch {
    throw new ApiError("העלאת התמונה נכשלה. נסו שוב.", 0);
  }
  if (!res.ok) {
    let detail = "העלאת התמונה נכשלה.";
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<{ avatar_url: string }>;
}
