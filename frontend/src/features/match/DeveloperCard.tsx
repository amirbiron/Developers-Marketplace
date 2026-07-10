import { motion } from "framer-motion";
import { BadgeCheck, ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";
import { ContactWhatsapp } from "@/components/ContactWhatsapp";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Chip } from "@/components/ui/Chip";
import { ScoreRing } from "@/components/ui/ScoreRing";
import { AVAILABILITY_LABELS, PRICING_LABELS } from "@/lib/labels";
import type { MatchResultItem, PricingModel } from "@/lib/types";

interface DeveloperCardProps {
  dev: MatchResultItem;
  requestId: string;
  index: number;
}

export function DeveloperCard({ dev, requestId, index }: DeveloperCardProps) {
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
        <Link
          to={`/dev/${dev.developer_id}`}
          state={{ requestId }}
          className="group/name flex min-w-0 flex-1 items-start gap-4"
        >
          <Avatar name={dev.full_name} src={dev.avatar_url} size={56} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5">
              <h3 className="truncate text-lg font-bold text-ink transition-colors group-hover/name:text-accent-bright">
                {dev.full_name}
              </h3>
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
        </Link>
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

      <ContactWhatsapp requestId={requestId} developerId={dev.developer_id} />
    </motion.article>
  );
}
