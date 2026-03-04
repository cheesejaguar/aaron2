import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Search,
  Sparkles,
  Link as LinkIcon,
  ChefHat,
  ShoppingCart,
  Minus,
  Plus,
  Flame,
  Leaf,
  Clock,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { recipesApi } from "@/api/recipes";
import type { Recipe, RecipeGenerateRequest } from "@/types";

type Ingredient = { name: string; quantity: string; unit: string };

function parseQuantity(q: string): number {
  if (!q) return 0;
  // Handle fractions like "1/2", "1 1/2"
  const parts = q.trim().split(/\s+/);
  let total = 0;
  for (const part of parts) {
    if (part.includes("/")) {
      const [num, den] = part.split("/");
      total += Number(num) / Number(den);
    } else {
      total += Number(part) || 0;
    }
  }
  return total;
}

function formatQuantity(n: number): string {
  if (n === 0) return "";
  if (Number.isInteger(n)) return String(n);
  // Common fractions
  const frac = n % 1;
  const whole = Math.floor(n);
  const fractions: [number, string][] = [
    [0.25, "\u00BC"],
    [0.333, "\u2153"],
    [0.5, "\u00BD"],
    [0.667, "\u2154"],
    [0.75, "\u00BE"],
  ];
  for (const [val, sym] of fractions) {
    if (Math.abs(frac - val) < 0.05) {
      return whole > 0 ? `${whole} ${sym}` : sym;
    }
  }
  return n.toFixed(1).replace(/\.0$/, "");
}

function scaleIngredient(ing: Ingredient, multiplier: number): string {
  const qty = parseQuantity(ing.quantity);
  if (qty === 0) return `${ing.name}`;
  const scaled = qty * multiplier;
  const formattedQty = formatQuantity(scaled);
  return `${formattedQty} ${ing.unit} ${ing.name}`.trim();
}

