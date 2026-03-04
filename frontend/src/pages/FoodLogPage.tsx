import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import {
  Plus,
  UtensilsCrossed,
  Coffee,
  Salad,
  Moon,
  Cookie,
  Flame,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { foodLogApi } from "@/api/food-log";
import { NutritionRings } from "@/components/dashboard/NutritionRings";
import { AIDailySummary } from "@/components/food-log/AIDailySummary";
import { foodLogSchema, type FoodLogFormData } from "@/lib/validations";

const MEAL_CONFIG: Record<
  string,
  { icon: typeof Coffee; accent: string; accentMuted: string; label: string }
> = {
  breakfast: {
    icon: Coffee,
    accent: "rgb(245 158 11)",
    accentMuted: "rgb(245 158 11 / 0.08)",
    label: "Breakfast",
  },
  lunch: {
    icon: Salad,
    accent: "rgb(16 185 129)",
    accentMuted: "rgb(16 185 129 / 0.08)",
    label: "Lunch",
  },
  dinner: {
    icon: Moon,
    accent: "rgb(244 114 69)",
    accentMuted: "rgb(244 114 69 / 0.08)",
    label: "Dinner",
  },
  snack: {
    icon: Cookie,
    accent: "rgb(167 139 250)",
    accentMuted: "rgb(167 139 250 / 0.08)",
    label: "Snack",
  },
};

export function FoodLogPage() {
  const queryClient = useQueryClient();
  const today = new Date().toISOString().split("T")[0];
  const [addOpen, setAddOpen] = useState(false);

  const form = useForm<FoodLogFormData>({
    resolver: zodResolver(foodLogSchema),
    defaultValues: { meal_type: "lunch", food_name: "" },
  });

  const { data: logs = [] } = useQuery({
    queryKey: ["food-log", today],
    queryFn: () => foodLogApi.list(today),
  });

  const { data: summary } = useQuery({
    queryKey: ["food-log", "daily-summary", today],
    queryFn: () => foodLogApi.dailySummary(today),
  });

  const createMutation = useMutation({
    mutationFn: foodLogApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["food-log"] });
      setAddOpen(false);
      form.reset();
      toast.success("Food logged");
    },
  });

  const onSubmit = (data: FoodLogFormData) => {
    createMutation.mutate(data);
  };

  // Group logs by meal type
  const grouped = logs.reduce(
    (acc, log) => {
      const type = log.meal_type || "snack";
      if (!acc[type]) acc[type] = [];
      acc[type].push(log);
      return acc;
    },
    {} as Record<string, typeof logs>
  );

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1
            className="text-4xl font-bold tracking-tight"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Food Log
          </h1>
          <p className="mt-2 text-sm text-muted-foreground/50 font-light">
            {new Date().toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>
        <Dialog open={addOpen} onOpenChange={setAddOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2 rounded-xl h-10 px-4">
              <Plus className="h-4 w-4" />
              Log Food
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg rounded-2xl">
            <DialogHeader>
              <DialogTitle
                className="text-xl"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                Log Food
              </DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mt-2">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="food_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Food Name
                        </FormLabel>
                        <FormControl>
                          <Input {...field} className="rounded-xl" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="meal_type"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Meal Type
                        </FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger className="rounded-xl">
                              <SelectValue />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent className="rounded-xl">
                            <SelectItem value="breakfast">Breakfast</SelectItem>
                            <SelectItem value="lunch">Lunch</SelectItem>
                            <SelectItem value="dinner">Dinner</SelectItem>
                            <SelectItem value="snack">Snack</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <FormField
                    control={form.control}
                    name="calories"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Calories
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            {...field}
                            value={field.value ?? ""}
                            className="rounded-xl"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="protein_g"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Protein (g)
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            {...field}
                            value={field.value ?? ""}
                            className="rounded-xl"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="carbs_g"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Carbs (g)
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            {...field}
                            value={field.value ?? ""}
                            className="rounded-xl"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="fat_g"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Fat (g)
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            {...field}
                            value={field.value ?? ""}
                            className="rounded-xl"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="fiber_g"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Fiber (g)
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            {...field}
                            value={field.value ?? ""}
                            className="rounded-xl"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="sodium_mg"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Sodium (mg)
                        </FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            {...field}
                            value={field.value ?? ""}
                            className="rounded-xl"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full rounded-xl h-10 mt-2"
                  disabled={createMutation.isPending}
                >
                  {createMutation.isPending ? "Logging..." : "Log Food"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {/* AI Summary */}
      <AIDailySummary date={today} />

      {/* Nutrition + Today's Log */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Nutrition rings — 3 cols */}
        <div
          className="meal-card-enter lg:col-span-3 rounded-2xl border border-border/40 p-6"
          style={{ animationDelay: "0.06s" }}
        >
          <div className="flex items-center gap-2 mb-5">
            <Flame className="h-4 w-4" style={{ color: "rgb(244 114 69 / 0.6)" }} />
            <h2
              className="text-lg font-bold"
              style={{ fontFamily: "'DM Serif Display', serif" }}
            >
              Daily Summary
            </h2>
          </div>
          {summary ? (
            <NutritionRings summary={summary} />
          ) : (
            <p className="text-sm text-muted-foreground/40 font-light py-4">
              No food logged today
            </p>
          )}
        </div>

        {/* Today's log — 2 cols */}
        <div
          className="meal-card-enter lg:col-span-2 rounded-2xl border border-border/40 p-6"
          style={{ animationDelay: "0.12s" }}
        >
          <div className="flex items-center gap-2 mb-5">
            <UtensilsCrossed className="h-4 w-4" style={{ color: "rgb(16 185 129 / 0.6)" }} />
            <h2
              className="text-lg font-bold"
              style={{ fontFamily: "'DM Serif Display', serif" }}
            >
              Today's Log
            </h2>
          </div>
          <div className="space-y-4">
            {Object.entries(MEAL_CONFIG).map(([type, config]) => {
              const mealLogs = grouped[type];
              if (!mealLogs || mealLogs.length === 0) return null;
              const Icon = config.icon;
              return (
                <div key={type}>
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className="h-3.5 w-3.5" style={{ color: config.accent }} />
                    <span
                      className="text-[10px] font-semibold uppercase tracking-widest"
                      style={{ color: config.accent }}
                    >
                      {config.label}
                    </span>
                  </div>
                  <div className="space-y-1.5">
                    {mealLogs.map((log) => (
                      <div
                        key={log.id}
                        className="flex items-center justify-between rounded-xl p-3 transition-colors"
                        style={{ background: config.accentMuted }}
                      >
                        <p className="text-sm font-medium text-foreground/90">
                          {log.food_name}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground/50 font-light">
                          {log.calories && (
                            <span className="tabular-nums">{log.calories} cal</span>
                          )}
                          {log.protein_g && (
                            <span className="tabular-nums">{log.protein_g}g protein</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
            {logs.length === 0 && (
              <p className="text-sm text-muted-foreground/40 font-light text-center py-6">
                No food logged today. Start logging!
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
