import api from "./client";
import type { User } from "@/types";

export const authApi = {
  getMe: () => api.get<User>("/auth/me").then((r) => r.data),

  updateSettings: (data: { name?: string; health_goals_json?: Record<string, unknown> }) =>
    api.patch<User>("/auth/settings", data).then((r) => r.data),
};
