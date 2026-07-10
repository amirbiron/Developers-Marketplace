import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { type ComponentType, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { Stepper } from "@/components/ui/Stepper";
import { postMatch } from "@/lib/api";
import { CATEGORY_BY_CODE } from "@/lib/labels";
import type { MatchAnswers, MatchResponse } from "@/lib/types";
import { ResultsView } from "./ResultsView";
import {
  StepDescription,
  StepInvolvement,
  StepPricing,
  StepProjectType,
  StepTimeline,
} from "./steps";

const EMPTY_ANSWERS: MatchAnswers = {
  project_type: null,
  pricing_prefs: [],
  timeline: null,
  involvement: null,
  portfolio_only: false,
  description: "",
  stack_pref: [],
};

interface StepDef {
  title: string;
  subtitle: string;
  Comp: ComponentType<{ answers: MatchAnswers; update: (patch: Partial<MatchAnswers>) => void }>;
}

const STEPS: StepDef[] = [
  {
    title: "מה בונים?",
    subtitle: "סוג הפרויקט הוא הציר המרכזי של ההתאמה",
    Comp: StepProjectType,
  },
  { title: "תמחור", subtitle: "איך היית רוצה להתמחר? אפשר לבחור כמה", Comp: StepPricing },
  { title: "לוח זמנים", subtitle: "כמה דחוף הפרויקט?", Comp: StepTimeline },
  { title: "מעורבות", subtitle: "כמה תרצה להיות מעורב בתהליך?", Comp: StepInvolvement },
  { title: "פרטים אחרונים", subtitle: "עוד קצת הקשר, והכול מוכן", Comp: StepDescription },
];

export function MatchFlow() {
  const [answers, setAnswers] = useState<MatchAnswers>(EMPTY_ANSWERS);
  const [step, setStep] = useState(0);
  const [phase, setPhase] = useState<"form" | "loading" | "results">("form");
  const [results, setResults] = useState<MatchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const update = (patch: Partial<MatchAnswers>) => setAnswers((a) => ({ ...a, ...patch }));

  const stepValid = () => {
    if (step === 0) return answers.project_type !== null;
    if (step === 2) return answers.timeline !== null;
    return true;
  };
  const canSubmit = answers.project_type !== null && answers.timeline !== null;
  const isLast = step === STEPS.length - 1;

  const submit = async () => {
    if (!canSubmit) return;
    setPhase("loading");
    setError(null);
    try {
      const res = await postMatch({
        project_type: answers.project_type as string,
        pricing_prefs: answers.pricing_prefs,
        timeline: answers.timeline as string,
        involvement: answers.involvement,
        portfolio_only: answers.portfolio_only,
        description: answers.description || null,
        stack_pref: answers.stack_pref,
      });
      setResults(res);
      setPhase("results");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError(e instanceof Error ? e.message : "ההתאמה נכשלה. נסו שוב.");
      setPhase("form");
    }
  };

  const reset = () => {
    setAnswers(EMPTY_ANSWERS);
    setStep(0);
    setResults(null);
    setError(null);
    setPhase("form");
  };

  if (phase === "results" && results) {
    return (
      <ResultsView
        data={results}
        projectTypeLabel={CATEGORY_BY_CODE[answers.project_type ?? ""]?.label ?? ""}
        onReset={reset}
      />
    );
  }

  const { title, subtitle, Comp } = STEPS[step];

  return (
    <div className="container-app max-w-2xl py-10">
      <div className="mb-8">
        <Stepper steps={STEPS.map((s) => s.title)} current={step} />
      </div>

      <div className="mb-6">
        <p dir="ltr" className="text-right font-mono text-xs text-accent-bright">
          [ {step + 1} / {STEPS.length} ]
        </p>
        <h1 className="mt-1 text-2xl font-bold text-ink sm:text-3xl">{title}</h1>
        <p className="mt-1 text-sm text-muted">{subtitle}</p>
      </div>

      {phase === "loading" ? (
        <div className="flex flex-col items-center gap-3 py-20">
          <Spinner className="h-8 w-8" />
          <p className="font-mono text-sm text-muted">מריץ התאמה…</p>
        </div>
      ) : (
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
            transition={{ duration: 0.25 }}
          >
            <Comp answers={answers} update={update} />
          </motion.div>
        </AnimatePresence>
      )}

      {error && <p className="mt-4 text-center text-sm text-syntax-rose">{error}</p>}

      <div className="mt-8 flex items-center justify-between gap-3">
        <Button
          variant="ghost"
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={step === 0 || phase === "loading"}
        >
          <ArrowRight className="h-4 w-4" />
          חזרה
        </Button>
        {isLast ? (
          <Button onClick={submit} loading={phase === "loading"} disabled={!canSubmit}>
            מצא מפתחים
          </Button>
        ) : (
          <Button onClick={() => setStep((s) => s + 1)} disabled={!stepValid()}>
            הבא
            <ArrowLeft className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
