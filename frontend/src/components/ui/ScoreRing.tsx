import { motion } from "framer-motion";

interface ScoreRingProps {
  value: number; // 0..100
  size?: number;
  stroke?: number;
}

/** טבעת ציון התאמה — SVG עם גרדיאנט ירוק ואנימציית מילוי בכניסה. */
export function ScoreRing({ value, size = 78, stroke = 6 }: ScoreRingProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - clamped / 100);

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1e2a36"
          strokeWidth={stroke}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#scoreGrad)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.1, ease: "easeOut" }}
        />
        <defs>
          <linearGradient id="scoreGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#34d399" />
            <stop offset="100%" stopColor="#0d9488" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span dir="ltr" className="font-mono text-lg font-bold leading-none text-ink">
          {clamped}
          <span className="text-xs text-muted">%</span>
        </span>
        <span className="mt-0.5 text-[10px] text-faint">התאמה</span>
      </div>
    </div>
  );
}
