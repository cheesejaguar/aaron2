// Auth
export interface User {
  id: string;
  email: string;
  name: string;
  health_goals_json?: Record<string, unknown> | null;
}

// Pantry
export interface PantryItem {
  id: string;
  name: string;
  category?: string | null;
  quantity: number;
  unit?: string | null;
  nutrition_json?: Record<string, unknown> | null;
  purchase_date?: string | null;
  estimated_expiry?: string | null;
  low_stock_threshold?: number | null;
}

export interface PantryItemCreate {
  name: string;
  category?: string | null;
  quantity?: number;
  unit?: string | null;
  purchase_date?: string | null;
  estimated_expiry?: string | null;
  low_stock_threshold?: number | null;
}

export interface PantryItemUpdate {
  name?: string;
  category?: string;
  quantity?: number;
  unit?: string;
}

// Recipe
export interface Recipe {
  id: string;
  title: string;
  description?: string | null;
  ingredients_json?: { name: string; quantity: string; unit: string }[] | null;
  steps_json?: string[] | null;
  nutrition_per_serving_json?: Record<string, number> | null;
  health_tags?: string[] | null;
  source_url?: string | null;
  is_ai_generated: boolean;
}

export interface RecipeCreate {
  title: string;
  description?: string;
  ingredients_json?: { name: string; quantity: string; unit: string }[];
  steps_json?: string[];
  health_tags?: string[];
}

export interface RecipeGenerateRequest {
  dietary_preferences?: string[];
  available_ingredients?: string[];
  health_focus?: string;
  cuisine?: string;
}

// Meal Plan
export interface MealPlanEntry {
  id: string;
  day_of_week: number;
  meal_type: string;
  recipe_id?: string | null;
  custom_meal_json?: Record<string, unknown> | null;
}

export interface MealPlan {
  id: string;
  week_start_date: string;
  entries: MealPlanEntry[];
}

export interface MealPlanCreate {
  week_start_date: string;
  entries?: { day_of_week: number; meal_type: string; recipe_id?: string }[];
}

export interface MealPlanSuggestRequest {
  week_start_date: string;
  dietary_preferences?: string[];
  health_focus?: string;
}

// Shopping List
export interface ShoppingListItem {
  id: string;
  name: string;
  quantity?: number | null;
  unit?: string | null;
  category?: string | null;
  is_checked: boolean;
  is_ai_suggested: boolean;
  health_priority_score?: number | null;
}

export interface ShoppingList {
  id: string;
  name: string;
  status: string;
  items: ShoppingListItem[];
}

export interface ShoppingListCreate {
  name: string;
  items?: { name: string; quantity?: number; unit?: string; category?: string }[];
}

// Food Log
export interface FoodLog {
  id: string;
  logged_at: string;
  meal_type: string;
  food_name: string;
  quantity?: number | null;
  unit?: string | null;
  calories?: number | null;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  fiber_g?: number | null;
  sodium_mg?: number | null;
  potassium_mg?: number | null;
  cholesterol_mg?: number | null;
}

export interface FoodLogCreate {
  meal_type: string;
  food_name: string;
  quantity?: number;
  unit?: string;
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
  sodium_mg?: number;
  potassium_mg?: number;
  cholesterol_mg?: number;
}

export interface DailySummary {
  date: string;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  total_fiber_g: number;
  total_sodium_mg: number;
  total_potassium_mg: number;
  total_cholesterol_mg: number;
  meal_count: number;
}

// Health
export interface BPLog {
  id: string;
  systolic: number;
  diastolic: number;
  pulse?: number | null;
  notes?: string | null;
  measured_at: string;
}

export interface BPLogCreate {
  systolic: number;
  diastolic: number;
  pulse?: number;
  notes?: string;
}

export interface WeightLog {
  id: string;
  weight_lbs: number;
  notes?: string | null;
  measured_at: string;
}

export interface WeightLogCreate {
  weight_lbs: number;
  notes?: string;
}

export interface CholesterolLog {
  id: string;
  total_mg_dl: number;
  ldl?: number | null;
  hdl?: number | null;
  triglycerides?: number | null;
  notes?: string | null;
  measured_at: string;
}

export interface CholesterolLogCreate {
  total_mg_dl: number;
  ldl?: number;
  hdl?: number;
  triglycerides?: number;
  notes?: string;
}

export interface DashboardData {
  latest_bp?: BPLog | null;
  latest_weight?: WeightLog | null;
  latest_cholesterol?: CholesterolLog | null;
  bp_status?: string | null;
  weight_trend: WeightLog[];
  bp_trend: BPLog[];
}

// AI Coach
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  reply: string;
  conversation_id: string;
}

export interface InsightsResponse {
  insights: {
    title: string;
    description: string;
    category: string;
    priority: string;
  }[];
}
