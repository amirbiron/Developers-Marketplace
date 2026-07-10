import { Check, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/cn";

interface OptionCardProps {
  selected: boolean;
  onClick: () => void;
  label: string;
  description?: string;
  icon?: LucideIcon;
  iconTint?: string;
  multi?: boolean;
}

export function OptionCard({
  selected,
  onClick,
  label,
  description,
  icon: Icon,
  iconTint,
  multi = false,
}: OptionCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={selected}
      className={cn(
        "group flex w-full items-start gap-3 rounded-2xl border p-4 text-right transition-all duration-200",
        selected
          ? "border-accent/60 bg-accent/[0.07] shadow-glow-sm"
          : "border-line bg-surface hover:border-line-strong hover:bg-elevated",
      )}
    >
      {Icon && (
        <span
          className={cn(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border bg-surface2 transition-colors",
            selected ? "border-accent/40" : "border-line",
          )}
        >
          <Icon className={cn("h-5 w-5", selected ? "text-accent-bright" : (iconTint ?? "text-muted"))} />
        </span>
      )}

      <span className="flex-1">
        <span className="block font-semibold text-ink">{label}</span>
        {description && <span className="mt-0.5 block text-sm leading-relaxed text-muted">{description}</span>}
      </span>

      <span
        className={cn(
          "mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center border transition-colors",
          multi ? "rounded-md" : "rounded-full",
          selected ? "border-accent bg-accent text-[#052e22]" : "border-line-strong text-transparent",
        )}
      >
        {selected && <Check className="h-3.5 w-3.5" strokeWidth={3} />}
      </span>
    </button>
  );
}
