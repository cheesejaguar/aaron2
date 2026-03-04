import api from "./client";
import type { ShoppingList, ShoppingListCreate } from "@/types";

export const shoppingListsApi = {
  list: () => api.get<ShoppingList[]>("/shopping-lists/").then((r) => r.data),

  create: (data: ShoppingListCreate) =>
    api.post<ShoppingList>("/shopping-lists/", data).then((r) => r.data),

  replenish: (id: string) =>
    api.post<ShoppingList>(`/shopping-lists/${id}/replenish`).then((r) => r.data),

  getAmazonCartUrl: (id: string) =>
    api.get<{ url: string }>(`/shopping-lists/${id}/amazon-cart-url`).then((r) => r.data),
};
