import api from "./client";
import type { MealPlan, MealPlanCreate, MealPlanSuggestRequest } from "@/types";

export const mealPlansApi = {
  list: () => api.get<MealPlan[]>("/meal-plans/").then((r) => r.data),

  create: (data: MealPlanCreate) =>
    api.post<MealPlan>("/meal-plans/", data).then((r) => r.data),

  suggest: (data: MealPlanSuggestRequest) =>
    api.post<MealPlan>("/meal-plans/suggest", data).then((r) => r.data),
};
