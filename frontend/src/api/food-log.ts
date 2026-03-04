import api from "./client";
import type { FoodLog, FoodLogCreate, DailySummary } from "@/types";

export const foodLogApi = {
  list: (date?: string) =>
    api.get<FoodLog[]>("/food-log/", { params: date ? { date } : {} }).then((r) => r.data),

  create: (data: FoodLogCreate) =>
    api.post<FoodLog>("/food-log/", data).then((r) => r.data),

  dailySummary: (date: string) =>
    api.get<DailySummary>("/food-log/daily-summary", { params: { date } }).then((r) => r.data),
};
