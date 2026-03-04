import { useQuery } from "@tanstack/react-query";
import { Bot, Loader2 } from "lucide-react";
import { coachApi } from "@/api/coach";

interface AIDailySummaryProps {
  date: string;
}

export function AIDailySummary({ date }: AIDailySummaryProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["coach", "daily-summary", date],
    queryFn: () => coachApi.dailyNutritionSummary(date),
  });

  return (
    <div
      className="meal-card-enter rounded-2xl border border-border/40 p-6"
      style={{
        background:
          "linear-gradient(145deg, rgb(167 139 250 / 0.05) 0%, transparent 50%)",
      }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Bot className="h-4 w-4" style={{ color: "rgb(167 139 250 / 0.6)" }} />
        <h2
          className="text-lg font-bold"
          style={{ fontFamily: "'DM Serif Display', serif" }}
        >
          AI Daily Summary
        </h2>
      </div>
      {isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground/50 font-light text-sm">
          <Loader2 className="h-4 w-4 animate-spin" />
          Analyzing your nutrition data...
        </div>
      ) : data?.insights && data.insights.length > 0 ? (
        <div className="space-y-3">
          {data.insights.map(
            (
              insight: { title: string; description: string },
              i: number
            ) => (
              <div
                key={i}
                className="rounded-xl p-3.5 bg-muted/20 border-l-2"
                style={{ borderLeftColor: "rgb(167 139 250 / 0.3)" }}
              >
                <p className="text-sm font-medium leading-snug mb-1">
                  {insight.title}
                </p>
                <p className="text-xs text-muted-foreground/50 font-light leading-relaxed">
                  {insight.description}
                </p>
              </div>
            )
          )}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground/40 font-light">
          Log more food to get AI-powered nutrition insights.
        </p>
      )}
    </div>
  );
}
