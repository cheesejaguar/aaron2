import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Sparkles,
  Calendar,
  ChefHat,
  UtensilsCrossed,
  Flame,
  Coffee,
  Salad,
  Moon,
  Cookie,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { mealPlansApi } from "@/api/meal-plans";
import { recipesApi } from "@/api/recipes";
import { foodLogApi } from "@/api/food-log";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"] as const;

const MEAL_CONFIG = {
  breakfast: {
    icon: Coffee,
    accent: "rgb(245 158 11)", // amber
    accentMuted: "rgb(245 158 11 / 0.12)",
    label: "Breakfast",
  },
  lunch: {
    icon: Salad,
    accent: "rgb(16 185 129)", // emerald
    accentMuted: "rgb(16 185 129 / 0.12)",
    label: "Lunch",
  },
  dinner: {
    icon: Moon,
    accent: "rgb(244 114 69)", // warm coral
    accentMuted: "rgb(244 114 69 / 0.12)",
    label: "Dinner",
  },
  snack: {
    icon: Cookie,
    accent: "rgb(167 139 250)", // violet
    accentMuted: "rgb(167 139 250 / 0.12)",
    label: "Snack",
  },
} as const;

type MealJson = {
  name?: string;
  description?: string;
  estimated_calories?: number;
  estimated_sodium_mg?: number;
};

function getNextMonday(): string {
  const d = new Date();
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(d.setDate(diff));
  return monday.toISOString().split("T")[0];
}

function formatWeekRange(startDate: string): string {
  const start = new Date(startDate + "T00:00:00");
  const end = new Date(start);
  end.setDate(end.getDate() + 6);
  const fmt = (d: Date) =>
    d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  return `${fmt(start)} – ${fmt(end)}`;
}

