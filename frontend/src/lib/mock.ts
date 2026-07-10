// שכבת mock — נתוני דמו + פורט נאמן של מנוע ההתאמה (app/engine.py) ל-TypeScript,
// כדי שהדמו יתנהג בדיוק כמו הבקאנד. מופעל כש-VITE_USE_MOCK != "false".

import type {
  DeveloperCreateBody,
  DeveloperCreateResponse,
  DeveloperPublic,
  MatchRequestBody,
  MatchResponse,
  MatchResultItem,
  ProjectTypeMeta,
  ReferralResponse,
} from "./types";
import { CATEGORIES } from "./labels";

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** פרופיל דמו — כמו MatchResultItem אך בלי match_score, עם שדות פנימיים. */
type DevProfile = Omit<MatchResultItem, "match_score"> & {
  _whatsapp: string;
  _recency: number; // ככל שגבוה יותר → עדכני יותר (tiebreaker)
};

const DEVELOPERS: DevProfile[] = [
  {
    developer_id: "d1",
    full_name: "יעל אברהמי",
    title: "Full-stack · SaaS",
    highlight: "מקימה SaaS עם billing ותשתית תשלומים מהיום הראשון",
    bio: "מפתחת פוֹל-סטאק עם 7 שנות ניסיון בבניית מוצרי SaaS מאפס — אימות, מנויים, דשבורדים.",
    avatar_url: null,
    project_types: ["saas", "webapp"],
    stack: ["React", "Next.js", "FastAPI", "Supabase", "Stripe"],
    ai_tools: ["Claude Code", "Cursor"],
    pricing_models: ["hourly", "budget_friendly"],
    hourly_rate: 380,
    availability: "available",
    portfolio_url: "https://yael.dev",
    links: { github: "https://github.com/yael", linkedin: "https://linkedin.com/in/yael" },
    is_verified: true,
    _whatsapp: "972501112233",
    _recency: 9,
  },
  {
    developer_id: "d2",
    full_name: "איתי לוי",
    title: "Mobile Engineer",
    highlight: "אפליקציות מובייל חלקות ומהירות ב-React Native",
    bio: "מתמחה באפליקציות מובייל חוצות-פלטפורמה עם ביצועים גבוהים וחוויית משתמש מוקפדת.",
    avatar_url: null,
    project_types: ["mobile", "webapp"],
    stack: ["React Native", "Expo", "TypeScript", "Firebase"],
    ai_tools: ["Cursor"],
    pricing_models: ["after_scoping"],
    hourly_rate: null,
    availability: "available",
    portfolio_url: "https://itai.app",
    links: { github: "https://github.com/itai" },
    is_verified: true,
    _whatsapp: "972502223344",
    _recency: 8,
  },
  {
    developer_id: "d3",
    full_name: "נועה שרון",
    title: "E-commerce Developer",
    highlight: "חנויות Shopify שממירות — עיצוב שמוכר",
    bio: "בונה חנויות אונליין מהירות וממירות, כולל אינטגרציות תשלום ומשלוח לשוק הישראלי.",
    avatar_url: null,
    project_types: ["store", "landing"],
    stack: ["Shopify", "Liquid", "React", "Tailwind"],
    ai_tools: [],
    pricing_models: ["hourly"],
    hourly_rate: 300,
    availability: "limited",
    portfolio_url: "https://noa-store.co.il",
    links: { linkedin: "https://linkedin.com/in/noa" },
    is_verified: false,
    _whatsapp: "972503334455",
    _recency: 6,
  },
  {
    developer_id: "d4",
    full_name: "דניאל כ״ץ",
    title: "Automation & AI",
    highlight: "אוטומציות ו-AI agents שחוסכות לצוות שעות בשבוע",
    bio: "מחבר מערכות, בונה אוטומציות ו-agents חכמים שמייתרים עבודה ידנית ומאיצים תהליכים.",
    avatar_url: null,
    project_types: ["automation", "ai_agents"],
    stack: ["Python", "LangChain", "n8n", "OpenAI", "Supabase"],
    ai_tools: ["Claude Code", "Claude", "Cursor"],
    pricing_models: ["after_scoping", "budget_friendly"],
    hourly_rate: null,
    availability: "available",
    portfolio_url: "https://daniel-ai.dev",
    links: { github: "https://github.com/danielk" },
    is_verified: true,
    _whatsapp: "972504445566",
    _recency: 9,
  },
  {
    developer_id: "d5",
    full_name: "מור פרידמן",
    title: "Bot Developer",
    highlight: "בוטים ל-WhatsApp ו-Telegram שמוכרים ומשרתים",
    bio: "בונה בוטים חכמים לשירות ומכירות עם אינטגרציות CRM ותשלומים.",
    avatar_url: null,
    project_types: ["bot_chat", "automation"],
    stack: ["Node.js", "Baileys", "Telegraf", "Supabase"],
    ai_tools: ["Claude"],
    pricing_models: ["budget_friendly"],
    hourly_rate: null,
    availability: "available",
    portfolio_url: null,
    links: { github: "https://github.com/morf" },
    is_verified: false,
    _whatsapp: "972505556677",
    _recency: 5,
  },
  {
    developer_id: "d6",
    full_name: "רון ביטון",
    title: "Senior Web Engineer",
    highlight: "מערכות web מורכבות עם קוד נקי וארכיטקטורה יציבה",
    bio: "מהנדס בכיר לבניית מערכות web בקנה מידה, עם דגש על אמינות, בדיקות ותחזוקתיות.",
    avatar_url: null,
    project_types: ["webapp", "saas"],
    stack: ["Vue", "Nuxt", "Node.js", "PostgreSQL"],
    ai_tools: ["Cursor"],
    pricing_models: ["hourly"],
    hourly_rate: 450,
    availability: "limited",
    portfolio_url: "https://ron.codes",
    links: { github: "https://github.com/ronb", linkedin: "https://linkedin.com/in/ronb" },
    is_verified: true,
    _whatsapp: "972506667788",
    _recency: 7,
  },
  {
    developer_id: "d7",
    full_name: "שירה גולן",
    title: "AI Engineer",
    highlight: "AI agents ו-RAG שמבינים את הביזנס שלך",
    bio: "בונה מערכות AI מבוססות agents ו-RAG, מחיבור מקורות מידע ועד ממשק משתמש.",
    avatar_url: null,
    project_types: ["ai_agents", "automation"],
    stack: ["Python", "LlamaIndex", "Claude", "Pinecone", "FastAPI"],
    ai_tools: ["Claude Code", "Claude"],
    pricing_models: ["after_scoping"],
    hourly_rate: null,
    availability: "available",
    portfolio_url: "https://shira.ai",
    links: { linkedin: "https://linkedin.com/in/shira" },
    is_verified: true,
    _whatsapp: "972507778899",
    _recency: 8,
  },
  {
    developer_id: "d8",
    full_name: "עידו רוזן",
    title: "Voice & Bots",
    highlight: "בוט קולי ומענה טלפוני חכם בעברית",
    bio: "מפתח מערכות קוליות ומענה טלפוני אוטומטי עם זיהוי דיבור והבנת שפה בעברית.",
    avatar_url: null,
    project_types: ["bot_voice", "bot_chat"],
    stack: ["Python", "Twilio", "LiveKit", "Whisper"],
    ai_tools: ["Claude"],
    pricing_models: ["budget_friendly", "after_scoping"],
    hourly_rate: null,
    availability: "available",
    portfolio_url: "https://ido-voice.dev",
    links: { github: "https://github.com/idor" },
    is_verified: false,
    _whatsapp: "972508889900",
    _recency: 6,
  },
];

