import { cn } from "@/lib/cn";

interface ToggleProps {
  checked: boolean;
  onChange: (value: boolean) => void;
  label?: string;
  hint?: string;
}

export function Toggle({ checked, onChange, label, hint }: ToggleProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={cn(
        "flex w-full items-center justify-between gap-4 rounded-2xl border p-4 text-right transition-colors",
        checked ? "border-accent/50 bg-accent/[0.06]" : "border-line bg-surface hover:border-line-strong",
      )}
    >
      <span>
        {label && <span className="block font-medium text-ink">{label}</span>}
        {hint && <span className="mt-0.5 block text-sm text-muted">{hint}</span>}
      </span>
      {/* המתג עצמו קורא LTR — סטנדרטי לפקד toggle גם בעמוד RTL */}
      <span
        dir="ltr"
        className={cn(
          "relative inline-block h-6 w-11 shrink-0 rounded-full transition-colors",
          checked ? "bg-accent" : "bg-line-strong",
        )}
      >
        <span
          className={cn(
            "absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200",
            checked ? "translate-x-5" : "translate-x-0",
          )}
        />
      </span>
    </button>
  );
}
