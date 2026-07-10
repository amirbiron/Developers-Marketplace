import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { DeveloperProfile } from "@/features/developer/DeveloperProfile";
import { getDeveloper } from "@/lib/api";
import type { DeveloperPublic } from "@/lib/types";

export function DeveloperPage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const requestId = (location.state as { requestId?: string } | null)?.requestId ?? null;

  const [dev, setDev] = useState<DeveloperPublic | null>(null);
  const [status, setStatus] = useState<"loading" | "error" | "ok">("loading");

  useEffect(() => {
    if (!id) return;
    let active = true;
    setStatus("loading");
    getDeveloper(id)
      .then((d) => {
        if (active) {
          setDev(d);
          setStatus("ok");
        }
      })
      .catch(() => {
        if (active) setStatus("error");
      });
    return () => {
      active = false;
    };
  }, [id]);

  if (status === "loading") {
    return (
      <div className="flex justify-center py-32">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (status === "error" || !dev) {
    return (
      <div className="container-app max-w-lg py-24">
        <div className="panel p-10 text-center">
          <h1 className="text-xl font-bold text-ink">המפתח לא נמצא</h1>
          <p className="mt-2 text-sm text-muted">ייתכן שהפרופיל הוסר, הושהה, או שהקישור שגוי.</p>
          <Link to="/match" className="mt-5 inline-block">
            <Button variant="secondary">חזרה לחיפוש</Button>
          </Link>
        </div>
      </div>
    );
  }

  return <DeveloperProfile dev={dev} requestId={requestId} />;
}