// ---- פורט של מנוע הניקוד (engine.py) ----
const norm = (s: string) => (s || "").trim().toLowerCase();
const normSet = (items: string[] | null | undefined) =>
  new Set((items || []).map(norm).filter(Boolean));

function availabilityTimelineScore(availability: string, timeline: string | null): number {
  const a = norm(availability);
  const t = norm(timeline || "");
  if (a === "available") return t === "urgent" ? 20 : 18;
  if (a === "limited") {
    if (t === "flexible") return 14;
    if (t === "weeks") return 10;
    if (t === "urgent") return 5;
    return 10;
  }
  return 0;
}

function stackScore(pref: string[], devStack: string[] | null | undefined): [number, boolean] {
  const p = normSet(pref);
  if (p.size === 0) return [0, false];
  const d = normSet(devStack);
  let overlap = 0;
  p.forEach((x) => {
    if (d.has(x)) overlap += 1;
  });
  return [(overlap / p.size) * 30, true];
}

function scoreDeveloper(dev: DevProfile, body: MatchRequestBody): number {
  const [stackPts, stackActive] = stackScore(body.stack_pref || [], dev.stack);
  const availPts = availabilityTimelineScore(dev.availability, body.timeline);
  const activeMax = 50 + (stackActive ? 30 : 0) + 20;
  const base = ((50 + stackPts + availPts) / activeMax) * 100;
  const budget =
    (body.pricing_prefs || []).map(norm).includes("budget_friendly") &&
    normSet(dev.pricing_models).has("budget_friendly")
      ? 10
      : 0;
  return base + budget;
}

