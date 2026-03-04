import { z } from "zod";

export const pantryItemSchema = z.object({
  name: z.string().min(1, "Name is required"),
  category: z.string().optional(),
  quantity: z.coerce.number().min(0, "Quantity must be positive").default(1),
  unit: z.string().optional(),
  purchase_date: z.string().optional(),
  estimated_expiry: z.string().optional(),
  low_stock_threshold: z.coerce.number().min(0).optional(),
});

export type PantryItemFormData = z.infer<typeof pantryItemSchema>;

export const foodLogSchema = z.object({
  meal_type: z.enum(["breakfast", "lunch", "dinner", "snack"]),
  food_name: z.string().min(1, "Food name is required"),
  quantity: z.coerce.number().min(0).optional(),
  unit: z.string().optional(),
  calories: z.coerce.number().min(0).optional(),
  protein_g: z.coerce.number().min(0).optional(),
  carbs_g: z.coerce.number().min(0).optional(),
  fat_g: z.coerce.number().min(0).optional(),
  fiber_g: z.coerce.number().min(0).optional(),
  sodium_mg: z.coerce.number().min(0).optional(),
});

export type FoodLogFormData = z.infer<typeof foodLogSchema>;

export const bpLogSchema = z.object({
  systolic: z.coerce
    .number()
    .min(60, "Systolic must be at least 60")
    .max(300, "Systolic must be at most 300"),
  diastolic: z.coerce
    .number()
    .min(30, "Diastolic must be at least 30")
    .max(200, "Diastolic must be at most 200"),
  pulse: z.coerce.number().min(30).max(250).optional(),
  notes: z.string().optional(),
});

export type BPLogFormData = z.infer<typeof bpLogSchema>;

export const weightLogSchema = z.object({
  weight_lbs: z.coerce
    .number()
    .min(50, "Weight must be at least 50 lbs")
    .max(1000, "Weight must be at most 1000 lbs"),
  notes: z.string().optional(),
});

export type WeightLogFormData = z.infer<typeof weightLogSchema>;

export const cholesterolLogSchema = z.object({
  total_mg_dl: z.coerce.number().min(50).max(500),
  ldl: z.coerce.number().min(0).max(400).optional(),
  hdl: z.coerce.number().min(0).max(200).optional(),
  triglycerides: z.coerce.number().min(0).max(1000).optional(),
  notes: z.string().optional(),
});

export type CholesterolLogFormData = z.infer<typeof cholesterolLogSchema>;

export const settingsSchema = z.object({
  name: z.string().min(1, "Name is required"),
  health_goals_json: z
    .object({
      dietary_preferences: z.array(z.string()).optional(),
      health_focus: z.string().optional(),
      calorie_target: z.coerce.number().min(500).max(10000).optional(),
    })
    .optional(),
});

export type SettingsFormData = z.infer<typeof settingsSchema>;
