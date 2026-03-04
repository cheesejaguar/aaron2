import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Heart, Plus, Scale, Activity } from "lucide-react";
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
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { healthApi } from "@/api/health";
import { BPChart } from "@/components/health/BPChart";
import { WeightChart } from "@/components/health/WeightChart";
import { CholesterolChart } from "@/components/health/CholesterolChart";
import {
  bpLogSchema,
  weightLogSchema,
  cholesterolLogSchema,
  type BPLogFormData,
  type WeightLogFormData,
  type CholesterolLogFormData,
} from "@/lib/validations";

const TIME_RANGES = [
  { value: 7, label: "7 Days" },
  { value: 30, label: "30 Days" },
  { value: 90, label: "90 Days" },
];

const METRIC_TABS = [
  {
    key: "bp",
    label: "Blood Pressure",
    icon: Heart,
    accent: "rgb(239 68 68)",
    accentMuted: "rgb(239 68 68 / 0.08)",
  },
  {
    key: "weight",
    label: "Weight",
    icon: Scale,
    accent: "rgb(96 165 250)",
    accentMuted: "rgb(96 165 250 / 0.08)",
  },
  {
    key: "cholesterol",
    label: "Cholesterol",
    icon: Activity,
    accent: "rgb(245 158 11)",
    accentMuted: "rgb(245 158 11 / 0.08)",
  },
] as const;

