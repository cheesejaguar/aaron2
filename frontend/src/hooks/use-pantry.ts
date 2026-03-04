import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { pantryApi } from "@/api/pantry";
import type { PantryItemCreate, PantryItemUpdate } from "@/types";

export function usePantryItems() {
  return useQuery({
    queryKey: ["pantry"],
    queryFn: pantryApi.list,
  });
}

export function useCreatePantryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PantryItemCreate) => pantryApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
      toast.success("Item added to pantry");
    },
    onError: () => toast.error("Failed to add item"),
  });
}

export function useUpdatePantryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PantryItemUpdate }) =>
      pantryApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
    },
  });
}

export function useDeletePantryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: pantryApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
      toast.success("Item removed");
    },
  });
}

export function useConsumePantryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, quantity }: { id: string; quantity: number }) =>
      pantryApi.consume(id, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
    },
  });
}
