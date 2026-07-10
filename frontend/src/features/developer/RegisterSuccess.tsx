import { CheckCircle2, Lock, ShieldQuestion } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import type { DeveloperPublic } from "@/lib/types";

export function RegisterSuccess({ dev, onEdit }: { dev: DeveloperPublic; onEdit: () => void }) {
  return (
    <div className="container-app max-w-xl py-16">
      <div className="panel flex flex-col items-center gap-5 p-8 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-accent/40 bg-accent/10 shadow-glow">
          <CheckCircle2 className="h-8 w-8 text-accent-bright" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-ink">הפרופיל שלך חי! 🎉</h1>
          <p className="mt-2 text-sm leading-relaxed text-muted">
            {dev.full_name}, הפרופיל שלך כבר ניתן להתאמה. לקוחות שיחפשו את מה שאתה בונה יראו
            אותך מיד.
          </p>
        </div>

        <div className="flex w-full items-start gap-3 rounded-xl border border-line bg-surface2 p-4 text-right">
          <ShieldQuestion className="mt-0.5 h-5 w-5 shrink-0 text-muted" />
          <p className="text-sm text-muted">
            תג <span className="font-medium text-accent-bright">"מאומת"</span> יתווסף בהמשך
            אחרי בדיקה קצרה — הוא דוחף אותך למעלה בתוצאות, אבל אתה כבר פעיל בלעדיו.
          </p>
        </div>

        <div className="flex w-full items-start gap-3 rounded-xl border border-line bg-surface2 p-4 text-right">
          <Lock className="mt-0.5 h-5 w-5 shrink-0 text-accent-bright" />
          <p className="text-sm text-muted">
            שמרנו במכשיר זה <span className="font-medium text-ink">קוד עריכה מאובטח</span> — כך
            רק אתה תוכל לעדכן את הפרופיל בהמשך.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-2">
          <Link to="/">
            <Button variant="secondary">חזרה לדף הבית</Button>
          </Link>
          <Button variant="ghost" onClick={onEdit}>
            עריכת הפרטים
          </Button>
        </div>
      </div>
    </div>
  );
}
