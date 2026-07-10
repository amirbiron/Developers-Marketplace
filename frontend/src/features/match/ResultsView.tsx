import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import type { MatchResponse } from "@/lib/types";
import { DeveloperCard } from "./DeveloperCard";
import { EmptyState } from "./EmptyState";

interface ResultsViewProps {
  data: MatchResponse;
  projectTypeLabel: string;
  onReset: () => void;
}

export function ResultsView({ data, projectTypeLabel, onReset }: ResultsViewProps) {
  const { results, request_id } = data;
  return (
    <div className="container-app py-10">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-xs text-accent-bright">
            // {results.length} תוצאות · {projectTypeLabel}
          </p>
          <h1 className="mt-1 text-2xl font-bold text-ink sm:text-3xl">
            {results.length > 0 ? "המפתחים שהכי מתאימים לך" : "לא נמצאו התאמות"}
          </h1>
          {results.length > 0 && (
            <p className="mt-1 text-sm text-muted">
              ממוין לפי התאמה. הפנייה ישירה בוואטסאפ — בלי תיווך ובלי עמלות.
            </p>
          )}
        </div>
        <Button variant="secondary" onClick={onReset} className="shrink-0">
          <ArrowRight className="h-4 w-4" />
          חיפוש חדש
        </Button>
      </div>

      {results.length === 0 ? (
        <EmptyState onReset={onReset} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {results.map((dev, i) => (
            <DeveloperCard key={dev.developer_id} dev={dev} requestId={request_id} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
