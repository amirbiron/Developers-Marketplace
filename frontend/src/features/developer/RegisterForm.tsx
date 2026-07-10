import { Ban, CircleCheck, CircleDot, ImagePlus, Loader2, Lock, type LucideIcon } from "lucide-react";
import { type ReactNode, useRef, useState } from "react";
import { Avatar } from "@/components/ui/Avatar";
import { Button } from "@/components/ui/Button";
import { Field, Input, Textarea } from "@/components/ui/Field";
import { OptionCard } from "@/components/ui/OptionCard";
import { TagInput } from "@/components/ui/TagInput";
import { postAvatar, postDeveloper } from "@/lib/api";
import { AVAILABILITY_LABELS, CATEGORIES, PRICING_LABELS } from "@/lib/labels";
import type { Availability, DeveloperCreateBody, DeveloperPublic, PricingModel } from "@/lib/types";
import { RegisterSuccess } from "./RegisterSuccess";

const STACK_SUGGESTIONS = [
  "React", "Next.js", "Vue", "React Native", "Node.js", "Python", "FastAPI",
  "Supabase", "PostgreSQL", "TypeScript", "Tailwind", "Docker",
];
const AI_SUGGESTIONS = ["Claude Code", "Claude", "Cursor", "Copilot", "Windsurf"];

const AVAILABILITY_OPTIONS: { code: Availability; icon: LucideIcon; hint: string }[] = [
  { code: "available", icon: CircleCheck, hint: "פנוי לקחת פרויקטים" },
  { code: "limited", icon: CircleDot, hint: "יש מקום למעט" },
  { code: "unavailable", icon: Ban, hint: "לא פנוי — לא תופיע בחיפושים" },
];

interface FormState {
  full_name: string;
  title: string;
  bio: string;
  highlight: string;
  avatar_url: string;
  project_types: string[];
  stack: string[];
  ai_tools: string[];
  pricing_models: string[];
  hourly_rate: string;
  availability: string;
  portfolio_url: string;
  linkedin: string;
  github: string;
  whatsapp: string;
}

const INITIAL: FormState = {
  full_name: "", title: "", bio: "", highlight: "", avatar_url: "",
  project_types: [], stack: [], ai_tools: [], pricing_models: [], hourly_rate: "",
  availability: "", portfolio_url: "", linkedin: "", github: "", whatsapp: "",
};

function Section({
  index,
  title,
  description,
  emphasis,
  children,
}: {
  index: number;
  title: string;
  description?: string;
  emphasis?: boolean;
  children: ReactNode;
}) {
  return (
    <section className="panel p-5 sm:p-6">
      <div className="mb-4 flex items-start gap-3">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-line bg-surface2 font-mono text-xs text-accent-bright">
          {index}
        </span>
        <div>
          <h2 className="font-semibold text-ink">
            {title}
            {emphasis && <span className="ms-2 text-xs text-accent-bright">· מומלץ מאוד</span>}
          </h2>
          {description && <p className="mt-0.5 text-sm text-muted">{description}</p>}
        </div>
      </div>
      {children}
    </section>
  );
}

