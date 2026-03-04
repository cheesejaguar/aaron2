import api from "./client";
import type { PantryItem, PantryItemCreate, PantryItemUpdate } from "@/types";

export const pantryApi = {
  list: () => api.get<PantryItem[]>("/pantry/").then((r) => r.data),

  create: (data: PantryItemCreate) =>
    api.post<PantryItem>("/pantry/", data).then((r) => r.data),

  update: (id: string, data: PantryItemUpdate) =>
    api.put<PantryItem>(`/pantry/${id}`, data).then((r) => r.data),

  delete: (id: string) => api.delete(`/pantry/${id}`).then((r) => r.data),

  consume: (id: string, quantity: number) =>
    api.post<PantryItem>(`/pantry/${id}/consume`, { quantity }).then((r) => r.data),

  parseReceipt: (rawText: string) =>
    api
      .post<{ items: unknown[]; pantry_items_created: number }>("/receipts/parse", {
        raw_text: rawText,
      })
      .then((r) => r.data),
};
