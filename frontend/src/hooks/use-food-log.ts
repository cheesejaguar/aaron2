import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { foodLogApi } from "@/api/food-log";
import type { FoodLogCreate } from "@/types";

export function useFoodLogs(date?: string) {
  return useQuery({
    queryKey: ["food-log", date],
    queryFn: () => foodLogApi.list(date),
  });
}

export function useDailySummary(date: string) {
  return useQuery({
    queryKey: ["food-log", "daily-summary", date],
    queryFn: () => foodLogApi.dailySummary(date),
  });
}

export function useCreateFoodLog() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: FoodLogCreate) => foodLogApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["food-log"] });
      toast.success("Food logged");
    },
    onError: () => toast.error("Failed to log food"),
  });
}
