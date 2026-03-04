import type { DailySummary } from "@/types";

interface NutritionRingsProps {
  summary: DailySummary;
}

const GOALS = {
  calories: 2000,
  protein_g: 50,
  carbs_g: 250,
  fat_g: 65,
  fiber_g: 30,
  sodium_mg: 1500,
  potassium_mg: 4700,
};

const NUTRIENTS = [
  { key: "total_calories", goal: GOALS.calories, label: "Calories", unit: "cal", accent: "rgb(244 114 69)" },
  { key: "total_protein_g", goal: GOALS.protein_g, label: "Protein", unit: "g", accent: "rgb(239 68 68)" },
  { key: "total_carbs_g", goal: GOALS.carbs_g, label: "Carbs", unit: "g", accent: "rgb(245 158 11)" },
  { key: "total_fat_g", goal: GOALS.fat_g, label: "Fat", unit: "g", accent: "rgb(167 139 250)" },
  { key: "total_fiber_g", goal: GOALS.fiber_g, label: "Fiber", unit: "g", accent: "rgb(16 185 129)" },
  { key: "total_sodium_mg", goal: GOALS.sodium_mg, label: "Sodium", unit: "mg", accent: "rgb(251 146 60)" },
  { key: "total_potassium_mg", goal: GOALS.potassium_mg, label: "Potassium", unit: "mg", accent: "rgb(34 211 238)" },
] as const;

export function NutritionRings({ summary }: NutritionRingsProps) {
  return (
    <div className="space-y-4">
      {/* Primary macro — Calories as a hero number */}
      <div className="flex items-baseline justify-between pb-3 border-b border-border/30">
        <div>
          <span className="text-3xl font-bold tabular-nums" style={{ fontFamily: "'DM Serif Display', serif" }}>
            {Math.round(summary.total_calories)}
          </span>
          <span className="text-sm text-muted-foreground/50 ml-1.5">
            / {GOALS.calories} cal
          </span>
        </div>
        <span className="text-xs text-muted-foreground/40 font-light">
          {summary.meal_count} meal{summary.meal_count !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Nutrient bars */}
      <div className="space-y-3">
        {NUTRIENTS.slice(1).map(({ key, goal, label, unit, accent }) => {
          const value = summary[key] as number;
          const percent = Math.min((value / goal) * 100, 100);
          const isOverSodium = key === "total_sodium_mg" && value > goal;

          return (
            <div key={key} className="group">
              <div className="flex items-baseline justify-between mb-1.5">
                <span className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: isOverSodium ? "rgb(239 68 68)" : accent, opacity: 0.8 }}>
                  {label}
                </span>
                <span className="text-xs tabular-nums text-muted-foreground/50">
                  <span className={`font-medium ${isOverSodium ? "text-red-400" : "text-foreground/70"}`}>
                    {Math.round(value)}
                  </span>
                  {" / "}
                  {goal} {unit}
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-muted/30 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700 ease-out"
                  style={{
                    width: `${percent}%`,
                    background: isOverSodium
                      ? "rgb(239 68 68)"
                      : `linear-gradient(90deg, ${accent}, ${accent}dd)`,
                    boxShadow: percent > 5 ? `0 0 8px ${accent}40` : "none",
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
