import { motion } from "framer-motion";
import { ArrowRight, BadgeCheck, ExternalLink, Lock, Search } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ContactWhatsapp } from "@/components/ContactWhatsapp";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { cn } from "@/lib/cn";
import { AVAILABILITY_LABELS, CATEGORY_BY_CODE, PRICING_LABELS } from "@/lib/labels";
import type { Availability, DeveloperPublic, PricingModel } from "@/lib/types";

function ProfileSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="panel p-5">
      <h2 className="mb-3 font-mono text-xs text-faint">// {title}</h2>
      {children}
    </div>
  );
}

function LinkPill({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-surface2 px-3 py-1.5 text-sm text-muted transition-colors hover:border-accent/40 hover:text-accent-bright"
    >
      {label}
      <ExternalLink className="h-3.5 w-3.5" />
    </a>
  );
}

const availabilityTone: Record<Availability, "available" | "limited" | "muted"> = {
  available: "available",
  limited: "limited",
  unavailable: "muted",
};

export function DeveloperProfile({
  dev,
  requestId,
}: {
  dev: DeveloperPublic;
  requestId: string | null;
}) {
  const hasLinks = dev.portfolio_url || (dev.links && Object.keys(dev.links).length > 0);

  return (
    <div className="container-app max-w-2xl py-10">
      <Link
        to="/match"
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-accent-bright"
      >
        <ArrowRight className="h-4 w-4" />
        חזרה לחיפוש
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="panel p-6 sm:p-8"
      >
        <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
          <Avatar name={dev.full_name} src={dev.avatar_url} size={88} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-ink">{dev.full_name}</h1>
              {dev.is_verified && <BadgeCheck className="h-5 w-5 text-accent-bright" />}
            </div>
            {dev.title && <p className="mt-0.5 text-muted">{dev.title}</p>}
            <div className="mt-2 flex flex-wrap gap-1.5">
              <Badge tone={availabilityTone[dev.availability as Availability]}>
                {AVAILABILITY_LABELS[dev.availability as Availability]}
              </Badge>
              {dev.is_verified && (
                <Badge tone="accent" icon={BadgeCheck}>
                  מאומת
                </Badge>
              )}
            </div>
          </div>
        </div>

        {dev.highlight && (
          <p className="mt-6 rounded-xl border border-accent/20 bg-accent/[0.05] px-4 py-3 font-medium text-ink">
            <span className="text-accent-bright">“</span>
            {dev.highlight}
            <span className="text-accent-bright">”</span>
          </p>
        )}

        {dev.bio && <p className="mt-5 leading-relaxed text-muted">{dev.bio}</p>}
      </motion.div>

      <div className="mt-4 grid gap-4">
        <ProfileSection title="סוגי פרויקט">
          <div className="flex flex-wrap gap-2">
            {dev.project_types.map((code) => {
              const c = CATEGORY_BY_CODE[code];
              return (
                <span
                  key={code}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-surface2 px-2.5 py-1 text-sm text-ink"
                >
                  {c?.Icon && <c.Icon className={cn("h-3.5 w-3.5", c.tint)} />}
                  {c?.label ?? code}
                </span>
              );
            })}
          </div>
        </ProfileSection>

        {dev.stack && dev.stack.length > 0 && (
          <ProfileSection title="טכנולוגיות (Stack)">
            <div className="flex flex-wrap gap-1.5">
              {dev.stack.map((s) => (
                <Chip key={s}>{s}</Chip>
              ))}
            </div>
          </ProfileSection>
        )}

        {dev.ai_tools && dev.ai_tools.length > 0 && (
          <ProfileSection title="כלי AI">
            <div className="flex flex-wrap gap-1.5">
              {dev.ai_tools.map((s) => (
                <Chip key={s}>{s}</Chip>
              ))}
            </div>
          </ProfileSection>
        )}

        <ProfileSection title="תמחור">
          <div className="flex flex-wrap items-center gap-2">
            {dev.pricing_models.map((m) => (
              <Badge key={m} tone="neutral">
                {PRICING_LABELS[m as PricingModel]?.label ?? m}
              </Badge>
            ))}
            {dev.hourly_rate && (
              <span dir="ltr" className="font-mono text-sm text-accent-bright">
                ₪{dev.hourly_rate}/hr
              </span>
            )}
          </div>
        </ProfileSection>

        {hasLinks && (
          <ProfileSection title="פורטפוליו וקישורים">
            <div className="flex flex-wrap gap-2">
              {dev.portfolio_url && <LinkPill href={dev.portfolio_url} label="תיק עבודות" />}
              {dev.links?.linkedin && <LinkPill href={dev.links.linkedin} label="LinkedIn" />}
              {dev.links?.github && <LinkPill href={dev.links.github} label="GitHub" />}
            </div>
          </ProfileSection>
        )}
      </div>

      <div className="mt-6">
        {requestId ? (
          <ContactWhatsapp requestId={requestId} developerId={dev.id} />
        ) : (
          <div className="panel flex flex-col items-center gap-3 p-6 text-center">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-line bg-surface2">
              <Lock className="h-5 w-5 text-muted" />
            </div>
            <p className="max-w-md text-sm leading-relaxed text-muted">
              כדי לפנות ל{dev.full_name} בוואטסאפ, ענה על 5 שאלות קצרות ונתאים אותך —
              כך הפנייה נרשמת והמספר נחשף רק לך.
            </p>
            <Link to="/match">
              <Button>
                <Search className="h-4 w-4" />
                מצא התאמה
              </Button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