export function HealthMetricsPage() {
  const queryClient = useQueryClient();
  const [bpOpen, setBpOpen] = useState(false);
  const [weightOpen, setWeightOpen] = useState(false);
  const [cholOpen, setCholOpen] = useState(false);
  const [timeRange, setTimeRange] = useState(30);
  const [activeTab, setActiveTab] = useState<"bp" | "weight" | "cholesterol">("bp");

  const bpForm = useForm<BPLogFormData>({
    resolver: zodResolver(bpLogSchema),
    defaultValues: { systolic: 120, diastolic: 80 },
  });

  const weightForm = useForm<WeightLogFormData>({
    resolver: zodResolver(weightLogSchema),
    defaultValues: { weight_lbs: 0 },
  });

  const cholForm = useForm<CholesterolLogFormData>({
    resolver: zodResolver(cholesterolLogSchema),
    defaultValues: { total_mg_dl: 0 },
  });

  const { data: bpLogs = [] } = useQuery({
    queryKey: ["health", "bp", timeRange],
    queryFn: () => healthApi.listBP(timeRange),
  });

  const { data: weightLogs = [] } = useQuery({
    queryKey: ["health", "weight", timeRange],
    queryFn: () => healthApi.listWeight(timeRange),
  });

  const { data: cholLogs = [] } = useQuery({
    queryKey: ["health", "cholesterol", timeRange],
    queryFn: () => healthApi.listCholesterol(timeRange),
  });

  const bpMutation = useMutation({
    mutationFn: healthApi.createBP,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["health"] });
      setBpOpen(false);
      bpForm.reset();
      toast.success("Blood pressure logged");
    },
  });

  const weightMutation = useMutation({
    mutationFn: healthApi.createWeight,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["health"] });
      setWeightOpen(false);
      weightForm.reset();
      toast.success("Weight logged");
    },
  });

  const cholMutation = useMutation({
    mutationFn: healthApi.createCholesterol,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["health"] });
      setCholOpen(false);
      cholForm.reset();
      toast.success("Cholesterol logged");
    },
  });

  const activeConfig = METRIC_TABS.find((t) => t.key === activeTab)!;

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1
            className="text-4xl font-bold tracking-tight"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Health Metrics
          </h1>
          <p className="mt-2 text-sm text-muted-foreground/50 font-light">
            Track blood pressure, weight & cholesterol
          </p>
        </div>

        {/* Time range selector */}
        <div className="flex items-center gap-1 rounded-xl border border-border/40 p-1">
          {TIME_RANGES.map((range) => (
            <button
              key={range.value}
              onClick={() => setTimeRange(range.value)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                timeRange === range.value
                  ? "bg-foreground/10 text-foreground"
                  : "text-muted-foreground/50 hover:text-muted-foreground"
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Metric tabs */}
      <div className="flex items-center gap-2">
        {METRIC_TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`meal-card-enter flex items-center gap-2 px-4 py-2.5 rounded-xl border transition-all duration-200 ${
                isActive
                  ? "border-border/70 shadow-lg shadow-black/10"
                  : "border-border/30 hover:border-border/50"
              }`}
              style={{
                background: isActive
                  ? `linear-gradient(145deg, ${tab.accentMuted} 0%, transparent 60%)`
                  : undefined,
              }}
            >
              <Icon
                className="h-4 w-4"
                style={{ color: isActive ? tab.accent : "rgb(148 163 184 / 0.5)" }}
              />
              <span
                className={`text-sm font-medium ${
                  isActive ? "text-foreground" : "text-muted-foreground/50"
                }`}
              >
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active metric content */}
      {activeTab === "bp" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Dialog open={bpOpen} onOpenChange={setBpOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2 rounded-xl h-10 px-4">
                  <Plus className="h-4 w-4" /> Log BP
                </Button>
              </DialogTrigger>
              <DialogContent className="rounded-2xl">
                <DialogHeader>
                  <DialogTitle
                    className="text-xl"
                    style={{ fontFamily: "'DM Serif Display', serif" }}
                  >
                    Log Blood Pressure
                  </DialogTitle>
                </DialogHeader>
                <Form {...bpForm}>
                  <form
                    onSubmit={bpForm.handleSubmit((data) => bpMutation.mutate(data))}
                    className="space-y-4 mt-2"
                  >
                    <div className="grid grid-cols-3 gap-4">
                      <FormField
                        control={bpForm.control}
                        name="systolic"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                              Systolic
                            </FormLabel>
                            <FormControl>
                              <Input type="number" {...field} className="rounded-xl" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={bpForm.control}
                        name="diastolic"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                              Diastolic
                            </FormLabel>
                            <FormControl>
                              <Input type="number" {...field} className="rounded-xl" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={bpForm.control}
                        name="pulse"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                              Pulse
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
                    <FormField
                      control={bpForm.control}
                      name="notes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                            Notes
                          </FormLabel>
                          <FormControl>
                            <Input {...field} value={field.value ?? ""} className="rounded-xl" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button
                      type="submit"
                      className="w-full rounded-xl h-10"
                      disabled={bpMutation.isPending}
                    >
                      {bpMutation.isPending ? "Saving..." : "Save"}
                    </Button>
                  </form>
                </Form>
              </DialogContent>
            </Dialog>
          </div>
          <div
            className="meal-card-enter rounded-2xl border border-border/40 p-6"
            style={{
              animationDelay: "0.06s",
              background: `linear-gradient(145deg, ${activeConfig.accentMuted} 0%, transparent 50%)`,
            }}
          >
            <div className="flex items-center gap-2 mb-5">
              <Heart className="h-4 w-4" style={{ color: "rgb(239 68 68 / 0.6)" }} />
              <h2
                className="text-lg font-bold"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                Blood Pressure Trend
              </h2>
            </div>
            {bpLogs.length > 0 ? (
              <BPChart data={bpLogs} />
            ) : (
              <p className="text-sm text-muted-foreground/40 font-light py-8 text-center">
                No readings yet
              </p>
            )}
          </div>
        </div>
      )}

      {activeTab === "weight" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Dialog open={weightOpen} onOpenChange={setWeightOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2 rounded-xl h-10 px-4">
                  <Plus className="h-4 w-4" /> Log Weight
                </Button>
              </DialogTrigger>
              <DialogContent className="rounded-2xl">
                <DialogHeader>
                  <DialogTitle
                    className="text-xl"
                    style={{ fontFamily: "'DM Serif Display', serif" }}
                  >
                    Log Weight
                  </DialogTitle>
                </DialogHeader>
                <Form {...weightForm}>
                  <form
                    onSubmit={weightForm.handleSubmit((data) => weightMutation.mutate(data))}
                    className="space-y-4 mt-2"
                  >
                    <FormField
                      control={weightForm.control}
                      name="weight_lbs"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                            Weight (lbs)
                          </FormLabel>
                          <FormControl>
                            <Input type="number" step="0.1" {...field} className="rounded-xl" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={weightForm.control}
                      name="notes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                            Notes
                          </FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              value={field.value ?? ""}
                              className="rounded-xl"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button
                      type="submit"
                      className="w-full rounded-xl h-10"
                      disabled={weightMutation.isPending}
                    >
                      {weightMutation.isPending ? "Saving..." : "Save"}
                    </Button>
                  </form>
                </Form>
              </DialogContent>
            </Dialog>
          </div>
          <div
            className="meal-card-enter rounded-2xl border border-border/40 p-6"
            style={{
              animationDelay: "0.06s",
              background: `linear-gradient(145deg, ${activeConfig.accentMuted} 0%, transparent 50%)`,
            }}
          >
            <div className="flex items-center gap-2 mb-5">
              <Scale className="h-4 w-4" style={{ color: "rgb(96 165 250 / 0.6)" }} />
              <h2
                className="text-lg font-bold"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                Weight Trend
              </h2>
            </div>
            {weightLogs.length > 0 ? (
              <WeightChart data={weightLogs} />
            ) : (
              <p className="text-sm text-muted-foreground/40 font-light py-8 text-center">
                No readings yet
              </p>
            )}
          </div>
        </div>
      )}

      {activeTab === "cholesterol" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Dialog open={cholOpen} onOpenChange={setCholOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2 rounded-xl h-10 px-4">
                  <Plus className="h-4 w-4" /> Log Cholesterol
                </Button>
              </DialogTrigger>
              <DialogContent className="rounded-2xl">
                <DialogHeader>
                  <DialogTitle
                    className="text-xl"
                    style={{ fontFamily: "'DM Serif Display', serif" }}
                  >
                    Log Cholesterol
                  </DialogTitle>
                </DialogHeader>
                <Form {...cholForm}>
                  <form
                    onSubmit={cholForm.handleSubmit((data) => cholMutation.mutate(data))}
                    className="space-y-4 mt-2"
                  >
                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={cholForm.control}
                        name="total_mg_dl"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                              Total (mg/dL)
                            </FormLabel>
                            <FormControl>
                              <Input type="number" {...field} className="rounded-xl" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={cholForm.control}
                        name="ldl"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                              LDL
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
                        control={cholForm.control}
                        name="hdl"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                              HDL
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
                        control={cholForm.control}
                        name="triglycerides"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                              Triglycerides
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
                      className="w-full rounded-xl h-10"
                      disabled={cholMutation.isPending}
                    >
                      {cholMutation.isPending ? "Saving..." : "Save"}
                    </Button>
                  </form>
                </Form>
              </DialogContent>
            </Dialog>
          </div>
          <div
            className="meal-card-enter rounded-2xl border border-border/40 p-6"
            style={{
              animationDelay: "0.06s",
              background: `linear-gradient(145deg, ${activeConfig.accentMuted} 0%, transparent 50%)`,
            }}
          >
            <div className="flex items-center gap-2 mb-5">
              <Activity className="h-4 w-4" style={{ color: "rgb(245 158 11 / 0.6)" }} />
              <h2
                className="text-lg font-bold"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                Cholesterol Trend
              </h2>
            </div>
            {cholLogs.length > 0 ? (
              <CholesterolChart data={cholLogs} />
            ) : (
              <p className="text-sm text-muted-foreground/40 font-light py-8 text-center">
                No readings yet
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
