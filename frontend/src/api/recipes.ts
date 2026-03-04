import api from "./client";
import type { Recipe, RecipeCreate, RecipeGenerateRequest } from "@/types";

export const recipesApi = {
  list: () => api.get<Recipe[]>("/recipes/").then((r) => r.data),

  create: (data: RecipeCreate) =>
    api.post<Recipe>("/recipes/", data).then((r) => r.data),

  get: (id: string) => api.get<Recipe>(`/recipes/${id}`).then((r) => r.data),

  generate: (data: RecipeGenerateRequest) =>
    api.post<Recipe>("/recipes/generate", data).then((r) => r.data),

  importUrl: (url: string) =>
    api.post<Recipe>("/recipes/import-url", { url }).then((r) => r.data),

  addToShoppingList: (id: string) =>
    api.post<{ message: string }>(`/recipes/${id}/add-to-shopping-list`).then((r) => r.data),
};
