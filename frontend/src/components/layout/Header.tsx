import { Terminal } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/cn";

export function Header() {
  const { pathname } = useLocation();

  const navLink = (to: string, label: string) => (
    <Link
      to={to}
      className={cn(
        "rounded-lg px-3 py-1.5 text-sm font-medium transition-colors",
        pathname === to ? "text-ink" : "text-muted hover:text-ink",
      )}
    >
      {label}
    </Link>
  );

  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-bg/70 backdrop-blur-xl">
      <div className="container-app flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-line bg-surface shadow-glow-sm">
            <Terminal className="h-5 w-5 text-accent-bright" />
          </span>
          <span dir="ltr" className="font-mono text-sm">
            <span className="text-faint">~/</span>
            <span className="font-semibold text-ink">devmatch</span>
            <span className="ml-0.5 inline-block h-4 w-[7px] translate-y-[3px] bg-accent-bright animate-blink" />
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {navLink("/match", "מצא מפתח")}
          {navLink("/join", "הצטרפ/י כמפתח/ת")}
        </nav>
      </div>
    </header>
  );
}
