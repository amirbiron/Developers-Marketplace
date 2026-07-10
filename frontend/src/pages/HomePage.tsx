import { motion } from "framer-motion";
import { ArrowLeft, ClipboardList, type LucideIcon, Search, Sparkles, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/cn";
import { CATEGORIES } from "@/lib/labels";

const HOW: { icon: LucideIcon; title: string; text: string }[] = [
  {
    icon: ClipboardList,
    title: "עונים על 5 שאלות",
    text: 'מה בונים, תמחור, לו"ז, מעורבות, ותיאור קצר. בלי הרשמה ובלי פרטים מראש.',
  },
  {
    icon: Sparkles,
    title: "מקבלים רשימה ממוקדת",
    text: "מנוע דטרמיניסטי מדרג התאמה ומחזיר 5–8 מפתחים מתאימים — לא רשימה אינסופית.",
  },
  {
    icon: Zap,
    title: "פונים ישירות בוואטסאפ",
    text: "לחיצה אחת פותחת צ'אט עם הודעה מוכנה. בלי תיווך, בלי עמלות, בלי מתווכים.",
  },
];

export function HomePage() {
  return (
    <div>
      {/* HERO */}
      <section className="container-app pb-16 pt-16 sm:pt-24">
        <div className="mx-auto max-w-3xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3 py-1 font-mono text-xs text-muted">
              <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse-glow" />
              rule-based · דטרמיניסטי · בלי תיווך
            </span>
            <h1 className="mt-6 text-4xl font-extrabold leading-tight text-ink sm:text-6xl">
              מצא את המפתח
              <br />
              ש<span className="text-gradient">יבנה לך את זה</span>
            </h1>
            <p className="mx-auto mt-5 max-w-xl text-lg leading-relaxed text-muted">
              5 שאלות, ורשימה קצרה של מפתחים ישראלים שמתאימים בדיוק למה שאתה צריך — כל אחד עם
              ציון התאמה ופנייה ישירה בוואטסאפ.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Link to="/match">
                <Button size="lg">
                  <Search className="h-4 w-4" />
                  מצא מפתח
                  <ArrowLeft className="h-4 w-4" />
                </Button>
              </Link>
              <Link to="/join">
                <Button size="lg" variant="secondary">
                  אני מפתח/ת
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* terminal card */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="mx-auto mt-14 max-w-lg overflow-hidden rounded-2xl border border-line bg-surface2/80 shadow-card backdrop-blur"
          >
            <div className="flex items-center gap-1.5 border-b border-line px-4 py-2.5">
              <span className="h-2.5 w-2.5 rounded-full bg-syntax-rose/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-syntax-amber/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-accent/70" />
              <span className="ms-2 font-mono text-xs text-faint">devmatch — zsh</span>
            </div>
            <div dir="ltr" className="space-y-1.5 p-5 text-left font-mono text-sm">
              <p className="text-muted">
                <span className="text-accent-bright">$</span> devmatch find --type=saas
                --timeline=weeks
              </p>
              <p className="text-faint">→ scanning developers…</p>
              <p className="text-ink">✓ 6 matches · sorted by fit</p>
              <p className="text-accent-bright">
                → top: Yael A. · 96% · available
                <span className="ms-1 inline-block h-3.5 w-2 translate-y-0.5 bg-accent-bright animate-blink" />
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="container-app py-8">
        <p className="mb-6 text-center font-mono text-xs text-faint">// איך זה עובד</p>
        <div className="grid gap-4 md:grid-cols-3">
          {HOW.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="panel p-6"
            >
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl border border-accent/30 bg-accent/10">
                <step.icon className="h-5 w-5 text-accent-bright" />
              </div>
              <div className="mb-1 flex items-center gap-2">
                <span className="font-mono text-xs text-faint">0{i + 1}</span>
                <h3 className="font-semibold text-ink">{step.title}</h3>
              </div>
              <p className="text-sm leading-relaxed text-muted">{step.text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CATEGORIES */}
      <section className="container-app py-10">
        <p className="mb-5 text-center font-mono text-xs text-faint">
          // 10 קטגוריות — בחר את הציר שלך
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {CATEGORIES.map((c) => (
            <span
              key={c.code}
              className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-3 py-1.5 text-sm text-muted transition-colors hover:border-line-strong hover:text-ink"
            >
              <c.Icon className={cn("h-3.5 w-3.5", c.tint)} />
              {c.label}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}
