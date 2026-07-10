function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  return ((parts[0]?.[0] ?? "") + (parts[1]?.[0] ?? "")).toUpperCase() || "?";
}

interface AvatarProps {
  name: string;
  src?: string | null;
  size?: number;
}

export function Avatar({ name, src, size = 56 }: AvatarProps) {
  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className="rounded-2xl border border-line object-cover"
        style={{ width: size, height: size }}
      />
    );
  }
  return (
    <div
      className="flex shrink-0 items-center justify-center rounded-2xl border border-accent/30 bg-gradient-to-br from-accent/25 to-syntax-cyan/15 font-mono font-bold text-accent-bright"
      style={{ width: size, height: size, fontSize: size * 0.32 }}
    >
      {initials(name)}
    </div>
  );
}
