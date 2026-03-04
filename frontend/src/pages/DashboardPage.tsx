import { useQuery } from "@tanstack/react-query";
import {
  Heart,
  Scale,
  Activity,
  TrendingDown,
  Bot,
  Sparkles,
  Utensils,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { healthApi } from "@/api/health";
import { foodLogApi } from "@/api/food-log";
import { coachApi } from "@/api/coach";
import { useUIStore } from "@/stores/ui-store";
import { NutritionRings } from "@/components/dashboard/NutritionRings";
import { PantryAlerts } from "@/components/dashboard/PantryAlerts";

const BP_STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  normal: { label: "Normal", color: "rgb(16 185 129)", bg: "rgb(16 185 129 / 0.1)" },
  elevated: { label: "Elevated", color: "rgb(245 158 11)", bg: "rgb(245 158 11 / 0.1)" },
  high_stage_1: { label: "High Stage 1", color: "rgb(251 146 60)", bg: "rgb(251 146 60 / 0.1)" },
  high_stage_2: { label: "High Stage 2", color: "rgb(239 68 68)", bg: "rgb(239 68 68 / 0.1)" },
  crisis: { label: "Crisis", color: "rgb(185 28 28)", bg: "rgb(185 28 28 / 0.15)" },
};

const INSIGHT_PRIORITY_BORDER: Record<string, string> = {
  high: "rgb(239 68 68 / 0.5)",
  medium: "rgb(245 158 11 / 0.4)",
  low: "rgb(16 185 129 / 0.3)",
};

function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