/** מזהה UUID קליל (לא קריפטוגרפי — מספיק לדמו). */
function fakeUuid(): string {
  const rand = () => Math.floor(Math.random() * 0x10000).toString(16).padStart(4, "0");
  return `${rand()}${rand()}-${rand()}-${rand()}-${rand()}-${rand()}${rand()}${rand()}`;
}

export async function getProjectTypes(): Promise<ProjectTypeMeta[]> {
  await delay(120);
  return CATEGORIES.map((c, i) => ({
    code: c.code,
    label_he: c.label,
    description_he: c.description,
    sort_order: i + 1,
  }));
}

export async function postMatch(body: MatchRequestBody): Promise<MatchResponse> {
  await delay(650);
  const wanted = norm(body.project_type);
  const passed = DEVELOPERS.filter((d) => {
    if (norm(d.availability) === "unavailable") return false;
    if (!normSet(d.project_types).has(wanted)) return false;
    if (body.portfolio_only && !(d.portfolio_url || "").trim()) return false;
    return true;
  });

  const scored = passed.map((d) => ({ dev: d, final: scoreDeveloper(d, body) }));
  scored.sort((a, b) => {
    if (b.final !== a.final) return b.final - a.final;
    if (a.dev.is_verified !== b.dev.is_verified) return a.dev.is_verified ? -1 : 1;
    const aAvail = norm(a.dev.availability) === "available";
    const bAvail = norm(b.dev.availability) === "available";
    if (aAvail !== bAvail) return aAvail ? -1 : 1;
    if (a.dev._recency !== b.dev._recency) return b.dev._recency - a.dev._recency;
    return a.dev.developer_id.localeCompare(b.dev.developer_id);
  });

  const results: MatchResultItem[] = scored.slice(0, 8).map(({ dev, final }) => {
    const { _whatsapp, _recency, ...rest } = dev;
    void _whatsapp;
    void _recency;
    return { ...rest, match_score: Math.round(Math.min(final, 100)) };
  });

  return { request_id: fakeUuid(), results };
}

export async function postReferral(
  requestId: string,
  developerId: string,
): Promise<ReferralResponse> {
  await delay(300);
  const dev = DEVELOPERS.find((d) => d.developer_id === developerId);
  const number = dev?._whatsapp ?? "972500000000";
  const text = encodeURIComponent(
    `היי! הגעתי דרך DevMatch. אני מחפש/ת מפתח/ת לפרויקט חדש.`,
  );
  void requestId;
  return { whatsapp_e164: number, wa_link: `https://wa.me/${number}?text=${text}` };
}

export async function postDeveloper(
  body: DeveloperCreateBody,
): Promise<DeveloperCreateResponse> {
  await delay(600);
  const { whatsapp_e164, ...rest } = body;
  void whatsapp_e164;
  return {
    id: fakeUuid(),
    is_verified: false,
    is_active: true,
    edit_token: `${fakeUuid()}${fakeUuid()}`,
    ...rest,
  };
}

export async function getDeveloper(id: string): Promise<DeveloperPublic> {
  await delay(250);
  const dev = DEVELOPERS.find((d) => d.developer_id === id);
  if (!dev) {
    throw new Error("המפתח לא נמצא");
  }
  return {
    id: dev.developer_id,
    full_name: dev.full_name,
    title: dev.title,
    bio: dev.bio,
    highlight: dev.highlight,
    avatar_url: dev.avatar_url,
    project_types: dev.project_types,
    stack: dev.stack ?? undefined,
    ai_tools: dev.ai_tools ?? undefined,
    pricing_models: dev.pricing_models,
    hourly_rate: dev.hourly_rate,
    availability: dev.availability,
    portfolio_url: dev.portfolio_url,
    links: dev.links,
    is_verified: dev.is_verified,
    is_active: true,
  };
}

export async function postAvatar(file: File): Promise<{ avatar_url: string }> {
  await delay(400);
  // בדמו — מחזירים data-URL מקומי כדי שהתצוגה המקדימה תעבוד בלי בקאנד
  const dataUrl = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error ?? new Error("קריאת הקובץ נכשלה"));
    reader.readAsDataURL(file);
  });
  return { avatar_url: dataUrl };
}
