import { Check } from "lucide-react";
import { cn } from "@/lib/cn";

export function Stepper({ steps, current }: { steps: string[]; current: number }) {
  return (
    <div className="flex items-center">
      {steps.map((label, i) => {
        const done = i < current;
        const active = i === current;
        return (
          <div key={label} className="flex flex-1 items-center last:flex-none">
            <div
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-full border font-mono text-xs transition-colors",
                done
                  ? "border-accent bg-accent text-[#052e22]"
                  : active
                    ? "border-accent text-accent-bright shadow-glow-sm"
                    : "border-line text-faint",
              )}
            >
              {done ? <Check className="h-3.5 w-3.5" strokeWidth={3} /> : i + 1}
            </div>
            {i < steps.length - 1 && (
              <div
                className={cn(
                  "mx-1.5 h-px flex-1 transition-colors",
                  done ? "bg-accent/60" : "bg-line",
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
