import api from "./client";
import type { ChatRequest, ChatResponse, InsightsResponse } from "@/types";

export const coachApi = {
  chat: (data: ChatRequest) =>
    api.post<ChatResponse>("/coach/chat", data).then((r) => r.data),

  insights: () =>
    api.get<InsightsResponse>("/coach/insights").then((r) => r.data),

  dailyNutritionSummary: (date: string) =>
    api.get<InsightsResponse>("/coach/insights", { params: { date } }).then((r) => r.data),
};
