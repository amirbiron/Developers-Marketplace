import { X } from "lucide-react";
import { type KeyboardEvent, useState } from "react";

interface TagInputProps {
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  suggestions?: string[];
}

export function TagInput({ value, onChange, placeholder, suggestions = [] }: TagInputProps) {
  const [draft, setDraft] = useState("");

  const add = (raw: string) => {
    const token = raw.trim();
    if (!token) return;
    if (!value.some((v) => v.toLowerCase() === token.toLowerCase())) {
      onChange([...value, token]);
    }
    setDraft("");
  };

  const remove = (token: string) => onChange(value.filter((v) => v !== token));

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      add(draft);
    } else if (e.key === "Backspace" && !draft && value.length > 0) {
      remove(value[value.length - 1]);
    }
  };

  const remaining = suggestions
    .filter((s) => !value.some((v) => v.toLowerCase() === s.toLowerCase()))
    .slice(0, 6);

  return (
    <div>
      <div className="flex flex-wrap items-center gap-1.5 rounded-xl border border-line bg-surface2 p-2 transition-colors focus-within:border-accent/60 focus-within:ring-2 focus-within:ring-accent/20">
        {value.map((token) => (
          <span
            key={token}
            className="inline-flex items-center gap-1 rounded-lg border border-line bg-surface px-2 py-1 font-mono text-xs text-ink"
          >
            {token}
            <button
              type="button"
              onClick={() => remove(token)}
              className="text-faint transition-colors hover:text-syntax-rose"
              aria-label={`הסר ${token}`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={value.length ? "" : placeholder}
          className="min-w-[110px] flex-1 bg-transparent px-1.5 py-1 text-sm text-ink placeholder:text-faint focus:outline-none"
        />
      </div>

      {remaining.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {remaining.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => add(s)}
              className="rounded-lg border border-line bg-surface px-2 py-1 font-mono text-xs text-muted transition-colors hover:border-accent/40 hover:text-accent-bright"
            >
              + {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