export function RegisterForm() {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [errors, setErrors] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [created, setCreated] = useState<DeveloperPublic | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const toggleArray = (key: "project_types" | "pricing_models", value: string) =>
    setForm((f) => {
      const has = f[key].includes(value);
      return { ...f, [key]: has ? f[key].filter((v) => v !== value) : [...f[key], value] };
    });

  const normalizeWhatsapp = (raw: string) => raw.replace(/[\s\-()]/g, "").replace(/^\+/, "");

  const onAvatarPick = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      setErrors(["התמונה גדולה מדי — מקסימום 5MB"]);
      if (fileRef.current) fileRef.current.value = "";
      return;
    }
    setAvatarLoading(true);
    setErrors([]);
    try {
      const res = await postAvatar(file);
      set("avatar_url", res.avatar_url);
    } catch (err) {
      setErrors([err instanceof Error ? err.message : "העלאת התמונה נכשלה"]);
    } finally {
      setAvatarLoading(false);
    }
  };

  const validate = (): string[] => {
    const e: string[] = [];
    if (!form.full_name.trim()) e.push("שם מלא הוא שדה חובה");
    if (form.project_types.length === 0) e.push("בחר לפחות סוג פרויקט אחד");
    if (form.pricing_models.length === 0) e.push("בחר לפחות מודל תמחור אחד");
    if (!form.availability) e.push("בחר זמינות");
    const phone = normalizeWhatsapp(form.whatsapp);
    if (!/^[1-9]\d{7,14}$/.test(phone)) e.push("מספר וואטסאפ לא תקין (E.164, למשל 972501234567)");
    if (
      form.pricing_models.includes("hourly") &&
      form.hourly_rate &&
      !(Number(form.hourly_rate) > 0)
    )
      e.push("תעריף שעתי חייב להיות מספר חיובי");
    return e;
  };

  const submit = async () => {
    const found = validate();
    if (found.length > 0) {
      setErrors(found);
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    setErrors([]);
    setSubmitting(true);
    const links: Record<string, string> = {};
    if (form.linkedin.trim()) links.linkedin = form.linkedin.trim();
    if (form.github.trim()) links.github = form.github.trim();
    const phone = normalizeWhatsapp(form.whatsapp);

    const body: DeveloperCreateBody = {
      full_name: form.full_name.trim(),
      title: form.title.trim() || null,
      bio: form.bio.trim() || null,
      highlight: form.highlight.trim() || null,
      avatar_url: form.avatar_url || null,
      whatsapp_e164: phone,
      project_types: form.project_types,
      stack: form.stack,
      ai_tools: form.ai_tools,
      pricing_models: form.pricing_models,
      hourly_rate:
        form.pricing_models.includes("hourly") && form.hourly_rate
          ? Number(form.hourly_rate)
          : null,
      availability: form.availability,
      portfolio_url: form.portfolio_url.trim() || null,
      links: Object.keys(links).length ? links : null,
    };

    try {
      const dev = await postDeveloper(body);
      setCreated(dev);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setErrors([err instanceof Error ? err.message : "ההרשמה נכשלה. נסו שוב."]);
    } finally {
      setSubmitting(false);
    }
  };

  if (created) {
    return <RegisterSuccess dev={created} onEdit={() => setCreated(null)} />;
  }

  const showHourly = form.pricing_models.includes("hourly");

  return (
    <div className="container-app max-w-2xl py-10">
      <div className="mb-8">
        <p className="font-mono text-xs text-accent-bright">// הצטרפות כמפתח/ת</p>
        <h1 className="mt-1 text-2xl font-bold text-ink sm:text-3xl">בוא נבנה לך פרופיל</h1>
        <p className="mt-1 text-sm text-muted">
          הפרופיל עולה מיד וניתן להתאמה — בלי המתנה לאישור. תג "מאומת" מתווסף בהמשך.
        </p>
      </div>

      {errors.length > 0 && (
        <div className="mb-6 rounded-xl border border-syntax-rose/40 bg-syntax-rose/10 p-4">
          <ul className="list-inside list-disc space-y-1 text-sm text-syntax-rose">
            {errors.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid gap-4">
        {/* 1. פרטים בסיסיים */}
        <Section index={1} title="פרטים בסיסיים">
          <div className="grid gap-4">
            <div className="flex items-center gap-4">
              <Avatar name={form.full_name || "מ פ"} src={form.avatar_url || null} size={64} />
              <div>
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  className="hidden"
                  onChange={onAvatarPick}
                />
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => fileRef.current?.click()}
                  disabled={avatarLoading}
                >
                  {avatarLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <ImagePlus className="h-4 w-4" />
                  )}
                  העלאת תמונה
                </Button>
                <p className="mt-1.5 text-xs text-faint">PNG / JPEG / WebP, עד 5MB</p>
              </div>
            </div>
            <Field label="שם מלא" required>
              <Input
                value={form.full_name}
                onChange={(e) => set("full_name", e.target.value)}
                placeholder="ישראל ישראלי"
              />
            </Field>
            <Field label="תפקיד" hint="למשל: Full-stack, ייעוץ מוצר">
              <Input
                value={form.title}
                onChange={(e) => set("title", e.target.value)}
                placeholder="Full-stack Developer"
              />
            </Field>
            <Field label="משפט בידול (highlight)" hint="במה אתה טוב במיוחד — משפט חד שמבדל אותך">
              <Input
                value={form.highlight}
                onChange={(e) => set("highlight", e.target.value)}
                maxLength={280}
                placeholder="בונה SaaS עם billing מהיום הראשון"
              />
            </Field>
            <Field label="על עצמך (bio)">
              <Textarea
                value={form.bio}
                onChange={(e) => set("bio", e.target.value)}
                maxLength={600}
                placeholder="קצת רקע, ניסיון, וסוג הפרויקטים שאתה אוהב לבנות…"
              />
            </Field>
          </div>
        </Section>

        {/* 2. סוגי פרויקט */}
        <Section
          index={2}
          title="סוגי פרויקט"
          description="בחר את כל מה שאתה בונה — זו ההתמחות שלפיה לקוחות ימצאו אותך. בלי תקרה."
          emphasis
        >
          <div className="grid gap-2.5 sm:grid-cols-2">
            {CATEGORIES.map((c) => (
              <OptionCard
                key={c.code}
                multi
                selected={form.project_types.includes(c.code)}
                onClick={() => toggleArray("project_types", c.code)}
                icon={c.Icon}
                iconTint={c.tint}
                label={c.label}
              />
            ))}
          </div>
        </Section>

        {/* 3. טכנולוגיות */}
        <Section index={3} title="טכנולוגיות וכלים">
          <div className="grid gap-4">
            <Field label="Stack" hint="נכנס למנוע ההתאמה — הוסף את מה שאתה עובד איתו">
              <TagInput
                value={form.stack}
                onChange={(v) => set("stack", v)}
                placeholder="React, FastAPI…"
                suggestions={STACK_SUGGESTIONS}
              />
            </Field>
            <Field label="כלי AI" hint="לתצוגה בלבד — נחמד לראות">
              <TagInput
                value={form.ai_tools}
                onChange={(v) => set("ai_tools", v)}
                placeholder="Claude Code, Cursor…"
                suggestions={AI_SUGGESTIONS}
              />
            </Field>
          </div>
        </Section>

        {/* 4. תמחור */}
        <Section index={4} title="מודל תמחור" description="אפשר לבחור כמה">
          <div className="grid gap-2.5">
            {(["hourly", "after_scoping", "budget_friendly"] as PricingModel[]).map((code) => (
              <OptionCard
                key={code}
                multi
                selected={form.pricing_models.includes(code)}
                onClick={() => toggleArray("pricing_models", code)}
                label={PRICING_LABELS[code].label}
                description={PRICING_LABELS[code].hint}
              />
            ))}
            {showHourly && (
              <div className="mt-1">
                <Field label="תעריף שעתי (₪)" hint="מוצג ללקוח על הכרטיס">
                  <Input
                    type="number"
                    inputMode="numeric"
                    value={form.hourly_rate}
                    onChange={(e) => set("hourly_rate", e.target.value)}
                    placeholder="350"
                  />
                </Field>
              </div>
            )}
          </div>
        </Section>

        {/* 5. זמינות */}
        <Section index={5} title="זמינות">
          <div className="grid gap-2.5 sm:grid-cols-3">
            {AVAILABILITY_OPTIONS.map(({ code, icon, hint }) => (
              <OptionCard
                key={code}
                selected={form.availability === code}
                onClick={() => set("availability", code)}
                icon={icon}
                label={AVAILABILITY_LABELS[code]}
                description={hint}
              />
            ))}
          </div>
        </Section>

        {/* 6. פורטפוליו וקישורים */}
        <Section
          index={6}
          title="פורטפוליו וקישורים"
          description="תיק עבודות קריטי בבנייה מאפס — בלעדיו לא תופיע ללקוחות שסיננו לפי תיק עבודות."
          emphasis
        >
          <div className="grid gap-4">
            <Field label="קישור לפורטפוליו">
              <Input
                dir="ltr"
                value={form.portfolio_url}
                onChange={(e) => set("portfolio_url", e.target.value)}
                placeholder="https://myportfolio.dev"
              />
            </Field>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="LinkedIn">
                <Input
                  dir="ltr"
                  value={form.linkedin}
                  onChange={(e) => set("linkedin", e.target.value)}
                  placeholder="https://linkedin.com/in/…"
                />
              </Field>
              <Field label="GitHub">
                <Input
                  dir="ltr"
                  value={form.github}
                  onChange={(e) => set("github", e.target.value)}
                  placeholder="https://github.com/…"
                />
              </Field>
            </div>
          </div>
        </Section>

        {/* 7. וואטסאפ */}
        <Section index={7} title="וואטסאפ ליצירת קשר">
          <Field label="מספר וואטסאפ" required>
            <Input
              dir="ltr"
              value={form.whatsapp}
              onChange={(e) => set("whatsapp", e.target.value)}
              placeholder="972501234567"
            />
          </Field>
          <div className="mt-3 flex items-start gap-2 rounded-xl border border-line bg-surface2 p-3">
            <Lock className="mt-0.5 h-4 w-4 shrink-0 text-accent-bright" />
            <p className="text-xs text-muted">
              המספר <span className="font-medium text-ink">לא מוצג בפומבי</span>. הוא נחשף רק
              כשלקוח לוחץ "פנה בוואטסאפ" — וגם אז הפנייה נרשמת.
            </p>
          </div>
        </Section>

        <Button onClick={submit} loading={submitting} size="lg" className="mt-2 w-full">
          פרסם את הפרופיל
        </Button>
      </div>
    </div>
  );
}
