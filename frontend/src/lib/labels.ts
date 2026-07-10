// תוויות עברית + אייקונים לכל ה-enums. הטקסטים תואמים ל-app/constants.py.

import {
  Bot,
  Boxes,
  Globe,
  LayoutDashboard,
  type LucideIcon,
  PhoneCall,
  Shapes,
  ShoppingBag,
  Smartphone,
  Sparkles,
  Workflow,
} from "lucide-react";
import type {
  Availability,
  Involvement,
  PricingModel,
  ProjectTypeCode,
  Timeline,
} from "./types";

export interface CategoryMeta {
  code: ProjectTypeCode;
  label: string;
  description: string;
  Icon: LucideIcon;
  tint: string; // צבע סינטקס לאייקון (גיוון ויזואלי)
}

/** 10 קטגוריות סוג-פרויקט — התיאורים חשובים כי אין חפיפה חלקית (Spec §1). */
export const CATEGORIES: CategoryMeta[] = [
  {
    code: "landing",
    label: "אתר תדמית",
    description: "דף נחיתה / נוכחות דיגיטלית — בלי משתמשים או התחברות.",
    Icon: Globe,
    tint: "text-syntax-cyan",
  },
  {
    code: "store",
    label: "חנות אונליין",
    description: "קטלוג מוצרים, עגלת קניות ותשלום.",
    Icon: ShoppingBag,
    tint: "text-syntax-amber",
  },
  {
    code: "mobile",
    label: "אפליקציית מובייל",
    description: "אפליקציה טבעית לאנדרואיד / iOS.",
    Icon: Smartphone,
    tint: "text-accent-bright",
  },
  {
    code: "webapp",
    label: "Web App",
    description: "מערכת עם משתמשים והתחברות — בלי מנוי חוזר.",
    Icon: LayoutDashboard,
    tint: "text-syntax-violet",
  },
  {
    code: "saas",
    label: "מערכת SaaS",
    description: "מערכת עם מנוי ותשלום חוזר.",
    Icon: Boxes,
    tint: "text-syntax-cyan",
  },
  {
    code: "automation",
    label: "אוטומציה ואינטגרציות",
    description: "חיבור בין מערכות, אוטומציות ו-APIs.",
    Icon: Workflow,
    tint: "text-accent-bright",
  },
  {
    code: "bot_chat",
    label: "בוט צ'אט",
    description: "בוט טקסט ל-WhatsApp / Telegram.",
    Icon: Bot,
    tint: "text-syntax-amber",
  },
  {
    code: "bot_voice",
    label: "בוט קולי",
    description: "מענה טלפוני אוטומטי / בוט קולי.",
    Icon: PhoneCall,
    tint: "text-syntax-rose",
  },
  {
    code: "ai_agents",
    label: "AI ואייג'נטים",
    description: "פתרונות מבוססי AI ואייג'נטים חכמים.",
    Icon: Sparkles,
    tint: "text-syntax-violet",
  },
  {
    code: "other",
    label: "אחר",
    description: "משהו אחר שלא נכנס לקטגוריות שלמעלה.",
    Icon: Shapes,
    tint: "text-muted",
  },
];

export const CATEGORY_BY_CODE: Record<string, CategoryMeta> = Object.fromEntries(
  CATEGORIES.map((c) => [c.code, c]),
);

export const PRICING_LABELS: Record<PricingModel, { label: string; hint: string }> = {
  hourly: { label: "לפי שעה", hint: "תעריף שעתי קבוע" },
  after_scoping: { label: "הצעת מחיר אחרי אפיון", hint: "מחיר סופי אחרי הבנת הפרויקט" },
  budget_friendly: { label: "תקציב נוח", hint: "פתרונות מותאמי תקציב" },
};

export const TIMELINE_LABELS: Record<Timeline, { label: string; hint: string }> = {
  urgent: { label: "דחוף", hint: "צריך להתחיל עכשיו" },
  weeks: { label: "כמה שבועות", hint: "יש זמן סביר" },
  flexible: { label: "גמיש", hint: "אין לחץ זמן" },
};

export const INVOLVEMENT_LABELS: Record<Involvement, { label: string; hint: string }> = {
  full_handoff: { label: "מסירה מלאה", hint: "שיבנו לי מקצה לקצה" },
  collaborative: { label: "עבודה משותפת", hint: "רוצה להיות מעורב בתהליך" },
};

export const AVAILABILITY_LABELS: Record<Availability, string> = {
  available: "פנוי",
  limited: "זמינות מוגבלת",
  unavailable: "לא פנוי",
};
