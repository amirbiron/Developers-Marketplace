import { motion } from "framer-motion";
import { BadgeCheck, ExternalLink } from "lucide-react";
import { useState } from "react";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { ScoreRing } from "@/components/ui/ScoreRing";
import { postReferral } from "@/lib/api";
import { AVAILABILITY_LABELS, PRICING_LABELS } from "@/lib/labels";
import type { MatchResultItem, PricingModel } from "@/lib/types";

function WhatsappGlyph() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden>
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.372-.025-.521-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.694.625.712.227 1.36.195 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.885-9.885 9.885M20.52 3.449C18.24 1.245 15.24 0 12.045 0 5.463 0 .104 5.359.101 11.893c0 2.096.549 4.14 1.595 5.945L0 24l6.335-1.652a12.062 12.062 0 005.71 1.454h.006c6.585 0 11.946-5.359 11.949-11.893a11.821 11.821 0 00-3.48-8.46" />
    </svg>
  );
}

interface DeveloperCardProps {
  dev: MatchResultItem;
  requestId: string;
  index: number;
}

export function DeveloperCard({ dev, requestId, index }: DeveloperCardProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const contact = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await postReferral(requestId, dev.developer_id);
      window.open(res.wa_link, "_blank", "noopener,noreferrer");
    } catch (e) {
      setError(e instanceof Error ? e.message : "לא הצלחנו לפתוח את הפנייה");
    } finally {
      setLoading(false);
    }
  };

  const pricingLabels = dev.pricing_models.map(
    (m) => PRICING_LABELS[m as PricingModel]?.label ?? m,
  );

  return (
    <motion.article
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06 }}
      className="panel group flex flex-col gap-4 p-5 transition-colors hover:border-line-strong"
    >
      <div className="flex items-start gap-4">
        <Avatar name={dev.full_name} src={dev.avatar_url} size={56} />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <h3 className="truncate text-lg font-bold text-ink">{dev.full_name}</h3>
            {dev.is_verified && <BadgeCheck className="h-4 w-4 shrink-0 text-accent-bright" />}
          </div>
          {dev.title && <p className="truncate text-sm text-muted">{dev.title}</p>}
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            <Badge tone={dev.availability === "available" ? "available" : "limited"}>
              {AVAILABILITY_LABELS[dev.availability]}
            </Badge>
            {dev.is_verified && (
              <Badge tone="accent" icon={BadgeCheck}>
                מאומת
              </Badge>
            )}
          </div>
        </div>
        <ScoreRing value={dev.match_score} />
      </div>

      {dev.highlight && (
        <p className="rounded-xl border border-accent/20 bg-accent/[0.05] px-3 py-2 text-sm font-medium text-ink">
          <span className="text-accent-bright">“</span>
          {dev.highlight}
          <span className="text-accent-bright">”</span>
        </p>
      )}

      {dev.bio && <p className="line-clamp-2 text-sm leading-relaxed text-muted">{dev.bio}</p>}

      {dev.stack && dev.stack.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {dev.stack.slice(0, 6).map((s) => (
            <Chip key={s}>{s}</Chip>
          ))}
        </div>
      )}

      <div className="mt-auto flex items-center justify-between gap-2 border-t border-line pt-4">
        <div className="text-sm">
          <span className="text-muted">{pricingLabels.join(" · ")}</span>
          {dev.hourly_rate && (
            <span dir="ltr" className="ms-1.5 font-mono text-accent-bright">
              ₪{dev.hourly_rate}/hr
            </span>
          )}
        </div>
        {dev.portfolio_url && (
          <a
            href={dev.portfolio_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex shrink-0 items-center gap-1 text-sm text-muted transition-colors hover:text-accent-bright"
          >
            תיק עבודות <ExternalLink className="h-3.5 w-3.5" />
          </a>
        )}
      </div>

      <Button variant="whatsapp" onClick={contact} loading={loading} className="w-full">
        {!loading && <WhatsappGlyph />}
        פנה בוואטסאפ
      </Button>
      {error && <p className="text-center text-xs text-syntax-rose">{error}</p>}
    </motion.article>
  );
}
