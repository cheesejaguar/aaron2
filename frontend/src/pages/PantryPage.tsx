import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import {
  Plus,
  Search,
  Trash2,
  Minus,
  Package,
  Apple,
  Beef,
  Milk,
  Wheat,
  Snowflake,
  Cookie,
  Droplets,
  ShoppingBasket,
  Clock,
  AlertTriangle,
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
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { pantryApi } from "@/api/pantry";
import { ReceiptUploadDialog } from "@/components/pantry/ReceiptUploadDialog";
import { pantryItemSchema, type PantryItemFormData } from "@/lib/validations";
import type { PantryItem } from "@/types";

const CATEGORY_CONFIG: Record<
  string,
  { icon: typeof Package; accent: string; accentMuted: string }
> = {
  produce: {
    icon: Apple,
    accent: "rgb(16 185 129)",
    accentMuted: "rgb(16 185 129 / 0.08)",
  },
  meat: {
    icon: Beef,
    accent: "rgb(239 68 68)",
    accentMuted: "rgb(239 68 68 / 0.08)",
  },
  dairy: {
    icon: Milk,
    accent: "rgb(96 165 250)",
    accentMuted: "rgb(96 165 250 / 0.08)",
  },
  grains: {
    icon: Wheat,
    accent: "rgb(245 158 11)",
    accentMuted: "rgb(245 158 11 / 0.08)",
  },
  frozen: {
    icon: Snowflake,
    accent: "rgb(34 211 238)",
    accentMuted: "rgb(34 211 238 / 0.08)",
  },
  snacks: {
    icon: Cookie,
    accent: "rgb(167 139 250)",
    accentMuted: "rgb(167 139 250 / 0.08)",
  },
  beverages: {
    icon: Droplets,
    accent: "rgb(56 189 248)",
    accentMuted: "rgb(56 189 248 / 0.08)",
  },
  canned: {
    icon: Package,
    accent: "rgb(251 146 60)",
    accentMuted: "rgb(251 146 60 / 0.08)",
  },
  condiments: {
    icon: Droplets,
    accent: "rgb(244 114 69)",
    accentMuted: "rgb(244 114 69 / 0.08)",
  },
  other: {
    icon: ShoppingBasket,
    accent: "rgb(148 163 184)",
    accentMuted: "rgb(148 163 184 / 0.08)",
  },
};

function getCategoryConfig(category: string) {
  const key = category.toLowerCase();
  return (
    CATEGORY_CONFIG[key] ||
    // fuzzy match
    Object.entries(CATEGORY_CONFIG).find(([k]) => key.includes(k))?.[1] ||
    CATEGORY_CONFIG.other
  );
}

function getExpiryStatus(expiry: string | null | undefined): "expired" | "soon" | "ok" | null {
  if (!expiry) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const exp = new Date(expiry + "T00:00:00");
  if (exp < today) return "expired";
  const threeDays = new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000);
  if (exp <= threeDays) return "soon";
  return "ok";
}

