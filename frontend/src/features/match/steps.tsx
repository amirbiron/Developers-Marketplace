import {
  CalendarClock,
  Clock,
  Code2,
  Coins,
  FileText,
  Hourglass,
  type LucideIcon,
  Rocket,
  Users,
  Zap,
} from "lucide-react";
import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { Field, Textarea } from "@/components/ui/Field";
import { OptionCard } from "@/components/ui/OptionCard";
import { TagInput } from "@/components/ui/TagInput";
import { Toggle } from "@/components/ui/Toggle";
import { cn } from "@/lib/cn";
import { CATEGORIES, INVOLVEMENT_LABELS, PRICING_LABELS, TIMELINE_LABELS } from "@/lib/labels";
import type { Involvement, MatchAnswers, PricingModel, Timeline } from "@/lib/types";

interface StepProps {
  answers: MatchAnswers;
  update: (patch: Partial<MatchAnswers>) => void;
}

const STACK_SUGGESTIONS = [
  "React",
  "Next.js",
  "Vue",
  "React Native",
  "Node.js",
  "Python",
  "FastAPI",
  "Supabase",
  "PostgreSQL",
  "Firebase",
];

export function StepProjectType({ answers, update }: StepProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {CATEGORIES.map((c) => (
        <OptionCard
          key={c.code}
          selected={answers.project_type === c.code}
          onClick={() => update({ project_type: c.code })}
          icon={c.Icon}
          iconTint={c.tint}
          label={c.label}
          description={c.description}
        />
      ))}
    </div>
  );
}

export function StepPricing({ answers, update }: StepProps) {
  const toggle = (m: PricingModel) => {
    const has = answers.pricing_prefs.includes(m);
    update({
      pricing_prefs: has
        ? answers.pricing_prefs.filter((x) => x !== m)
        : [...answers.pricing_prefs, m],
    });
  };
  const items: { code: PricingModel; icon: LucideIcon }[] = [
    { code: "hourly", icon: Clock },
    { code: "after_scoping", icon: FileText },
    { code: "budget_friendly", icon: Coins },
  ];
  return (
    <div className="grid gap-3">
      {items.map(({ code, icon }) => (
        <OptionCard
          key={code}
          multi
          selected={answers.pricing_prefs.includes(code)}
          onClick={() => toggle(code)}
          icon={icon}
          label={PRICING_LABELS[code].label}
          description={PRICING_LABELS[code].hint}
        />
      ))}
      <p className="text-center text-xs text-faint">אפשר לבחור כמה, או לדלג</p>
    </div>
  );
}

export function StepTimeline({ answers, update }: StepProps) {
  const items: { code: Timeline; icon: LucideIcon }[] = [
    { code: "urgent", icon: Zap },
    { code: "weeks", icon: CalendarClock },
    { code: "flexible", icon: Hourglass },
  ];
  return (
    <div className="grid gap-3">
      {items.map(({ code, icon }) => (
        <OptionCard
          key={code}
          selected={answers.timeline === code}
          onClick={() => update({ timeline: code })}
          icon={icon}
          label={TIMELINE_LABELS[code].label}
          description={TIMELINE_LABELS[code].hint}
        />
      ))}
    </div>
  );
}

export function StepInvolvement({ answers, update }: StepProps) {
  const items: { code: Involvement; icon: LucideIcon }[] = [
    { code: "full_handoff", icon: Rocket },
    { code: "collaborative", icon: Users },
  ];
  return (
    <div className="grid gap-3">
      {items.map(({ code, icon }) => (
        <OptionCard
          key={code}
          selected={answers.involvement === code}
          onClick={() => update({ involvement: code })}
          icon={icon}
          label={INVOLVEMENT_LABELS[code].label}
          description={INVOLVEMENT_LABELS[code].hint}
        />
      ))}
      <p className="text-center text-xs text-faint">מטא-דאטה לפנייה — עוזר למפתח להתכונן</p>
    </div>
  );
}

export function StepDescription({ answers, update }: StepProps) {
  const [showAdvanced, setShowAdvanced] = useState(answers.stack_pref.length > 0);
  return (
    <div className="grid gap-4">
      <Field label="תיאור קצר של הפרויקט" hint="לא חובה — יעזור למפתח להבין למה אתה צריך">
        <Textarea
          value={answers.description}
          onChange={(e) => update({ description: e.target.value })}
          maxLength={1000}
          placeholder="למשל: מערכת ניהול לקוחות עם דשבורד, התחברות, והתראות במייל…"
        />
      </Field>

      <Toggle
        checked={answers.portfolio_only}
        onChange={(v) => update({ portfolio_only: v })}
        label="הצג רק מפתחים עם תיק עבודות"
        hint="קריטי בבנייה מאפס — לראות עבודות קודמות"
      />

      <div>
        <button
          type="button"
          onClick={() => setShowAdvanced((s) => !s)}
          className="flex items-center gap-2 font-mono text-xs text-muted transition-colors hover:text-accent-bright"
        >
          <Code2 className="h-3.5 w-3.5" />
          טכנולוגיות מועדפות (מתקדם)
          <ChevronDown
            className={cn("h-3.5 w-3.5 transition-transform", showAdvanced && "rotate-180")}
          />
        </button>
        {showAdvanced && (
          <div className="mt-3">
            <TagInput
              value={answers.stack_pref}
              onChange={(v) => update({ stack_pref: v })}
              placeholder="React, Supabase… (Enter להוספה)"
              suggestions={STACK_SUGGESTIONS}
            />
            <p className="mt-1.5 text-xs text-faint">
              אם תציין — נשקלל התאמת stack. אם לא — ההתאמה תתבסס על מה שחשוב לך.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