function RecipeDetailModal({
  recipe,
  open,
  onOpenChange,
  onAddToShoppingList,
  onGenerateFull,
  isGenerating,
}: {
  recipe: Recipe;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAddToShoppingList: () => void;
  onGenerateFull: () => void;
  isGenerating: boolean;
}) {
  const [servings, setServings] = useState(1);
  const hasFullRecipe =
    recipe.ingredients_json && recipe.ingredients_json.length > 0;
  const hasSteps = recipe.steps_json && recipe.steps_json.length > 0;
  const nutrition = recipe.nutrition_per_serving_json;

  // Scale nutrition by servings
  const scaledNutrition = nutrition
    ? Object.fromEntries(
        Object.entries(nutrition).map(([k, v]) => [k, Math.round(v * servings)])
      )
    : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl p-0 overflow-hidden rounded-2xl border-border/50">
        <DialogDescription className="sr-only">
          Recipe details for {recipe.title}
        </DialogDescription>
        <ScrollArea className="max-h-[85vh]">
          <div className="p-8">
            {/* Header */}
            <DialogHeader className="space-y-3 mb-6">
              <div className="flex items-start justify-between gap-4">
                <DialogTitle
                  className="text-2xl leading-tight pr-4"
                  style={{ fontFamily: "'DM Serif Display', serif" }}
                >
                  {recipe.title}
                </DialogTitle>
              </div>
              {recipe.description && (
                <p className="text-sm text-muted-foreground/80 font-light leading-relaxed">
                  {recipe.description}
                </p>
              )}
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                {recipe.health_tags?.map((tag) => (
                  <span
                    key={tag}
                    className="text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded-full"
                    style={{
                      color: "rgb(16 185 129)",
                      background: "rgb(16 185 129 / 0.1)",
                    }}
                  >
                    {tag}
                  </span>
                ))}
                {recipe.is_ai_generated && (
                  <span
                    className="text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded-full"
                    style={{
                      color: "rgb(167 139 250)",
                      background: "rgb(167 139 250 / 0.1)",
                    }}
                  >
                    AI Generated
                  </span>
                )}
                {recipe.source_url && (
                  <a
                    href={recipe.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded-full inline-flex items-center gap-1 hover:opacity-80 transition-opacity"
                    style={{
                      color: "rgb(96 165 250)",
                      background: "rgb(96 165 250 / 0.1)",
                    }}
                  >
                    <ExternalLink className="h-2.5 w-2.5" />
                    Source
                  </a>
                )}
              </div>
            </DialogHeader>

            {/* Stub recipe — no ingredients/steps */}
            {!hasFullRecipe && !hasSteps && (
              <div className="py-8 text-center space-y-4">
                <div className="relative inline-block">
                  <div
                    className="absolute inset-0 rounded-full blur-xl opacity-20"
                    style={{
                      background:
                        "radial-gradient(circle, rgb(245 158 11 / 0.5), rgb(16 185 129 / 0.3))",
                    }}
                  />
                  <ChefHat className="h-12 w-12 text-muted-foreground/30 relative" />
                </div>
                <p className="text-sm text-muted-foreground/60 font-light max-w-xs mx-auto">
                  This recipe was bookmarked without full details. Generate the
                  complete recipe with ingredients and step-by-step
                  instructions.
                </p>
                <Button
                  onClick={onGenerateFull}
                  disabled={isGenerating}
                  className="gap-2 rounded-xl"
                >
                  <Sparkles
                    className={`h-4 w-4 ${isGenerating ? "generating-pulse" : ""}`}
                  />
                  {isGenerating
                    ? "Generating..."
                    : "Generate Full Recipe"}
                </Button>
              </div>
            )}

            {/* Serving adjuster + nutrition */}
            {(hasFullRecipe || scaledNutrition) && (
              <>
                <div className="flex items-center justify-between py-4">
                  {/* Serving control */}
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
                      Servings
                    </span>
                    <div className="flex items-center gap-0 bg-muted/30 rounded-lg border border-border/50">
                      <button
                        onClick={() =>
                          setServings((s) => Math.max(1, s - 1))
                        }
                        className="px-2.5 py-1.5 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        <Minus className="h-3.5 w-3.5" />
                      </button>
                      <span className="px-3 py-1.5 text-sm font-semibold tabular-nums min-w-[2rem] text-center">
                        {servings}
                      </span>
                      <button
                        onClick={() => setServings((s) => s + 1)}
                        className="px-2.5 py-1.5 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        <Plus className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Quick nutrition */}
                  {scaledNutrition && (
                    <div className="flex items-center gap-4 text-xs text-muted-foreground/60">
                      {scaledNutrition.calories != null && (
                        <span className="flex items-center gap-1">
                          <Flame className="h-3 w-3" style={{ color: "rgb(244 114 69)" }} />
                          <span className="tabular-nums font-medium">
                            {scaledNutrition.calories}
                          </span>{" "}
                          cal
                        </span>
                      )}
                      {scaledNutrition.protein_g != null && (
                        <span className="tabular-nums">
                          <span className="font-medium">{scaledNutrition.protein_g}g</span>{" "}
                          protein
                        </span>
                      )}
                      {scaledNutrition.sodium_mg != null && (
                        <span className="tabular-nums">
                          <span className="font-medium">{scaledNutrition.sodium_mg}</span>{" "}
                          mg sodium
                        </span>
                      )}
                    </div>
                  )}
                </div>
                <Separator className="opacity-30" />
              </>
            )}

            {/* Ingredients */}
            {hasFullRecipe && (
              <div className="py-5">
                <h3
                  className="text-base font-bold mb-4"
                  style={{ fontFamily: "'DM Serif Display', serif" }}
                >
                  Ingredients
                </h3>
                <ul className="space-y-2.5">
                  {(recipe.ingredients_json as Ingredient[]).map(
                    (ing, i) => (
                      <li key={i} className="flex items-baseline gap-3 text-sm">
                        <span
                          className="shrink-0 w-1.5 h-1.5 rounded-full mt-1.5"
                          style={{ background: "rgb(16 185 129 / 0.5)" }}
                        />
                        <span className="font-light leading-relaxed">
                          {scaleIngredient(ing, servings)}
                        </span>
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}

            {/* Steps */}
            {hasSteps && (
              <>
                {hasFullRecipe && <Separator className="opacity-30" />}
                <div className="py-5">
                  <h3
                    className="text-base font-bold mb-5"
                    style={{ fontFamily: "'DM Serif Display', serif" }}
                  >
                    Instructions
                  </h3>
                  <ol className="space-y-5">
                    {recipe.steps_json!.map((step, i) => (
                      <li key={i} className="flex gap-4">
                        <span
                          className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                          style={{
                            color: "rgb(245 158 11)",
                            background: "rgb(245 158 11 / 0.1)",
                          }}
                        >
                          {i + 1}
                        </span>
                        <p className="text-sm font-light leading-relaxed pt-1 text-foreground/85">
                          {step}
                        </p>
                      </li>
                    ))}
                  </ol>
                </div>
              </>
            )}

            {/* Actions */}
            {hasFullRecipe && (
              <>
                <Separator className="opacity-30" />
                <div className="pt-5">
                  <Button
                    variant="outline"
                    className="w-full gap-2 rounded-xl h-10"
                    onClick={onAddToShoppingList}
                  >
                    <ShoppingCart className="h-4 w-4" />
                    Add Ingredients to Shopping List
                  </Button>
                </div>
              </>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}

export function RecipesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [genOpen, setGenOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [importUrl, setImportUrl] = useState("");
  const [genRequest, setGenRequest] = useState<RecipeGenerateRequest>({});
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);

  const { data: recipes = [] } = useQuery({
    queryKey: ["recipes"],
    queryFn: recipesApi.list,
  });

  const generateMutation = useMutation({
    mutationFn: recipesApi.generate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      setGenOpen(false);
      toast.success("Recipe generated!");
    },
    onError: () => toast.error("Failed to generate recipe"),
  });

  const generateFullMutation = useMutation({
    mutationFn: recipesApi.generate,
    onSuccess: (newRecipe) => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      setSelectedRecipe(newRecipe);
      toast.success("Full recipe generated!");
    },
    onError: () => toast.error("Failed to generate recipe"),
  });

  const addToShoppingMutation = useMutation({
    mutationFn: recipesApi.addToShoppingList,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["shopping-lists"] });
      toast.success(data.message);
    },
    onError: () => toast.error("Failed to add to shopping list"),
  });

  const importMutation = useMutation({
    mutationFn: recipesApi.importUrl,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      setImportOpen(false);
      setImportUrl("");
      toast.success("Recipe imported!");
    },
    onError: () => toast.error("Failed to import recipe"),
  });

  const filtered = recipes.filter((r) =>
    r.title.toLowerCase().includes(search.toLowerCase())
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
            Recipes
          </h1>
          <p className="mt-2 text-muted-foreground text-sm font-light">
            {recipes.length} recipe{recipes.length !== 1 ? "s" : ""} in your
            collection
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog open={importOpen} onOpenChange={setImportOpen}>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                className="gap-2 rounded-xl h-10 px-4 border-border/50"
              >
                <LinkIcon className="h-4 w-4" />
                Import URL
              </Button>
            </DialogTrigger>
            <DialogContent className="rounded-2xl">
              <DialogHeader>
                <DialogTitle
                  style={{ fontFamily: "'DM Serif Display', serif" }}
                >
                  Import Recipe from URL
                </DialogTitle>
                <DialogDescription>
                  Paste a link to any recipe page and we'll extract the details.
                </DialogDescription>
              </DialogHeader>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  importMutation.mutate(importUrl);
                }}
                className="space-y-4"
              >
                <div className="space-y-2">
                  <Label className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Recipe URL
                  </Label>
                  <Input
                    value={importUrl}
                    onChange={(e) => setImportUrl(e.target.value)}
                    placeholder="https://..."
                    required
                    className="rounded-xl"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full rounded-xl h-10"
                  disabled={importMutation.isPending}
                >
                  {importMutation.isPending ? "Importing..." : "Import"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={genOpen} onOpenChange={setGenOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2 rounded-xl h-10 px-5 shadow-lg shadow-primary/20">
                <Sparkles className="h-4 w-4" />
                Generate
              </Button>
            </DialogTrigger>
            <DialogContent className="rounded-2xl">
              <DialogHeader>
                <DialogTitle
                  style={{ fontFamily: "'DM Serif Display', serif" }}
                >
                  Generate AI Recipe
                </DialogTitle>
                <DialogDescription>
                  Create a DASH-friendly recipe tailored to your pantry and
                  preferences.
                </DialogDescription>
              </DialogHeader>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  generateMutation.mutate(genRequest);
                }}
                className="space-y-4"
              >
                <div className="space-y-2">
                  <Label className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Health Focus
                  </Label>
                  <Input
                    value={genRequest.health_focus || ""}
                    onChange={(e) =>
                      setGenRequest({
                        ...genRequest,
                        health_focus: e.target.value,
                      })
                    }
                    placeholder="e.g., low sodium, heart healthy"
                    className="rounded-xl"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Cuisine
                  </Label>
                  <Input
                    value={genRequest.cuisine || ""}
                    onChange={(e) =>
                      setGenRequest({
                        ...genRequest,
                        cuisine: e.target.value,
                      })
                    }
                    placeholder="e.g., Mediterranean, Asian"
                    className="rounded-xl"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Available Ingredients
                  </Label>
                  <Input
                    onChange={(e) =>
                      setGenRequest({
                        ...genRequest,
                        available_ingredients: e.target.value
                          .split(",")
                          .map((s) => s.trim())
                          .filter(Boolean),
                      })
                    }
                    placeholder="chicken, broccoli, rice"
                    className="rounded-xl"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full rounded-xl h-10"
                  disabled={generateMutation.isPending}
                >
                  <Sparkles
                    className={`h-4 w-4 mr-2 ${generateMutation.isPending ? "generating-pulse" : ""}`}
                  />
                  {generateMutation.isPending
                    ? "Generating..."
                    : "Generate Recipe"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground/40" />
        <Input
          placeholder="Search recipes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-11 h-11 rounded-xl border-border/50 bg-muted/20 font-light"
        />
      </div>

      {/* Recipe Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((recipe, i) => {
          const hasIngredients =
            recipe.ingredients_json && recipe.ingredients_json.length > 0;
          const hasSteps =
            recipe.steps_json && recipe.steps_json.length > 0;
          const nutrition = recipe.nutrition_per_serving_json;
          const isComplete = hasIngredients && hasSteps;

          return (
            <button
              key={recipe.id}
              className="meal-card-enter text-left rounded-2xl border border-border/40 p-5 transition-all duration-200 cursor-pointer group outline-none
                hover:border-border/70 hover:shadow-xl hover:shadow-black/15 hover:scale-[1.02] hover:-translate-y-0.5
                focus-visible:ring-2 focus-visible:ring-primary/50"
              style={{
                animationDelay: `${i * 0.04}s`,
                background: isComplete
                  ? "linear-gradient(145deg, rgb(16 185 129 / 0.06) 0%, transparent 40%)"
                  : "linear-gradient(145deg, rgb(245 158 11 / 0.05) 0%, transparent 40%)",
              }}
              onClick={() => setSelectedRecipe(recipe)}
            >
              {/* Title */}
              <h3
                className="text-base font-semibold leading-snug group-hover:text-foreground transition-colors line-clamp-2 mb-2"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                {recipe.title}
              </h3>

              {/* Description */}
              {recipe.description && (
                <p className="text-xs text-muted-foreground/60 font-light leading-relaxed line-clamp-2 mb-3">
                  {recipe.description}
                </p>
              )}

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {recipe.health_tags?.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="text-[9px] font-medium uppercase tracking-wider px-1.5 py-0.5 rounded-full"
                    style={{
                      color: "rgb(16 185 129 / 0.7)",
                      background: "rgb(16 185 129 / 0.08)",
                    }}
                  >
                    {tag}
                  </span>
                ))}
                {recipe.health_tags && recipe.health_tags.length > 3 && (
                  <span className="text-[9px] text-muted-foreground/40 px-1">
                    +{recipe.health_tags.length - 3}
                  </span>
                )}
              </div>

              {/* Footer info */}
              <div className="flex items-center justify-between pt-2 border-t border-border/20">
                <div className="flex items-center gap-3 text-[10px] text-muted-foreground/50">
                  {nutrition?.calories != null && (
                    <span className="flex items-center gap-1">
                      <Flame
                        className="h-3 w-3"
                        style={{ color: "rgb(244 114 69 / 0.6)" }}
                      />
                      <span className="tabular-nums font-medium">
                        {nutrition.calories}
                      </span>{" "}
                      cal
                    </span>
                  )}
                  {hasSteps && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {recipe.steps_json!.length} steps
                    </span>
                  )}
                  {hasIngredients && (
                    <span className="flex items-center gap-1">
                      <Leaf className="h-3 w-3" />
                      {recipe.ingredients_json!.length} items
                    </span>
                  )}
                </div>
                {!isComplete && (
                  <span
                    className="text-[9px] font-medium uppercase tracking-wider px-1.5 py-0.5 rounded-full"
                    style={{
                      color: "rgb(245 158 11 / 0.7)",
                      background: "rgb(245 158 11 / 0.1)",
                    }}
                  >
                    Bookmark
                  </span>
                )}
                {recipe.is_ai_generated && isComplete && (
                  <Sparkles
                    className="h-3 w-3"
                    style={{ color: "rgb(167 139 250 / 0.5)" }}
                  />
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Empty state */}
      {filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="relative mb-6">
            <div
              className="absolute inset-0 rounded-full blur-2xl opacity-20"
              style={{
                background:
                  "radial-gradient(circle, rgb(16 185 129 / 0.5), rgb(245 158 11 / 0.3))",
              }}
            />
            <ChefHat className="h-16 w-16 text-muted-foreground/30 relative" />
          </div>
          <h2
            className="text-2xl font-bold text-foreground/80 mb-2"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            {search ? "No matches" : "Start your collection"}
          </h2>
          <p className="text-sm text-muted-foreground/60 max-w-sm font-light leading-relaxed">
            {search
              ? `No recipes match "${search}"`
              : "Generate a recipe with AI, import from a URL, or save meals from your planner."}
          </p>
        </div>
      )}

      {/* Recipe Detail Modal */}
      {selectedRecipe && (
        <RecipeDetailModal
          recipe={selectedRecipe}
          open={!!selectedRecipe}
          onOpenChange={(open) => {
            if (!open) setSelectedRecipe(null);
          }}
          onAddToShoppingList={() =>
            addToShoppingMutation.mutate(selectedRecipe.id)
          }
          onGenerateFull={() =>
            generateFullMutation.mutate({
              health_focus: "DASH diet, low sodium",
              available_ingredients: [selectedRecipe.title],
            })
          }
          isGenerating={generateFullMutation.isPending}
        />
      )}
    </div>
  );
}
