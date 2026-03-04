import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Clock } from "lucide-react";
import { pantryApi } from "@/api/pantry";

export function PantryAlerts() {
  const { data: items = [] } = useQuery({
    queryKey: ["pantry"],
    queryFn: pantryApi.list,
  });

  const today = new Date();
  const threeDaysFromNow = new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000);

  const lowStock = items.filter(
    (item) =>
      item.low_stock_threshold != null && item.quantity <= item.low_stock_threshold
  );

  const expiringSoon = items.filter((item) => {
    if (!item.estimated_expiry) return false;
    const expiry = new Date(item.estimated_expiry);
    return expiry <= threeDaysFromNow && expiry >= today;
  });

  if (lowStock.length === 0 && expiringSoon.length === 0) return null;

  return (
    <div className="meal-card-enter rounded-2xl border border-amber-500/20 p-5" style={{ background: "linear-gradient(135deg, rgb(245 158 11 / 0.05) 0%, transparent 60%)" }}>
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="h-4 w-4" style={{ color: "rgb(245 158 11)" }} />
        <h3 className="text-xs font-semibold uppercase tracking-widest" style={{ color: "rgb(245 158 11)" }}>
          Pantry Alerts
        </h3>
      </div>
      <div className="space-y-2">
        {lowStock.map((item) => (
          <div key={`low-${item.id}`} className="flex items-center gap-3 text-sm">
            <span className="shrink-0 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full" style={{ color: "rgb(245 158 11)", background: "rgb(245 158 11 / 0.1)" }}>
              Low
            </span>
            <span className="text-foreground/70 font-light">
              {item.name} — {item.quantity} {item.unit || "units"}
            </span>
          </div>
        ))}
        {expiringSoon.map((item) => (
          <div key={`exp-${item.id}`} className="flex items-center gap-3 text-sm">
            <span className="shrink-0 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full inline-flex items-center gap-1" style={{ color: "rgb(239 68 68)", background: "rgb(239 68 68 / 0.1)" }}>
              <Clock className="h-2.5 w-2.5" />
              Exp
            </span>
            <span className="text-foreground/70 font-light">
              {item.name} — {item.estimated_expiry}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
