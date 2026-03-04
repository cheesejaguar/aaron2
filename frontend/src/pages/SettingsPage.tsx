import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Save, User, Target } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { authApi } from "@/api/auth";
import { settingsSchema, type SettingsFormData } from "@/lib/validations";

const DIETARY_OPTIONS = [
  "DASH Diet",
  "Low Sodium",
  "High Fiber",
  "Heart Healthy",
  "Mediterranean",
];

export function SettingsPage() {
  const queryClient = useQueryClient();
  const [selectedPrefs, setSelectedPrefs] = useState<string[]>([]);

  const { data: user } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: authApi.getMe,
  });

  const form = useForm<SettingsFormData>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      name: "",
      health_goals_json: {
        dietary_preferences: [],
        health_focus: "",
        calorie_target: 2000,
      },
    },
  });

  useEffect(() => {
    if (user) {
      form.reset({
        name: user.name,
        health_goals_json: {
          dietary_preferences:
            (user.health_goals_json?.dietary_preferences as string[]) || [],
          health_focus: (user.health_goals_json?.health_focus as string) || "",
          calorie_target:
            (user.health_goals_json?.calorie_target as number) || 2000,
        },
      });
      setSelectedPrefs(
        (user.health_goals_json?.dietary_preferences as string[]) || []
      );
    }
  }, [user, form]);

  const mutation = useMutation({
    mutationFn: authApi.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      toast.success("Settings saved");
    },
    onError: () => toast.error("Failed to save settings"),
  });

  const togglePref = (pref: string) => {
    const next = selectedPrefs.includes(pref)
      ? selectedPrefs.filter((p) => p !== pref)
      : [...selectedPrefs, pref];
    setSelectedPrefs(next);
    form.setValue("health_goals_json.dietary_preferences", next);
  };

  const onSubmit = (data: SettingsFormData) => {
    mutation.mutate({
      name: data.name,
      health_goals_json: {
        ...data.health_goals_json,
        dietary_preferences: selectedPrefs,
      },
    });
  };

  return (
    <div className="space-y-8 max-w-2xl">
      {/* Header */}
      <div>
        <h1
          className="text-4xl font-bold tracking-tight"
          style={{ fontFamily: "'DM Serif Display', serif" }}
        >
          Settings
        </h1>
        <p className="mt-2 text-sm text-muted-foreground/50 font-light">
          Manage your profile and health goals
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Profile section */}
          <div
            className="meal-card-enter rounded-2xl border border-border/40 p-6"
            style={{
              animationDelay: "0s",
              background:
                "linear-gradient(145deg, rgb(96 165 250 / 0.05) 0%, transparent 50%)",
            }}
          >
            <div className="flex items-center gap-2 mb-5">
              <User className="h-4 w-4" style={{ color: "rgb(96 165 250 / 0.6)" }} />
              <h2
                className="text-lg font-bold"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                Profile
              </h2>
            </div>
            <div className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                      Name
                    </FormLabel>
                    <FormControl>
                      <Input {...field} className="rounded-xl" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                  Email
                </label>
                <Input
                  value={user?.email || ""}
                  readOnly
                  className="rounded-xl opacity-50"
                />
              </div>
            </div>
          </div>

          {/* Health Goals section */}
          <div
            className="meal-card-enter rounded-2xl border border-border/40 p-6"
            style={{
              animationDelay: "0.06s",
              background:
                "linear-gradient(145deg, rgb(16 185 129 / 0.05) 0%, transparent 50%)",
            }}
          >
            <div className="flex items-center gap-2 mb-5">
              <Target className="h-4 w-4" style={{ color: "rgb(16 185 129 / 0.6)" }} />
              <h2
                className="text-lg font-bold"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                Health Goals
              </h2>
            </div>
            <div className="space-y-4">
              <FormField
                control={form.control}
                name="health_goals_json.calorie_target"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                      Target Daily Calories
                    </FormLabel>
                    <FormControl>
                      <Input type="number" {...field} className="rounded-xl" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="health_goals_json.health_focus"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                      Health Focus
                    </FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="e.g., lower blood pressure, weight loss"
                        className="rounded-xl"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                  Dietary Preferences
                </label>
                <div className="flex flex-wrap gap-2">
                  {DIETARY_OPTIONS.map((pref) => {
                    const isSelected = selectedPrefs.includes(pref);
                    return (
                      <button
                        key={pref}
                        type="button"
                        onClick={() => togglePref(pref)}
                        className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
                          isSelected
                            ? "border-emerald-500/50 text-emerald-400"
                            : "border-border/40 text-muted-foreground/50 hover:border-border/70 hover:text-muted-foreground"
                        }`}
                        style={{
                          background: isSelected
                            ? "rgb(16 185 129 / 0.08)"
                            : undefined,
                        }}
                      >
                        {pref}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          <Button
            type="submit"
            className="w-full rounded-xl h-10 gap-2"
            disabled={mutation.isPending}
          >
            <Save className="h-4 w-4" />
            {mutation.isPending ? "Saving..." : "Save Settings"}
          </Button>
        </form>
      </Form>
    </div>
  );
}