function formatExpiry(expiry: string): string {
  const d = new Date(expiry + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function PantryItemCard({
  item,
  accentMuted,
  delay,
  onConsume,
  onDelete,
}: {
  item: PantryItem;
  accentMuted: string;
  delay: number;
  onConsume: () => void;
  onDelete: () => void;
}) {
  const expiryStatus = getExpiryStatus(item.estimated_expiry);
  const isLowStock =
    item.low_stock_threshold != null && item.quantity <= item.low_stock_threshold;

  return (
    <div
      className="meal-card-enter group rounded-xl border border-border/40 p-4 transition-all duration-200 hover:border-border/70 hover:shadow-lg hover:shadow-black/10"
      style={{
        animationDelay: `${delay}s`,
        background: `linear-gradient(145deg, ${accentMuted} 0%, transparent 60%)`,
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-medium leading-snug text-foreground/90 truncate">
            {item.name}
          </h3>
          <div className="flex items-baseline gap-1.5 mt-1">
            <span
              className="text-lg font-bold tabular-nums"
              style={{ fontFamily: "'DM Serif Display', serif" }}
            >
              {item.quantity}
            </span>
            <span className="text-xs text-muted-foreground/50 font-light">
              {item.unit || "units"}
            </span>
          </div>
        </div>

        {/* Actions — visible on hover */}
        <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-150 shrink-0">
          <button
            onClick={onConsume}
            className="h-7 w-7 rounded-lg flex items-center justify-center text-muted-foreground/50 hover:text-foreground/80 hover:bg-muted/40 transition-colors"
            title="Use one"
          >
            <Minus className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={onDelete}
            className="h-7 w-7 rounded-lg flex items-center justify-center text-muted-foreground/50 hover:text-red-400 hover:bg-red-500/10 transition-colors"
            title="Remove"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Status pills */}
      {(isLowStock || (expiryStatus && expiryStatus !== "ok")) && (
        <div className="flex items-center gap-2 mt-3">
          {isLowStock && (
            <span
              className="inline-flex items-center gap-1 text-[9px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full"
              style={{ color: "rgb(245 158 11)", background: "rgb(245 158 11 / 0.1)" }}
            >
              <AlertTriangle className="h-2.5 w-2.5" />
              Low
            </span>
          )}
          {expiryStatus === "expired" && (
            <span
              className="inline-flex items-center gap-1 text-[9px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full"
              style={{ color: "rgb(239 68 68)", background: "rgb(239 68 68 / 0.1)" }}
            >
              <Clock className="h-2.5 w-2.5" />
              Expired
            </span>
          )}
          {expiryStatus === "soon" && item.estimated_expiry && (
            <span
              className="inline-flex items-center gap-1 text-[9px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full"
              style={{ color: "rgb(251 146 60)", background: "rgb(251 146 60 / 0.1)" }}
            >
              <Clock className="h-2.5 w-2.5" />
              Exp {formatExpiry(item.estimated_expiry)}
            </span>
          )}
        </div>
      )}

      {/* Normal expiry — subtle */}
      {expiryStatus === "ok" && item.estimated_expiry && (
        <p className="mt-2 text-[10px] text-muted-foreground/35 font-light">
          Exp {formatExpiry(item.estimated_expiry)}
        </p>
      )}
    </div>
  );
}

export function PantryPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [addOpen, setAddOpen] = useState(false);

  const form = useForm<PantryItemFormData>({
    resolver: zodResolver(pantryItemSchema),
    defaultValues: { name: "", quantity: 1, category: "", unit: "" },
  });

  const { data: items = [] } = useQuery({
    queryKey: ["pantry"],
    queryFn: pantryApi.list,
  });

  const createMutation = useMutation({
    mutationFn: pantryApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
      setAddOpen(false);
      form.reset();
      toast.success("Item added");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: pantryApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
      toast.success("Item removed");
    },
  });

  const consumeMutation = useMutation({
    mutationFn: ({ id, quantity }: { id: string; quantity: number }) =>
      pantryApi.consume(id, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
    },
  });

  const filtered = items.filter(
    (item) =>
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.category?.toLowerCase().includes(search.toLowerCase())
  );

  const grouped = filtered.reduce(
    (acc, item) => {
      const cat = item.category || "Other";
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(item);
      return acc;
    },
    {} as Record<string, typeof items>
  );

  // Sort categories alphabetically, "Other" last
  const sortedCategories = Object.keys(grouped).sort((a, b) => {
    if (a === "Other") return 1;
    if (b === "Other") return -1;
    return a.localeCompare(b);
  });

  const totalItems = items.length;
  const lowStockCount = items.filter(
    (i) => i.low_stock_threshold != null && i.quantity <= i.low_stock_threshold
  ).length;
  const expiringCount = items.filter((i) => {
    const s = getExpiryStatus(i.estimated_expiry);
    return s === "soon" || s === "expired";
  }).length;

  const onSubmit = (data: PantryItemFormData) => {
    createMutation.mutate(data);
  };

  let cardIndex = 0;

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1
            className="text-4xl font-bold tracking-tight"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Pantry
          </h1>
          <div className="flex items-center gap-4 mt-2">
            <span className="text-sm text-muted-foreground/50 font-light">
              {totalItems} item{totalItems !== 1 ? "s" : ""}
            </span>
            {lowStockCount > 0 && (
              <span className="text-xs font-medium" style={{ color: "rgb(245 158 11)" }}>
                {lowStockCount} low stock
              </span>
            )}
            {expiringCount > 0 && (
              <span className="text-xs font-medium" style={{ color: "rgb(251 146 60)" }}>
                {expiringCount} expiring
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <ReceiptUploadDialog />
          <Dialog open={addOpen} onOpenChange={setAddOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2 rounded-xl h-10 px-4">
                <Plus className="h-4 w-4" />
                Add Item
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md rounded-2xl">
              <DialogHeader>
                <DialogTitle
                  className="text-xl"
                  style={{ fontFamily: "'DM Serif Display', serif" }}
                >
                  Add Pantry Item
                </DialogTitle>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mt-2">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Name
                        </FormLabel>
                        <FormControl>
                          <Input {...field} className="rounded-xl" placeholder="e.g. Chicken Breast" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="quantity"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                            Quantity
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
                      name="unit"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                            Unit
                          </FormLabel>
                          <FormControl>
                            <Input {...field} className="rounded-xl" placeholder="lbs, oz..." />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <FormField
                    control={form.control}
                    name="category"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                          Category
                        </FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            className="rounded-xl"
                            placeholder="produce, dairy, meat..."
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button
                    type="submit"
                    className="w-full rounded-xl h-10 mt-2"
                    disabled={createMutation.isPending}
                  >
                    {createMutation.isPending ? "Adding..." : "Add Item"}
                  </Button>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground/40" />
        <Input
          placeholder="Search items or categories..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-11 h-11 rounded-xl border-border/40 bg-muted/20 focus:bg-background transition-colors"
        />
      </div>

      {/* Category sections */}
      {sortedCategories.map((category, catIdx) => {
        const config = getCategoryConfig(category);
        const Icon = config.icon;
        const categoryItems = grouped[category];

        return (
          <div key={category} className="space-y-3">
            {/* Category header */}
            <div
              className="meal-card-enter flex items-center gap-2.5 px-1"
              style={{ animationDelay: `${catIdx * 0.06}s` }}
            >
              <Icon className="h-4 w-4" style={{ color: config.accent }} />
              <h2
                className="text-[11px] font-semibold uppercase tracking-widest"
                style={{ color: config.accent }}
              >
                {category}
              </h2>
              <span className="text-[10px] text-muted-foreground/30 font-light ml-1">
                {categoryItems.length}
              </span>
            </div>

            {/* Items grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {categoryItems.map((item) => {
                const idx = cardIndex++;
                return (
                  <PantryItemCard
                    key={item.id}
                    item={item}
                    accentMuted={config.accentMuted}
                    delay={0.04 + idx * 0.03}
                    onConsume={() => consumeMutation.mutate({ id: item.id, quantity: 1 })}
                    onDelete={() => deleteMutation.mutate(item.id)}
                  />
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Empty state */}
      {filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="relative mb-6">
            <div
              className="absolute inset-0 rounded-full blur-2xl opacity-20"
              style={{
                background:
                  "radial-gradient(circle, rgb(16 185 129 / 0.5), rgb(245 158 11 / 0.3), rgb(96 165 250 / 0.3))",
              }}
            />
            <ShoppingBasket className="h-16 w-16 text-muted-foreground/40 relative" />
          </div>
          <h2
            className="text-2xl font-bold text-foreground/80 mb-2"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            {search ? "No matches" : "Your pantry is empty"}
          </h2>
          <p className="text-sm text-muted-foreground/60 max-w-sm font-light leading-relaxed">
            {search
              ? "Try a different search term"
              : "Add items manually or upload a grocery receipt to get started."}
          </p>
        </div>
      )}
    </div>
  );
}