export function DashboardPage() {
  const toggleCoach = useUIStore((s) => s.toggleCoachPanel);
  const today = new Date().toISOString().split("T")[0];

  const { data: dashboard } = useQuery({
    queryKey: ["health", "dashboard"],
    queryFn: healthApi.dashboard,
  });

  const { data: dailySummary } = useQuery({
    queryKey: ["food-log", "daily-summary", today],
    queryFn: () => foodLogApi.dailySummary(today),
  });

  const { data: insights } = useQuery({
    queryKey: ["coach", "insights"],
    queryFn: coachApi.insights,
  });

  const bpStatus = dashboard?.bp_status
    ? BP_STATUS_CONFIG[dashboard.bp_status]
    : null;

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground/50 font-light mb-1">
            {getGreeting()}, Aaron
          </p>
          <h1
            className="text-4xl font-bold tracking-tight"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Dashboard
          </h1>
        </div>
        <Button
          variant="outline"
          onClick={toggleCoach}
          className="gap-2 rounded-xl h-10 px-4 border-border/50"
        >
          <Bot className="h-4 w-4" />
          AI Coach
        </Button>
      </div>

      {/* Health Metrics — Three cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Blood Pressure */}
        <div
          className="meal-card-enter rounded-2xl border border-border/40 p-5 transition-all duration-200 hover:border-border/70 hover:shadow-lg hover:shadow-black/10"
          style={{
            animationDelay: "0s",
            background: "linear-gradient(145deg, rgb(239 68 68 / 0.06) 0%, transparent 50%)",
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "rgb(239 68 68 / 0.6)" }}>
              Blood Pressure
            </span>
            <Heart className="h-4 w-4" style={{ color: "rgb(239 68 68 / 0.4)" }} />
          </div>
          {dashboard?.latest_bp ? (
            <>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold tabular-nums" style={{ fontFamily: "'DM Serif Display', serif" }}>
                  {dashboard.latest_bp.systolic}
                </span>
                <span className="text-lg text-muted-foreground/40 font-light">/</span>
                <span className="text-3xl font-bold tabular-nums" style={{ fontFamily: "'DM Serif Display', serif" }}>
                  {dashboard.latest_bp.diastolic}
                </span>
              </div>
              {bpStatus && (
                <span
                  className="inline-block mt-3 text-[10px] font-semibold uppercase tracking-wider px-2.5 py-1 rounded-full"
                  style={{ color: bpStatus.color, background: bpStatus.bg }}
                >
                  {bpStatus.label}
                </span>
              )}
              {dashboard.latest_bp.pulse && (
                <p className="mt-2 text-xs text-muted-foreground/40 font-light">
                  {dashboard.latest_bp.pulse} bpm
                </p>
              )}
            </>
          ) : (
            <p className="text-sm text-muted-foreground/40 font-light mt-2">
              No readings yet
            </p>
          )}
        </div>

        {/* Weight */}
        <div
          className="meal-card-enter rounded-2xl border border-border/40 p-5 transition-all duration-200 hover:border-border/70 hover:shadow-lg hover:shadow-black/10"
          style={{
            animationDelay: "0.06s",
            background: "linear-gradient(145deg, rgb(96 165 250 / 0.06) 0%, transparent 50%)",
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "rgb(96 165 250 / 0.6)" }}>
              Weight
            </span>
            <Scale className="h-4 w-4" style={{ color: "rgb(96 165 250 / 0.4)" }} />
          </div>
          {dashboard?.latest_weight ? (
            <>
              <div className="flex items-baseline gap-1.5">
                <span className="text-3xl font-bold tabular-nums" style={{ fontFamily: "'DM Serif Display', serif" }}>
                  {dashboard.latest_weight.weight_lbs}
                </span>
                <span className="text-sm text-muted-foreground/40 font-light">lbs</span>
              </div>
              <p className="mt-3 text-xs text-muted-foreground/40 font-light flex items-center gap-1.5">
                <TrendingDown className="h-3 w-3" />
                {dashboard.weight_trend.length} reading{dashboard.weight_trend.length !== 1 ? "s" : ""} tracked
              </p>
            </>
          ) : (
            <p className="text-sm text-muted-foreground/40 font-light mt-2">
              No readings yet
            </p>
          )}
        </div>

        {/* Cholesterol */}
        <div
          className="meal-card-enter rounded-2xl border border-border/40 p-5 transition-all duration-200 hover:border-border/70 hover:shadow-lg hover:shadow-black/10"
          style={{
            animationDelay: "0.12s",
            background: "linear-gradient(145deg, rgb(245 158 11 / 0.06) 0%, transparent 50%)",
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "rgb(245 158 11 / 0.6)" }}>
              Cholesterol
            </span>
            <Activity className="h-4 w-4" style={{ color: "rgb(245 158 11 / 0.4)" }} />
          </div>
          {dashboard?.latest_cholesterol ? (
            <>
              <div className="flex items-baseline gap-1.5">
                <span className="text-3xl font-bold tabular-nums" style={{ fontFamily: "'DM Serif Display', serif" }}>
                  {dashboard.latest_cholesterol.total_mg_dl}
                </span>
                <span className="text-sm text-muted-foreground/40 font-light">mg/dL</span>
              </div>
              <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground/40 font-light">
                <span>
                  LDL <span className="text-foreground/60 font-medium tabular-nums">{dashboard.latest_cholesterol.ldl ?? "—"}</span>
                </span>
                <span className="text-border">|</span>
                <span>
                  HDL <span className="text-foreground/60 font-medium tabular-nums">{dashboard.latest_cholesterol.hdl ?? "—"}</span>
                </span>
                {dashboard.latest_cholesterol.triglycerides != null && (
                  <>
                    <span className="text-border">|</span>
                    <span>
                      Trig <span className="text-foreground/60 font-medium tabular-nums">{dashboard.latest_cholesterol.triglycerides}</span>
                    </span>
                  </>
                )}
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground/40 font-light mt-2">
              No readings yet
            </p>
          )}
        </div>
      </div>

      {/* Pantry Alerts */}
      <PantryAlerts />

      {/* Nutrition + Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Nutrition — takes 3 cols */}
        <div
          className="meal-card-enter lg:col-span-3 rounded-2xl border border-border/40 p-6"
          style={{ animationDelay: "0.18s" }}
        >
          <div className="flex items-center gap-2 mb-5">
            <Utensils className="h-4 w-4" style={{ color: "rgb(244 114 69 / 0.6)" }} />
            <h2
              className="text-lg font-bold"
              style={{ fontFamily: "'DM Serif Display', serif" }}
            >
              Today's Nutrition
            </h2>
          </div>
          {dailySummary ? (
            <NutritionRings summary={dailySummary} />
          ) : (
            <p className="text-sm text-muted-foreground/40 font-light py-4">
              No food logged today
            </p>
          )}
        </div>

        {/* AI Insights — takes 2 cols */}
        <div
          className="meal-card-enter lg:col-span-2 rounded-2xl border border-border/40 p-6"
          style={{ animationDelay: "0.24s" }}
        >
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" style={{ color: "rgb(167 139 250 / 0.6)" }} />
              <h2
                className="text-lg font-bold"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                AI Insights
              </h2>
            </div>
          </div>
          <div className="space-y-3">
            {insights?.insights && insights.insights.length > 0 ? (
              insights.insights.map((insight, i) => (
                <div
                  key={i}
                  className="meal-card-enter rounded-xl p-3.5 bg-muted/20 border-l-2"
                  style={{
                    animationDelay: `${0.3 + i * 0.06}s`,
                    borderLeftColor:
                      INSIGHT_PRIORITY_BORDER[insight.priority] || "rgb(16 185 129 / 0.3)",
                  }}
                >
                  <div className="flex items-center gap-2 mb-1.5">
                    <span
                      className="text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-full"
                      style={{
                        color: "rgb(167 139 250 / 0.7)",
                        background: "rgb(167 139 250 / 0.08)",
                      }}
                    >
                      {insight.category}
                    </span>
                  </div>
                  <p className="text-sm font-medium leading-snug mb-1">
                    {insight.title}
                  </p>
                  <p className="text-xs text-muted-foreground/50 font-light leading-relaxed">
                    {insight.description}
                  </p>
                </div>
              ))
            ) : (
              <div className="py-6 text-center">
                <Bot className="h-8 w-8 text-muted-foreground/20 mx-auto mb-3" />
                <p className="text-sm text-muted-foreground/40 font-light">
                  Insights will appear as you log more data
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