export function MealPlannerPage() {
  const queryClient = useQueryClient();
  const [weekStart] = useState(getNextMonday());

  const { data: plans = [] } = useQuery({
    queryKey: ["meal-plans"],
    queryFn: mealPlansApi.list,
  });

  const suggestMutation = useMutation({
    mutationFn: mealPlansApi.suggest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meal-plans"] });
      toast.success("Meal plan generated!");
    },
    onError: () => toast.error("Failed to generate meal plan"),
  });

  const saveRecipeMutation = useMutation({
    mutationFn: recipesApi.create,
    onSuccess: (recipe) => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      toast.success(`"${recipe.title}" saved to recipes`);
    },
    onError: () => toast.error("Failed to save recipe"),
  });

  const logMealMutation = useMutation({
    mutationFn: foodLogApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["food-log"] });
      toast.success("Meal logged!");
    },
    onError: () => toast.error("Failed to log meal"),
  });

  const currentPlan = plans[0];

  const getMealsForDay = (dayIndex: number, mealType: string) => {
    if (!currentPlan) return null;
    return currentPlan.entries.find(
      (e) => e.day_of_week === dayIndex && e.meal_type === mealType
    );
  };

  const getDayCalories = (dayIndex: number): number => {
    if (!currentPlan) return 0;
    return currentPlan.entries
      .filter((e) => e.day_of_week === dayIndex)
      .reduce((sum, e) => {
        const meal = e.custom_meal_json as MealJson | null | undefined;
        return sum + (meal?.estimated_calories ?? 0);
      }, 0);
  };

  const handleSaveAsRecipe = (meal: MealJson, mealType: string) => {
    saveRecipeMutation.mutate({
      title: meal.name || "Untitled Meal",
      description: meal.description,
      health_tags: ["DASH", mealType],
    });
  };

  const handleLogMeal = (meal: MealJson, mealType: string) => {
    logMealMutation.mutate({
      meal_type: mealType,
      food_name: meal.name || "Meal",
      calories: meal.estimated_calories,
      sodium_mg: meal.estimated_sodium_mg,
    });
  };

  const isGenerating = suggestMutation.isPending;

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1
            className="text-4xl font-bold tracking-tight"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Meal Planner
          </h1>
          {currentPlan ? (
            <p className="mt-2 text-muted-foreground flex items-center gap-2 text-sm font-light">
              <Calendar className="h-3.5 w-3.5" />
              {formatWeekRange(currentPlan.week_start_date)}
            </p>
          ) : (
            <p className="mt-2 text-muted-foreground text-sm font-light">
              Plan your week with DASH-optimized meals
            </p>
          )}
        </div>
        <Button
          onClick={() =>
            suggestMutation.mutate({
              week_start_date: weekStart,
              health_focus: "DASH diet, low sodium",
            })
          }
          disabled={isGenerating}
          className="gap-2 px-5 h-11 text-sm font-medium rounded-xl shadow-lg shadow-primary/20 transition-all hover:shadow-xl hover:shadow-primary/30 hover:scale-[1.02] active:scale-[0.98]"
        >
          <Sparkles className={`h-4 w-4 ${isGenerating ? "generating-pulse" : ""}`} />
          {isGenerating ? "Crafting your week..." : "AI Suggest Plan"}
        </Button>
      </div>

      {/* Plan Grid */}
      {currentPlan ? (
        <div className="space-y-3">
          {/* Day headers */}
          <div className="grid grid-cols-7 gap-2 px-1">
            {DAYS.map((day, i) => {
              const startDate = new Date(currentPlan.week_start_date + "T00:00:00");
              startDate.setDate(startDate.getDate() + i);
              const dateNum = startDate.getDate();
              const isToday =
                new Date().toDateString() === startDate.toDateString();
              return (
                <div key={day} className="text-center">
                  <div
                    className={`text-xs tracking-wide uppercase font-semibold ${
                      isToday ? "text-primary" : "text-muted-foreground/60"
                    }`}
                  >
                    {day}
                  </div>
                  <div
                    className={`text-lg font-light mt-0.5 ${
                      isToday ? "text-primary" : "text-foreground/80"
                    }`}
                  >
                    {dateNum}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Meals by type */}
          {MEAL_TYPES.map((mealType) => {
            const config = MEAL_CONFIG[mealType];
            const Icon = config.icon;
            return (
              <div key={mealType} className="space-y-1.5">
                {/* Meal type label */}
                <div className="flex items-center gap-2 px-1 pt-2">
                  <Icon
                    className="h-3.5 w-3.5"
                    style={{ color: config.accent }}
                  />
                  <span
                    className="text-[11px] font-semibold uppercase tracking-widest"
                    style={{ color: config.accent }}
                  >
                    {config.label}
                  </span>
                </div>

                {/* Cards row */}
                <div className="grid grid-cols-7 gap-2">
                  {DAYS.map((_, dayIdx) => {
                    const entry = getMealsForDay(dayIdx, mealType);
                    const meal = entry?.custom_meal_json as
                      | MealJson
                      | null
                      | undefined;
                    const delay = dayIdx * 0.04 + MEAL_TYPES.indexOf(mealType) * 0.06;

                    if (!meal) {
                      return (
                        <div
                          key={dayIdx}
                          className="meal-card-enter rounded-xl border border-border/40 border-dashed min-h-[88px] flex items-center justify-center"
                          style={{ animationDelay: `${delay}s` }}
                        >
                          <span className="text-[10px] text-muted-foreground/30 font-light">
                            —
                          </span>
                        </div>
                      );
                    }

                    return (
                      <DropdownMenu key={dayIdx}>
                        <DropdownMenuTrigger asChild>
                          <button
                            className="meal-card-enter w-full text-left rounded-xl border border-border/50 min-h-[88px] p-3 transition-all duration-200 cursor-pointer group outline-none
                              hover:border-border hover:shadow-lg hover:shadow-black/20 hover:scale-[1.03] hover:-translate-y-0.5
                              focus-visible:ring-2 focus-visible:ring-primary/50"
                            style={{
                              animationDelay: `${delay}s`,
                              background: `linear-gradient(135deg, ${config.accentMuted} 0%, transparent 60%)`,
                            }}
                          >
                            <p className="text-[12.5px] font-medium leading-snug text-foreground/90 group-hover:text-foreground transition-colors line-clamp-2">
                              {meal.name}
                            </p>
                            {meal.estimated_calories && (
                              <div className="mt-2 flex items-center gap-1">
                                <Flame
                                  className="h-3 w-3"
                                  style={{ color: config.accent, opacity: 0.7 }}
                                />
                                <span
                                  className="text-[10px] font-medium tabular-nums"
                                  style={{ color: config.accent, opacity: 0.7 }}
                                >
                                  {meal.estimated_calories}
                                </span>
                              </div>
                            )}
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                          align="start"
                          className="w-48 rounded-xl"
                        >
                          <DropdownMenuItem
                            className="gap-2.5 cursor-pointer rounded-lg"
                            onClick={() => handleSaveAsRecipe(meal, mealType)}
                          >
                            <ChefHat className="h-4 w-4 text-muted-foreground" />
                            <span>Save as Recipe</span>
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="gap-2.5 cursor-pointer rounded-lg"
                            onClick={() => handleLogMeal(meal, mealType)}
                          >
                            <UtensilsCrossed className="h-4 w-4 text-muted-foreground" />
                            <span>Log to Food Log</span>
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* Daily calorie totals */}
          <div className="grid grid-cols-7 gap-2 pt-3 border-t border-border/30 mt-4">
            {DAYS.map((_, dayIdx) => {
              const total = getDayCalories(dayIdx);
              return (
                <div key={dayIdx} className="text-center">
                  <span className="text-xs text-muted-foreground/50 font-light">
                    Total
                  </span>
                  <p className="text-sm font-semibold tabular-nums text-foreground/70">
                    {total > 0 ? `${total}` : "—"}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      ) : isGenerating ? (
        /* Loading skeleton */
        <div className="space-y-4">
          <div className="grid grid-cols-7 gap-2">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="text-center">
                <div className="h-3 w-8 mx-auto rounded bg-muted/50 meal-shimmer" />
                <div className="h-5 w-5 mx-auto mt-1 rounded bg-muted/30 meal-shimmer" />
              </div>
            ))}
          </div>
          {MEAL_TYPES.map((type) => (
            <div key={type} className="grid grid-cols-7 gap-2">
              {Array.from({ length: 7 }).map((_, i) => (
                <div
                  key={i}
                  className="rounded-xl border border-border/30 min-h-[88px] meal-shimmer"
                  style={{ animationDelay: `${i * 0.1}s` }}
                />
              ))}
            </div>
          ))}
        </div>
      ) : (
        /* Empty state */
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="relative mb-6">
            <div
              className="absolute inset-0 rounded-full blur-2xl opacity-20"
              style={{
                background:
                  "radial-gradient(circle, rgb(245 158 11 / 0.5), rgb(16 185 129 / 0.3), rgb(244 114 69 / 0.3))",
              }}
            />
            <Calendar className="h-16 w-16 text-muted-foreground/40 relative" />
          </div>
          <h2
            className="text-2xl font-bold text-foreground/80 mb-2"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Your week awaits
          </h2>
          <p className="text-sm text-muted-foreground/60 max-w-sm font-light leading-relaxed">
            Generate a personalized DASH diet plan using ingredients from your
            pantry. Click any meal to save it as a recipe or log it directly.
          </p>
          <Button
            onClick={() =>
              suggestMutation.mutate({
                week_start_date: weekStart,
                health_focus: "DASH diet, low sodium",
              })
            }
            className="mt-8 gap-2 px-6 h-11 rounded-xl shadow-lg shadow-primary/20"
          >
            <Sparkles className="h-4 w-4" />
            Generate Meal Plan
          </Button>
        </div>
      )}
    </div>
  );
}
