import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

export function Chip({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-lg border border-line bg-surface2 px-2 py-0.5 font-mono text-xs text-muted",
        className,
      )}
    >
      {children}
    </span>
  );
}
