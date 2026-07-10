import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

type Tone = "neutral" | "accent" | "available" | "limited" | "muted";

const TONES: Record<Tone, string> = {
  neutral: "border-line bg-surface2 text-muted",
  accent: "border-accent/40 bg-accent/10 text-accent-bright",
  available: "border-accent/40 bg-accent/10 text-accent-bright",
  limited: "border-syntax-amber/40 bg-syntax-amber/10 text-syntax-amber",
  muted: "border-line bg-surface2 text-faint",
};

interface BadgeProps {
  tone?: Tone;
  icon?: LucideIcon;
  children: ReactNode;
  className?: string;
}

export function Badge({ tone = "neutral", icon: Icon, children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        TONES[tone],
        className,
      )}
    >
      {Icon && <Icon className="h-3 w-3" />}
      {children}
    </span>
  );
}
