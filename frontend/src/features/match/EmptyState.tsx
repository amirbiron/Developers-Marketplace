import { SearchX } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function EmptyState({ onReset }: { onReset: () => void }) {
  return (
    <div className="panel flex flex-col items-center gap-4 p-10 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-line bg-surface2">
        <SearchX className="h-7 w-7 text-muted" />
      </div>
      <div>
        <h3 className="text-lg font-bold text-ink">לא נמצאו מפתחים מתאימים</h3>
        <p className="mt-1 max-w-sm text-sm leading-relaxed text-muted">
          עוד אין מפתח שתואם בדיוק למה שחיפשת. אפשר לנסות קטגוריה אחרת, או לפרסם בקשה פתוחה
          ונעדכן אותך כשיצטרף מי שמתאים.
        </p>
      </div>
      <Button variant="primary" onClick={onReset}>
        חיפוש חדש
      </Button>
    </div>
  );
}
